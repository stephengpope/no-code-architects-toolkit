import os
import ffmpeg
import logging
import requests
import subprocess
import whisper
from datetime import timedelta
import srt
import re
from services.file_management import download_file

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set appropriate logging level
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Storage path
STORAGE_PATH = "/tmp/"

def rgb_to_ass_color(rgb_color):
    """Convert RGB color code to ASS color format (&HAABBGGRR)."""
    if isinstance(rgb_color, str):
        rgb_color = rgb_color.lstrip('#')
        if len(rgb_color) == 6:
            r = int(rgb_color[0:2], 16)
            g = int(rgb_color[2:4], 16)
            b = int(rgb_color[4:6], 16)
            # ASS format is &HAABBGGRR, with AA (alpha) set to 00 (opaque)
            return f"&H00{b:02X}{g:02X}{r:02X}"
    # Default to white color
    return "&H00FFFFFF"

def generate_transcription(video_path, language='auto'):
    """Generate transcription with word-level timestamps from video file."""
    try:
        model = whisper.load_model("base")
        transcription_options = {
            'word_timestamps': True,
            'verbose': True,
        }
        if language != 'auto':
            transcription_options['language'] = language
        result = model.transcribe(video_path, **transcription_options)
        return result
    except Exception as e:
        logger.error(f"Error in transcription: {str(e)}")
        raise

def get_video_resolution(video_path):
    """Get the resolution of the video using ffprobe."""
    try:
        probe = ffmpeg.probe(video_path)
        video_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
        if video_streams:
            width = int(video_streams[0]['width'])
            height = int(video_streams[0]['height'])
            return width, height
        else:
            return 384, 288
    except Exception as e:
        logger.error(f"Error getting video resolution: {str(e)}")
        return 384, 288

def get_available_fonts():
    """Get a list of available fonts on the system."""
    try:
        import matplotlib.font_manager as fm
    except ImportError:
        logger.error("matplotlib is not installed. Please install it using 'pip install matplotlib'")
        return []

    font_list = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    font_names = set()
    for font in font_list:
        try:
            font_prop = fm.FontProperties(fname=font)
            font_name = font_prop.get_name()
            font_names.add(font_name)
        except Exception:
            continue
    return list(font_names)

def format_ass_time(seconds):
    """Format seconds into ASS time format (H:MM:SS.cs) with centiseconds."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centiseconds = int(round((seconds - int(seconds)) * 100))
    return f"{hours}:{minutes:02}:{secs:02}.{centiseconds:02}"

def create_style_line(style_options, video_resolution, is_karaoke=False):
    """
    Create the style line for ASS subtitles based on style_options.
    If is_karaoke=True, expect a format that includes SecondaryColour.
    """
    # Handle font availability
    font_family = style_options.get('font_family', 'Arial')
    available_fonts = get_available_fonts()
    if font_family not in available_fonts:
        logger.warning(f"Font '{font_family}' not found. Available fonts: {', '.join(available_fonts)}")
        return {'error': f"Font '{font_family}' not available.", 'available_fonts': available_fonts}

    # Convert colors from RGB to ASS
    line_color = rgb_to_ass_color(style_options.get('line_color', '#FFFFFF'))    # Primary
    word_color = rgb_to_ass_color(style_options.get('word_color', '#FFFF00'))    # Active word (karaoke)
    outline_color = rgb_to_ass_color(style_options.get('outline_color', '#000000'))
    box_color = rgb_to_ass_color(style_options.get('box_color', '#000000'))
    highlight_color = rgb_to_ass_color(style_options.get('highlight_color', '#FF0000'))
    shadow_color = rgb_to_ass_color(style_options.get('shadow_color', '#000000'))
    # Note: highlight_color and shadow_color usage is limited. shadow_color not directly supported by ASS.

    font_size = style_options.get('font_size', int(video_resolution[1] * 0.05))
    bold = '1' if style_options.get('bold', False) else '0'
    italic = '1' if style_options.get('italic', False) else '0'
    underline = '1' if style_options.get('underline', False) else '0'
    strikeout = '1' if style_options.get('strikeout', False) else '0'
    scale_x = style_options.get('scale_x', '100')
    scale_y = style_options.get('scale_y', '100')
    spacing = style_options.get('spacing', '0')
    angle = style_options.get('angle', '0')
    border_style = style_options.get('border_style', '1')
    outline_width = style_options.get('outline_width', '2')
    shadow_offset = style_options.get('shadow_offset', '0')

    # Alignment mapping
    position_mapping = {
        'top-left': '7',
        'top-center': '8',
        'top-right': '9',
        'center-left': '4',
        'center-center': '5',
        'center-right': '6',
        'bottom-left': '1',
        'bottom-center': '2',
        'bottom-right': '3',
    }
    alignment = position_mapping.get(style_options.get('position', 'bottom-center'), '2')

    margin_l = style_options.get('margin_l', '20')
    margin_r = style_options.get('margin_r', '20')
    margin_v = style_options.get('margin_v', '20')

    if is_karaoke:
        # Karaoke format includes SecondaryColour
        # Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
        style_line = "Style: Default"
        style_line += f",{font_family}"
        style_line += f",{font_size}"
        style_line += f",{line_color}"    # PrimaryColour
        style_line += f",{word_color}"    # SecondaryColour
        style_line += f",{outline_color}" # OutlineColour
        style_line += f",{box_color}"     # BackColour
        style_line += f",{bold}"
        style_line += f",{italic}"
        style_line += f",{underline}"
        style_line += f",{strikeout}"
        style_line += f",{scale_x}"
        style_line += f",{scale_y}"
        style_line += f",{spacing}"
        style_line += f",{angle}"
        style_line += f",{border_style}"
        style_line += f",{outline_width}"
        style_line += f",{shadow_offset}"
        style_line += f",{alignment}"
        style_line += f",{margin_l}"
        style_line += f",{margin_r}"
        style_line += f",{margin_v}"
        style_line += ",0"  # Encoding
    else:
        # Classic format
        # Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
        style_line = "Style: Default"
        style_line += f",{font_family}"
        style_line += f",{font_size}"
        style_line += f",{line_color}"    # PrimaryColour
        style_line += f",{outline_color}" # OutlineColour
        style_line += f",{box_color}"     # BackColour
        style_line += f",{bold}"
        style_line += f",{italic}"
        style_line += f",{underline}"
        style_line += f",{strikeout}"
        style_line += f",{scale_x}"
        style_line += f",{scale_y}"
        style_line += f",{spacing}"
        style_line += f",{angle}"
        style_line += f",{border_style}"
        style_line += f",{outline_width}"
        style_line += f",{shadow_offset}"
        style_line += f",{alignment}"
        style_line += f",{margin_l}"
        style_line += f",{margin_r}"
        style_line += f",{margin_v}"
        style_line += ",0"  # Encoding

    return style_line

def process_subtitle_text(text, style_options, replace_dict, all_caps, max_words_per_line):
    """Apply text transformations based on style options."""
    # Apply 'replace' option
    for old_word, new_word in replace_dict.items():
        text = re.sub(re.escape(old_word), new_word, text, flags=re.IGNORECASE)
    # Apply 'all_caps' option
    if all_caps:
        text = text.upper()
    # Apply 'max_words_per_line'
    if max_words_per_line > 0:
        words_list = text.split()
        lines = [' '.join(words_list[i:i+max_words_per_line]) for i in range(0, len(words_list), max_words_per_line)]
        text = '\\N'.join(lines)
    return text

def srt_to_ass_classic(transcription_result, options=None, video_resolution=(384, 288)):
    """Convert transcription result to ASS format (classic style)."""
    if options is None:
        options = []
    style_options = {opt["option"].replace('-', '_'): opt["value"] for opt in options}

    # Prepare ASS header
    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_resolution[0]}
PlayResY: {video_resolution[1]}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""

    style_line = create_style_line(style_options, video_resolution, is_karaoke=False)
    if isinstance(style_line, dict) and 'error' in style_line:
        return style_line

    ass_content = ass_header + style_line + "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    
    replace_dict = style_options.get('replace', {})
    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)
    x = style_options.get('x', None)
    y = style_options.get('y', None)
    position_tag = f"{{\\pos({x},{y})}}" if x is not None and y is not None else ""

    for segment in transcription_result['segments']:
        start_ass = format_ass_time(segment['start'])
        end_ass = format_ass_time(segment['end'])
        
        text = segment['text'].strip().replace('\n', ' ')
        # Apply 'replace' and 'all_caps', 'max_words_per_line'
        text = process_subtitle_text(text, style_options, replace_dict, all_caps, max_words_per_line)
        
        ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{position_tag}{text}\n"

    return ass_content

def srt_to_ass_karaoke(transcription_result, options=None, video_resolution=(384, 288)):
    """Convert transcription result to ASS format with karaoke effects."""
    if options is None:
        options = []
    style_options = {opt["option"].replace('-', '_'): opt["value"] for opt in options}

    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_resolution[0]}
PlayResY: {video_resolution[1]}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""

    style_line = create_style_line(style_options, video_resolution, is_karaoke=True)
    if isinstance(style_line, dict) and 'error' in style_line:
        return style_line

    ass_content = ass_header + style_line + "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"

    replace_dict = style_options.get('replace', {})
    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)
    x = style_options.get('x', None)
    y = style_options.get('y', None)
    position_tag = f"{{\\pos({x},{y})}}" if x is not None and y is not None else ""

    # Retrieve highlight_color and box_color for highlighting active words
    highlight_color = rgb_to_ass_color(style_options.get('highlight_color', '#FF0000'))
    box_color = rgb_to_ass_color(style_options.get('box_color', '#000000'))

    for segment in transcription_result['segments']:
        start_ass = format_ass_time(segment['start'])
        end_ass = format_ass_time(segment['end'])
        
        words = segment.get('words', [])
        if not words:
            # No word-level data, fallback to classic style approach
            text = segment['text'].strip().replace('\n', ' ')
            # Apply 'replace' and 'all_caps'
            text = process_subtitle_text(text, style_options, replace_dict, all_caps, max_words_per_line)
            ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{position_tag}{text}\n"
            continue

        # Build karaoke line with highlighting active words
        karaoke_text = ""
        word_count = 0
        for word_info in words:
            word = word_info['word'].strip().replace('\n', ' ')
            if not word:
                continue
            # Apply 'replace' option
            for old_word, new_word in replace_dict.items():
                word = word.replace(old_word, new_word)
            # Apply 'all_caps' option
            if all_caps:
                word = word.upper()

            duration_cs = int(round((word_info['end'] - word_info['start']) * 100))
            # Insert highlight tags for the active word
            # \4c sets the border color (not directly background), so we use \c for text color as a workaround
            # For actual background highlighting, ASS lacks direct support per word
            # Alternatively, use \3c for primary outline color or \c for text color changes
            # Here, we'll change the text color of the active word
            highlighted_word = f"{{\\c{highlight_color}\\k{duration_cs}}}{word}{{\\c}} "  # Reset color after word

            karaoke_text += highlighted_word
            word_count += 1

            if max_words_per_line > 0 and word_count >= max_words_per_line:
                karaoke_text = karaoke_text.strip()
                ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{position_tag}{karaoke_text}\n"
                karaoke_text = ""
                word_count = 0

        if karaoke_text:
            karaoke_text = karaoke_text.strip()
            ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{position_tag}{karaoke_text}\n"

    return ass_content

def srt_to_ass_highlight(transcription_result, options=None, video_resolution=(384, 288)):
    """Convert transcription result to ASS format with active word highlighted with background."""
    # Placeholder for highlight style implementation if needed
    # Due to ASS limitations, this is not straightforward
    # Returning an error message for now
    return {"error": "Highlight style not implemented yet due to ASS limitations."}

def srt_to_ass_underline(transcription_result, options=None, video_resolution=(384, 288)):
    """Convert transcription result to ASS format with active word underlined."""
    # Placeholder for underline style implementation if needed
    # Could use override tags to underline active words
    # Implementing similar to karaoke but adding underline
    if options is None:
        options = []
    style_options = {opt["option"].replace('-', '_'): opt["value"] for opt in options}

    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_resolution[0]}
PlayResY: {video_resolution[1]}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""

    style_line = create_style_line(style_options, video_resolution, is_karaoke=False)
    if isinstance(style_line, dict) and 'error' in style_line:
        return style_line

    ass_content = ass_header + style_line + "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"

    replace_dict = style_options.get('replace', {})
    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)
    x = style_options.get('x', None)
    y = style_options.get('y', None)
    position_tag = f"{{\\pos({x},{y})}}" if x is not None and y is not None else ""

    for segment in transcription_result['segments']:
        start_ass = format_ass_time(segment['start'])
        end_ass = format_ass_time(segment['end'])
        
        words = segment.get('words', [])
        if not words:
            # Fallback to classic style
            text = segment['text'].strip().replace('\n', ' ')
            text = process_subtitle_text(text, style_options, replace_dict, all_caps, max_words_per_line)
            ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{position_tag}{text}\n"
            continue

        # Build underlined active words
        dialogue_text = ""
        word_count = 0
        for word_info in words:
            word = word_info['word'].strip().replace('\n', ' ')
            if not word:
                continue
            # Apply 'replace' option
            for old_word, new_word in replace_dict.items():
                word = word.replace(old_word, new_word)
            # Apply 'all_caps' option
            if all_caps:
                word = word.upper()

            duration_cs = int(round((word_info['end'] - word_info['start']) * 100))
            # Apply underline to active word using \u1 and reset with \u0
            underlined_word = f"{{\\u1\\k{duration_cs}}}{word}{{\\u0}} "

            dialogue_text += underlined_word
            word_count += 1

            if max_words_per_line > 0 and word_count >= max_words_per_line:
                dialogue_text = dialogue_text.strip()
                ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{position_tag}{dialogue_text}\n"
                dialogue_text = ""
                word_count = 0

        if dialogue_text:
            dialogue_text = dialogue_text.strip()
            ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{position_tag}{dialogue_text}\n"

    return ass_content

def srt_to_ass_word_by_word(transcription_result, options=None, video_resolution=(384, 288)):
    """Convert transcription result to ASS format with word-by-word display."""
    # Placeholder for word-by-word style implementation if needed
    # This would involve creating separate dialogue events for each word, replacing the previous one
    # Not implemented due to complexity and potential performance issues
    return {"error": "Word-by-word style not implemented yet."}

def process_captioning_v1(video_url, caption_srt, caption_ass, options, job_id, language='auto'):
    """Enhanced v1 captioning process with transcription fallback and multiple styles."""
    try:
        # Download video
        video_path = download_file(video_url, STORAGE_PATH)
        logger.info(f"Job {job_id}: Video downloaded to {video_path}")

        # Get video resolution
        video_resolution = get_video_resolution(video_path)
        logger.info(f"Job {job_id}: Video resolution detected as {video_resolution[0]}x{video_resolution[1]}")

        # Convert options array to dictionary, mapping hyphenated names to underscores
        style_options = {}
        for opt in options:
            option_name = opt["option"].replace('-', '_')
            style_options[option_name] = opt["value"]

        # Determine subtitle content and type
        if caption_ass:
            subtitle_content = caption_ass
            subtitle_type = 'ass'
        elif caption_srt:
            subtitle_content = caption_srt
            subtitle_type = 'srt'
        else:
            # Generate transcription with word-level timestamps
            logger.info(f"Job {job_id}: No subtitles provided, generating transcription with word-level timestamps")
            transcription_result = generate_transcription(video_path, language=language)
            # Determine the style to use
            style_type = style_options.get('style', 'classic').lower()
            if style_type == 'classic':
                subtitle_content = srt_to_ass_classic(transcription_result, options, video_resolution=video_resolution)
            elif style_type == 'karaoke':
                subtitle_content = srt_to_ass_karaoke(transcription_result, options, video_resolution=video_resolution)
            elif style_type == 'highlight':
                subtitle_content = srt_to_ass_highlight(transcription_result, options, video_resolution=video_resolution)
            elif style_type == 'underline':
                subtitle_content = srt_to_ass_underline(transcription_result, options, video_resolution=video_resolution)
            elif style_type == 'word-by-word':
                subtitle_content = srt_to_ass_word_by_word(transcription_result, options, video_resolution=video_resolution)
            else:
                # Default to classic if unknown style
                logger.warning(f"Unknown style '{style_type}'. Defaulting to 'classic'.")
                subtitle_content = srt_to_ass_classic(transcription_result, options, video_resolution=video_resolution)
            subtitle_type = 'ass'

        # If subtitle_content is a dict with 'error', return it directly
        if isinstance(subtitle_content, dict) and 'error' in subtitle_content:
            logger.error(f"Job {job_id}: {subtitle_content['error']}")
            return subtitle_content

        # Save subtitle content to file
        subtitle_filename = f"{job_id}.{subtitle_type}"
        subtitle_path = os.path.join(STORAGE_PATH, subtitle_filename)
        with open(subtitle_path, 'w', encoding='utf-8') as f:
            f.write(subtitle_content)
        logger.info(f"Job {job_id}: Subtitle file saved to {subtitle_path}")

        # Prepare output path
        output_filename = f"{job_id}_captioned.mp4"
        output_path = os.path.join(STORAGE_PATH, output_filename)

        # Process video with subtitles using FFmpeg
        try:
            # Use FFmpeg's subtitles filter with ASS file
            ffmpeg.input(video_path).output(
                output_path,
                vf=f"subtitles='{subtitle_path}'",
                acodec='copy'
            ).run(overwrite_output=True)
            logger.info(f"Job {job_id}: FFmpeg processing completed. Output saved to {output_path}")
        except ffmpeg.Error as e:
            stderr_output = e.stderr.decode('utf8') if e.stderr else 'Unknown error'
            logger.error(f"Job {job_id}: FFmpeg error: {stderr_output}")
            raise

        # Optionally, clean up temporary files
        # os.remove(video_path)
        # os.remove(subtitle_path)

        return output_path

    except Exception as e:
        logger.error(f"Job {job_id}: Error in process_captioning_v1: {str(e)}")
        return {"error": str(e)}
