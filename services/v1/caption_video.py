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
        # Enable word-level timestamps
        transcription_options = {
            'word_timestamps': True,
            'verbose': True,
        }
        if language != 'auto':
            transcription_options['language'] = language
        result = model.transcribe(video_path, **transcription_options)
        return result  # Return the full result including word timings
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
            return 384, 288  # Default values if resolution can't be determined
    except Exception as e:
        logger.error(f"Error getting video resolution: {str(e)}")
        return 384, 288

def get_available_fonts():
    """Get a list of available fonts on the system."""
    import matplotlib.font_manager as fm
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

def srt_to_ass_karaoke(transcription_result, options=None, video_resolution=(384, 288)):
    """Convert transcription result to ASS format with karaoke effects."""
    if options is None:
        options = []
    
    # Helper function to format time
    def format_ass_time(seconds):
        """Format seconds for ASS time (H:MM:SS.cs) with centiseconds."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centiseconds = int((seconds - int(seconds)) * 100)
        return f"{hours}:{minutes:02}:{secs:02}.{centiseconds:02}"
    
    # Generate ASS header with style
    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_resolution[0]}
PlayResY: {video_resolution[1]}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""
    # Convert options array to dictionary, mapping hyphenated names to underscores
    style_options = {}
    for opt in options:
        option_name = opt["option"].replace('-', '_')
        style_options[option_name] = opt["value"]
    
    # Handle font availability
    font_family = style_options.get('font_family', 'Arial')
    available_fonts = get_available_fonts()
    if font_family not in available_fonts:
        logger.warning(f"Font '{font_family}' not found. Available fonts are: {', '.join(available_fonts)}")
        return {'error': f"Font '{font_family}' not available.", 'available_fonts': available_fonts}
    
    # Convert colors from RGB to ASS color format
    line_color = rgb_to_ass_color(style_options.get('line_color', '#888888'))  # Inactive words
    word_color = rgb_to_ass_color(style_options.get('word_color', '#FFFFFF'))  # Active word
    outline_color = rgb_to_ass_color(style_options.get('outline_color', '#000000'))
    box_color = rgb_to_ass_color(style_options.get('box_color', '#000000'))
    
    # Style parameters
    font_size = style_options.get('font_size', int(video_resolution[1] * 0.05))  # Defaults to 5% of video height
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
    # Map position to alignment number
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
    
    # Generate style line
    style_line = "Style: Default"
    style_line += f",{font_family}"  # Fontname
    style_line += f",{font_size}"  # Fontsize
    style_line += f",{line_color}"  # PrimaryColour
    style_line += f",{word_color}"  # SecondaryColour
    style_line += f",{outline_color}"  # OutlineColour
    style_line += f",{box_color}"  # BackColour
    style_line += f",{bold}"  # Bold
    style_line += f",{italic}"  # Italic
    style_line += f",{underline}"  # Underline
    style_line += f",{strikeout}"  # StrikeOut
    style_line += f",{scale_x}"  # ScaleX
    style_line += f",{scale_y}"  # ScaleY
    style_line += f",{spacing}"  # Spacing
    style_line += f",{angle}"  # Angle
    style_line += f",{border_style}"  # BorderStyle
    style_line += f",{outline_width}"  # Outline
    style_line += f",{shadow_offset}"  # Shadow
    style_line += f",{alignment}"  # Alignment
    style_line += f",{margin_l}"  # MarginL
    style_line += f",{margin_r}"  # MarginR
    style_line += f",{margin_v}"  # MarginV
    style_line += ",0"  # Encoding set to 0 (ANSI)
    
    ass_content = ass_header + style_line + "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    
    # Process 'replace' option
    replace_dict = style_options.get('replace', {})
    
    # Process each segment
    max_words_per_line = int(style_options.get('max_words_per_line', 0))  # 0 means no limit
    all_caps = style_options.get('all_caps', False)
    x = style_options.get('x', None)
    y = style_options.get('y', None)
    position_tag = ""
    if x is not None and y is not None:
        position_tag = f"{{\\pos({x},{y})}}"
    
    for segment in transcription_result['segments']:
        start_time = segment['start']
        end_time = segment['end']
        start_ass = format_ass_time(start_time)
        end_ass = format_ass_time(end_time)
        
        words = segment.get('words', [])
        if not words:
            # Fallback if word-level timestamps are not available
            text = segment['text'].strip().replace('\n', '\\N')
            # Apply 'replace' option
            for old_word, new_word in replace_dict.items():
                text = text.replace(old_word, new_word)
            # Apply 'all_caps' option
            if all_caps:
                text = text.upper()
            # Apply 'max_words_per_line'
            if max_words_per_line > 0:
                words_list = text.split()
                lines = [' '.join(words_list[i:i+max_words_per_line]) for i in range(0, len(words_list), max_words_per_line)]
                text = '\\N'.join(lines)
            ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{position_tag}{text}\n"
            continue
        
        # Build the karaoke text
        karaoke_text = ""
        word_count = 0
        for word_info in words:
            word = word_info['word'].strip().replace('\n', '\\N')
            if not word:
                continue
            # Apply 'replace' option
            for old_word, new_word in replace_dict.items():
                word = word.replace(old_word, new_word)
            # Apply 'all_caps' option
            if all_caps:
                word = word.upper()
            # Calculate duration in centiseconds
            duration_cs = int((word_info['end'] - word_info['start']) * 100)
            karaoke_text += f"{{\\k{duration_cs}}}{word} "
            word_count += 1
            # Handle max_words_per_line
            if max_words_per_line > 0 and word_count >= max_words_per_line:
                karaoke_text = karaoke_text.strip()
                ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{position_tag}{karaoke_text}\n"
                karaoke_text = ""
                word_count = 0
        if karaoke_text:
            karaoke_text = karaoke_text.strip()
            ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{position_tag}{karaoke_text}\n"
    
    return ass_content

def process_captioning_v1(video_url, caption_srt, caption_ass, options, job_id, language='auto'):
    """Enhanced v1 captioning process with transcription fallback and karaoke effects."""
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
            style_type = style_options.get('style', 'classic')
            if style_type == 'classic':
                # Implement srt_to_ass function similarly, adjusted for API parameters
                subtitle_content = srt_to_ass_karaoke(transcription_result, options, video_resolution=video_resolution)
            elif style_type == 'classic-progressive':
                subtitle_content = srt_to_ass_karaoke(transcription_result, options, video_resolution=video_resolution)
            else:
                # Default to classic
                subtitle_content = srt_to_ass_karaoke(transcription_result, options, video_resolution=video_resolution)
            subtitle_type = 'ass'
    
        # Save subtitle content to file
        subtitle_path = os.path.join(STORAGE_PATH, f"{job_id}.{subtitle_type}")
        with open(subtitle_path, 'w', encoding='utf-8') as f:
            f.write(subtitle_content)
    
        # Prepare output path
        output_path = os.path.join(STORAGE_PATH, f"{job_id}_captioned.mp4")
    
        # Process video with subtitles
        try:
            ffmpeg.input(video_path).output(
                output_path,
                vf=f"subtitles='{subtitle_path}'",
                acodec='copy'
            ).run(overwrite_output=True)
            logger.info(f"Job {job_id}: FFmpeg processing completed")
        except ffmpeg.Error as e:
            logger.error(f"Job {job_id}: FFmpeg error: {e.stderr.decode('utf8') if e.stderr else 'Unknown error'}")
            raise
    
        # Clean up temporary files if needed
        # os.remove(video_path)
        # os.remove(subtitle_path)
    
        return output_path
    
    except Exception as e:
        logger.error(f"Job {job_id}: Error in process_captioning_v1: {str(e)}")
        raise
