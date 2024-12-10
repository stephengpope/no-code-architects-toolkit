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

# Mapping of position strings to ASS alignment numbers
POSITION_ALIGNMENT_MAP = {
    "bottom_left": 1,
    "bottom_center": 2,
    "bottom_right": 3,
    "middle_left": 4,
    "middle_center": 5,
    "middle_right": 6,
    "top_left": 7,
    "top_center": 8,
    "top_right": 9
}

def rgb_to_ass_color(rgb_color):
    """Convert RGB color code to ASS color format (&HAABBGGRR)."""
    if isinstance(rgb_color, str):
        rgb_color = rgb_color.lstrip('#')
        if len(rgb_color) == 6:
            r = int(rgb_color[0:2], 16)
            g = int(rgb_color[2:4], 16)
            b = int(rgb_color[4:6], 16)
            return f"&H00{b:02X}{g:02X}{r:02X}"
    # Default to white color if invalid
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
            return 384, 288  # Default resolution
    except Exception as e:
        logger.error(f"Error getting video resolution: {str(e)}")
        return 384, 288  # Default resolution

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

def calculate_position(position, video_width, video_height, x=None, y=None):
    """
    Calculate the (x, y) coordinates based on the position string and video resolution.
    If x and y are provided, they override the position settings.

    Positions are expected to be in the format 'vertical_horizontal', e.g., 'top_left'.
    """
    if x is not None and y is not None:
        logger.info(f"Using custom coordinates: x={x}, y={y}")
        return int(x), int(y)

    mapping = {
        "bottom_left": (100, video_height - 100),
        "bottom_center": (video_width // 2, video_height - 100),
        "bottom_right": (video_width - 100, video_height - 100),
        "middle_left": (100, video_height // 2),
        "middle_center": (video_width // 2, video_height // 2),
        "middle_right": (video_width - 100, video_height // 2),
        "top_left": (100, 100),
        "top_center": (video_width // 2, 100),
        "top_right": (video_width - 100, 100)
    }

    return mapping.get(position.lower(), (video_width // 2, video_height // 2))  # Default to 'middle_center'

def process_subtitle_text(text, replace_dict, all_caps, max_words_per_line):
    """Apply text transformations based on style options."""
    for old_word, new_word in replace_dict.items():
        text = re.sub(re.escape(old_word), new_word, text, flags=re.IGNORECASE)
    if all_caps:
        text = text.upper()
    if max_words_per_line > 0:
        words = text.split()
        lines = [' '.join(words[i:i+max_words_per_line]) for i in range(0, len(words), max_words_per_line)]
        text = '\\N'.join(lines)
    return text

def srt_to_transcription_result(srt_content):
    """Convert SRT content into a transcription_result-like structure."""
    subtitles = list(srt.parse(srt_content))
    segments = []
    for sub in subtitles:
        segments.append({
            'start': sub.start.total_seconds(),
            'end': sub.end.total_seconds(),
            'text': sub.content.strip(),
            'words': []  # Placeholder for word-level data if available
        })
    return {'segments': segments}

def create_style_line(style_options, video_resolution, is_karaoke=False):
    """
    Create the style line for ASS subtitles based on style_options.

    Parameters:
        style_options (dict): Dictionary containing style settings.
        video_resolution (tuple): Tuple of (width, height) of the video.
        is_karaoke (bool): Whether to create a karaoke style.

    Returns:
        str or dict: ASS style line string or error dictionary if font is unavailable.
    """
    font_family = style_options.get('font_family', 'Arial')
    available_fonts = get_available_fonts()
    if font_family not in available_fonts:
        logger.warning(f"Font '{font_family}' not found. Available fonts: {', '.join(available_fonts)}")
        return {'error': f"Font '{font_family}' not available.", 'available_fonts': available_fonts}

    line_color = rgb_to_ass_color(style_options.get('line_color', '#FFFFFF'))
    word_color = rgb_to_ass_color(style_options.get('word_color', '#FFFF00'))
    outline_color = rgb_to_ass_color(style_options.get('outline_color', '#000000'))
    box_color = rgb_to_ass_color(style_options.get('box_color', '#000000'))
    # shadow_color is not directly supported in ASS; it's handled via shadow_offset

    font_size = style_options.get('font_size', int(video_resolution[1] * 0.05))
    bold = '1' if style_options.get('bold', False) else '0'
    italic = '1' if style_options.get('italic', False) else '0'
    underline = '1' if style_options.get('underline', False) else '0'
    strikeout = '1' if style_options.get('strikeout', False) else '0'
    scale_x = style_options.get('scale_x', '100')
    scale_y = style_options.get('scale_y', '100')
    spacing = style_options.get('spacing', '0')
    angle = style_options.get('angle', '0')
    border_style = style_options.get('border_style', '1')  # 1: outline+shadow, 3: opaque box
    outline_width = style_options.get('outline_width', '2')
    shadow_offset = style_options.get('shadow_offset', '0')

    margin_l = style_options.get('margin_l', '20')
    margin_r = style_options.get('margin_r', '20')
    margin_v = style_options.get('margin_v', '20')

    # Map position to alignment
    position = style_options.get('position', 'middle_center')
    alignment = POSITION_ALIGNMENT_MAP.get(position.lower(), 5)

    if is_karaoke:
        # Karaoke format includes SecondaryColour
        style_line = "Style: Default"
        style_line += f",{font_family}"
        style_line += f",{font_size}"
        style_line += f",{line_color}"
        style_line += f",{word_color}"
        style_line += f",{outline_color}"
        style_line += f",{box_color}"
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
        style_line = "Style: Default"
        style_line += f",{font_family}"
        style_line += f",{font_size}"
        style_line += f",{line_color}"
        style_line += f",{outline_color}"
        style_line += f",{box_color}"
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

def srt_to_ass_classic(transcription_result, settings=None, replace_dict=None, video_resolution=(384, 288)):
    if settings is None:
        settings = {}
    if replace_dict is None:
        replace_dict = {}

    style_options = settings.copy()

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

    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)

    # Calculate (x, y) based on position or x and y
    x = style_options.get('x')
    y = style_options.get('y')
    position = style_options.get('position', 'middle_center')
    x_coord, y_coord = calculate_position(position, video_resolution[0], video_resolution[1], x, y)
    position_tag = f"{{\\pos({x_coord},{y_coord})}}"

    for segment in transcription_result['segments']:
        start_ass = format_ass_time(segment['start'])
        end_ass = format_ass_time(segment['end'])
        text = segment['text'].strip().replace('\n', ' ')
        text = process_subtitle_text(text, replace_dict, all_caps, max_words_per_line)
        ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{position_tag}{text}\n"

    return ass_content

def srt_to_ass_karaoke(transcription_result, settings=None, replace_dict=None, video_resolution=(384, 288)):
    if settings is None:
        settings = {}
    if replace_dict is None:
        replace_dict = {}

    style_options = settings.copy()

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

    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)

    # Calculate (x, y) based on position or x and y
    x = style_options.get('x')
    y = style_options.get('y')
    position = style_options.get('position', 'middle_center')
    x_coord, y_coord = calculate_position(position, video_resolution[0], video_resolution[1], x, y)
    position_tag = f"{{\\pos({x_coord},{y_coord})}}"

    word_color = rgb_to_ass_color(style_options.get('word_color', '#FFFF00'))

    for segment in transcription_result['segments']:
        start_ass = format_ass_time(segment['start'])
        end_ass = format_ass_time(segment['end'])

        words = segment.get('words', [])
        if not words:
            # No word-level data, fallback to classic style approach
            text = segment['text'].strip().replace('\n', ' ')
            text = process_subtitle_text(text, replace_dict, all_caps, max_words_per_line)
            ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{position_tag}{text}\n"
            continue

        karaoke_text = ""
        word_count = 0
        for word_info in words:
            word = word_info.get('word', '').strip().replace('\n', ' ')
            if not word:
                continue

            # Apply replacements and all_caps
            for old, new in replace_dict.items():
                word = re.sub(re.escape(old), new, word, flags=re.IGNORECASE)
            if all_caps:
                word = word.upper()

            duration_cs = int(round((word_info['end'] - word_info['start']) * 100))
            # Use word_color for highlighting
            highlighted_word = f"{{\\c{word_color}\\k{duration_cs}}}{word}{{\\c}} "
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

def srt_to_ass_highlight(transcription_result, settings=None, replace_dict=None, video_resolution=(384, 288)):
    """
    Convert transcription result to ASS format with a "highlight" style:
    The entire line is visible, but the currently active word is highlighted by changing its text color.
    One Dialogue event per word is produced, updating the highlight as time progresses.
    """
    if settings is None:
        settings = {}
    if replace_dict is None:
        replace_dict = {}

    style_options = settings.copy()

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

    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)

    # Calculate (x, y) based on position or x and y
    x = style_options.get('x')
    y = style_options.get('y')
    position = style_options.get('position', 'middle_center')
    x_coord, y_coord = calculate_position(position, video_resolution[0], video_resolution[1], x, y)
    position_tag = f"{{\\pos({x_coord},{y_coord})}}"

    word_color = rgb_to_ass_color(style_options.get('word_color', '#FFFF00'))

    for segment in transcription_result['segments']:
        start_time = segment['start']
        end_time = segment['end']
        text = segment['text'].strip().replace('\n', ' ')

        # Apply global replacements and all_caps to the entire line
        line_processed = process_subtitle_text(text, replace_dict, all_caps, max_words_per_line)

        words_info = segment.get('words', [])

        if words_info and len(words_info) > 0:
            # We have word-level timestamps
            processed_words = []
            for w_info in words_info:
                w = w_info['word'].strip().replace('\n', ' ')
                # Apply replacements and all_caps individually again to be sure
                for old_word, new_word in replace_dict.items():
                    w = re.sub(re.escape(old_word), new_word, w, flags=re.IGNORECASE)
                if all_caps:
                    w = w.upper()
                processed_words.append(w)

            # Now for each word, we produce a Dialogue event
            for i, w_info in enumerate(words_info):
                w_start = w_info['start']
                w_end = w_info['end']

                # Construct the line with highlight on the i-th word using word_color
                line_words_for_highlight = line_processed.split()

                if i < len(line_words_for_highlight):
                    # Highlight this word by changing its text color
                    line_words_for_highlight[i] = f"{{\\c{word_color}}}{line_words_for_highlight[i]}{{\\c}}"
                else:
                    # If indexing off, fallback by highlighting the last word
                    line_words_for_highlight[-1] = f"{{\\c{word_color}}}{line_words_for_highlight[-1]}{{\\c}}"

                highlighted_line = ' '.join(line_words_for_highlight)

                start_ass = format_ass_time(w_start)
                end_ass = format_ass_time(w_end)
                ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{position_tag}{highlighted_line}\n"

        else:
            # No word-level timing
            line_words = line_processed.split()
            if not line_words:
                # No words, just display the line as is
                start_ass = format_ass_time(start_time)
                end_ass = format_ass_time(end_time)
                ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{position_tag}{line_processed}\n"
                continue

            num_words = len(line_words)
            word_duration = (end_time - start_time) / num_words

            for i, w in enumerate(line_words):
                # Apply replaces and all_caps
                for old_word, new_word in replace_dict.items():
                    w = re.sub(re.escape(old_word), new_word, w, flags=re.IGNORECASE)
                if all_caps:
                    w = w.upper()

                word_start = start_time + i * word_duration
                word_end = word_start + word_duration
                start_ass = format_ass_time(word_start)
                end_ass = format_ass_time(word_end)
                # Highlight the i-th word by changing text color
                temp_line = line_words[:]
                temp_line[i] = f"{{\\c{word_color}}}{temp_line[i]}{{\\c}}"
                highlighted_line = ' '.join(temp_line)
                ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{position_tag}{highlighted_line}\n"

    return ass_content

def srt_to_ass_word_by_word(transcription_result, settings=None, replace_dict=None, video_resolution=(384, 288)):
    """
    Convert transcription result to ASS format with one word displayed at a time.
    If word-level timestamps are available, respect them; otherwise, evenly split the segment duration.
    Each word is shown as a separate Dialogue event line.
    """
    if settings is None:
        settings = {}
    if replace_dict is None:
        replace_dict = {}

    style_options = settings.copy()

    # Prepare ASS header
    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_resolution[0]}
PlayResY: {video_resolution[1]}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""

    # Create style line
    style_line = create_style_line(style_options, video_resolution, is_karaoke=False)
    if isinstance(style_line, dict) and 'error' in style_line:
        return style_line

    ass_content = ass_header + style_line + "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"

    # Extract style-related options
    max_words_per_line = int(style_options.get('max_words_per_line', 0))  # Not directly relevant here since we do one word per line
    all_caps = style_options.get('all_caps', False)

    # Calculate (x, y) based on position or x and y
    x = style_options.get('x')
    y = style_options.get('y')
    position = style_options.get('position', 'middle_center')
    x_coord, y_coord = calculate_position(position, video_resolution[0], video_resolution[1], x, y)
    position_tag = f"{{\\pos({x_coord},{y_coord})}}"

    for segment in transcription_result['segments']:
        start_time = segment['start']
        end_time = segment['end']
        segment_duration = end_time - start_time
        text = segment['text'].strip().replace('\n', ' ')

        # Attempt to get word-level data
        words_info = segment.get('words', [])

        if words_info and len(words_info) > 0:
            # We have word-level timestamps, respect them
            for word_info in words_info:
                w = word_info['word'].strip().replace('\n', ' ')
                if not w:
                    continue
                # Apply replaces and all_caps
                for old_word, new_word in replace_dict.items():
                    w = re.sub(re.escape(old_word), new_word, w, flags=re.IGNORECASE)
                if all_caps:
                    w = w.upper()

                word_start = word_info['start']
                word_end = word_info['end']
                # Create a Dialogue line for this word
                start_ass = format_ass_time(word_start)
                end_ass = format_ass_time(word_end)
                ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{position_tag}{w}\n"
        else:
            # No word-level timing, split the text into words and divide time evenly
            words_list = text.split()
            if not words_list:
                # No words at all, skip
                continue

            # Evenly divide the segment duration among words
            num_words = len(words_list)
            if num_words == 0:
                continue
            word_duration = segment_duration / num_words

            for i, w in enumerate(words_list):
                # Apply replaces and all_caps
                for old_word, new_word in replace_dict.items():
                    w = re.sub(re.escape(old_word), new_word, w, flags=re.IGNORECASE)
                if all_caps:
                    w = w.upper()

                word_start = start_time + i * word_duration
                word_end = word_start + word_duration
                start_ass = format_ass_time(word_start)
                end_ass = format_ass_time(word_end)
                ass_content += f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{position_tag}{w}\n"

    return ass_content

def srt_to_ass_underline(transcription_result, settings=None, replace_dict=None, video_resolution=(1920, 1080)):
    if settings is None:
        settings = {}
    if replace_dict is None:
        replace_dict = {}

    style_options = settings.copy()

    # Prepare ASS header and styles
    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_resolution[0]}
PlayResY: {video_resolution[1]}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{style_options.get('font_family', 'Arial')},{style_options.get('font_size', 50)},{rgb_to_ass_color(style_options.get('line_color', '#FFFFFF'))},{rgb_to_ass_color(style_options.get('outline_color', '#000000'))},{rgb_to_ass_color(style_options.get('box_color', '#000000'))},{int(style_options.get('bold', False))},{int(style_options.get('italic', False))},{int(style_options.get('underline', False))},{int(style_options.get('strikeout', False))},{style_options.get('scale_x', 100)},{style_options.get('scale_y', 100)},{style_options.get('spacing', 0)},{style_options.get('angle', 0)},{style_options.get('border_style', 1)},{style_options.get('outline_width', 2)},{style_options.get('shadow_offset', 0)},{POSITION_ALIGNMENT_MAP.get(style_options.get('position', 'middle_center').lower(), 5)},20,20,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass_content = ass_header

    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)

    # Calculate position
    position_str = style_options.get('position', 'middle_center')
    x, y = calculate_position(position_str, video_resolution[0], video_resolution[1], style_options.get('x'), style_options.get('y'))

    # Determine alignment number based on position
    alignment = POSITION_ALIGNMENT_MAP.get(position_str.lower(), 5)

    for segment in transcription_result['segments']:
        start_time = format_ass_time(segment['start'])
        end_time = format_ass_time(segment['end'])
        text = segment['text'].strip()

        # Apply replacements and transformations
        text = process_subtitle_text(text, replace_dict, all_caps, max_words_per_line)

        if 'words' in segment and segment['words']:
            words_info = segment['words']
            for i, word_info in enumerate(words_info):
                word = word_info.get('word', '').strip()
                if not word:
                    continue

                # Apply replacements and all_caps
                for old, new in replace_dict.items():
                    word = re.sub(re.escape(old), new, word, flags=re.IGNORECASE)
                if all_caps:
                    word = word.upper()

                # Apply underline
                underlined_word = f"{{\\u1}}{word}{{\\u0}}"

                # Adjust timing to prevent overlap
                if i < len(words_info) - 1:
                    next_word_start = words_info[i + 1]['start']
                    word_end = min(word_info['end'], next_word_start - 0.01)  # 10ms gap
                else:
                    word_end = word_info['end']

                # Format dialogue line
                ass_line = f"Dialogue: 0,{format_ass_time(word_info['start'])},{format_ass_time(word_end)},Default,,0,0,0,,{{\\pos({x},{y})\\an{alignment}}}{underlined_word}\n"
                ass_content += ass_line
        else:
            # No word-level data; apply underline to entire text
            underlined_text = f"{{\\u1}}{text}{{\\u0}}"
            ass_line = f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{{\\pos({x},{y})\\an{alignment}}}{underlined_text}\n"
            ass_content += ass_line

    return ass_content

def process_captioning_v1(video_url, captions, settings, replace, job_id, language='auto'):
    """Enhanced v1 captioning process with transcription fallback and multiple styles."""
    try:
        # Ensure 'settings' is a dictionary
        if not isinstance(settings, dict):
            logger.error(f"Job {job_id}: 'settings' should be a dictionary.")
            return {"error": "'settings' should be a dictionary."}

        # Normalize settings keys by replacing hyphens with underscores
        style_options = {k.replace('-', '_'): v for k, v in settings.items()}

        # Ensure 'replace' is a list of dicts with 'find' and 'replace' keys
        if not isinstance(replace, list):
            logger.error(f"Job {job_id}: 'replace' should be a list of objects with 'find' and 'replace' keys.")
            return {"error": "'replace' should be a list of objects with 'find' and 'replace' keys."}

        # Convert 'replace' list to dictionary
        replace_dict = {}
        for item in replace:
            if 'find' in item and 'replace' in item:
                replace_dict[item['find']] = item['replace']
            else:
                logger.warning(f"Job {job_id}: Invalid replace item {item}. Skipping.")

        # Handle deprecated 'highlight_color' by merging it into 'word_color'
        if 'highlight_color' in style_options:
            logger.warning(f"Job {job_id}: 'highlight_color' is deprecated and has been merged into 'word_color'. Using 'word_color' instead.")
            # Override 'word_color' with 'highlight_color' if needed
            style_options['word_color'] = style_options.pop('highlight_color')

        # Early Font Availability Check
        font_family = style_options.get('font_family', 'Arial')
        available_fonts = get_available_fonts()
        if font_family not in available_fonts:
            logger.warning(f"Font '{font_family}' not found. Available fonts: {', '.join(available_fonts)}")
            return {'error': f"Font '{font_family}' not available.", 'available_fonts': available_fonts}

        logger.info(f"Job {job_id}: Font '{font_family}' is available.")

        # Proceed with downloading and processing the video
        # Download video
        video_path = download_file(video_url, STORAGE_PATH)
        logger.info(f"Job {job_id}: Video downloaded to {video_path}")

        # Get video resolution
        video_resolution = get_video_resolution(video_path)
        logger.info(f"Job {job_id}: Video resolution detected as {video_resolution[0]}x{video_resolution[1]}")

        # Determine style
        style_type = style_options.get('style', 'classic').lower()

        # Determine subtitle content
        if captions:
            # Check if it's ASS by looking for '[Script Info]'
            if '[Script Info]' in captions:
                # It's ASS directly
                subtitle_content = captions
                subtitle_type = 'ass'
            else:
                # Treat as SRT
                transcription_result = srt_to_transcription_result(captions)
                # Generate ASS based on chosen style
                if style_type == 'classic':
                    subtitle_content = srt_to_ass_classic(transcription_result, settings=style_options, replace_dict=replace_dict, video_resolution=video_resolution)
                elif style_type == 'karaoke':
                    subtitle_content = srt_to_ass_karaoke(transcription_result, settings=style_options, replace_dict=replace_dict, video_resolution=video_resolution)
                elif style_type == 'highlight':
                    subtitle_content = srt_to_ass_highlight(transcription_result, settings=style_options, replace_dict=replace_dict, video_resolution=video_resolution)
                elif style_type == 'underline':
                    subtitle_content = srt_to_ass_underline(transcription_result, settings=style_options, replace_dict=replace_dict, video_resolution=video_resolution)
                elif style_type == 'word_by_word':
                    subtitle_content = srt_to_ass_word_by_word(transcription_result, settings=style_options, replace_dict=replace_dict, video_resolution=video_resolution)
                else:
                    logger.warning(f"Job {job_id}: Unknown style '{style_type}'. Defaulting to 'classic'.")
                    subtitle_content = srt_to_ass_classic(transcription_result, settings=style_options, replace_dict=replace_dict, video_resolution=video_resolution)
                subtitle_type = 'ass'
        else:
            # No captions provided, generate transcription
            logger.info(f"Job {job_id}: No captions provided, generating transcription")
            transcription_result = generate_transcription(video_path, language=language)
            if style_type == 'classic':
                subtitle_content = srt_to_ass_classic(transcription_result, settings=style_options, replace_dict=replace_dict, video_resolution=video_resolution)
            elif style_type == 'karaoke':
                subtitle_content = srt_to_ass_karaoke(transcription_result, settings=style_options, replace_dict=replace_dict, video_resolution=video_resolution)
            elif style_type == 'highlight':
                subtitle_content = srt_to_ass_highlight(transcription_result, settings=style_options, replace_dict=replace_dict, video_resolution=video_resolution)
            elif style_type == 'underline':
                subtitle_content = srt_to_ass_underline(transcription_result, settings=style_options, replace_dict=replace_dict, video_resolution=video_resolution)
            elif style_type == 'word_by_word':
                subtitle_content = srt_to_ass_word_by_word(transcription_result, settings=style_options, replace_dict=replace_dict, video_resolution=video_resolution)
            else:
                logger.warning(f"Job {job_id}: Unknown style '{style_type}'. Defaulting to 'classic'.")
                subtitle_content = srt_to_ass_classic(transcription_result, settings=style_options, replace_dict=replace_dict, video_resolution=video_resolution)
            subtitle_type = 'ass'

        # Check for font availability and return available fonts if not
        # Note: This check is now redundant due to early font check, but keeping for safety
        if isinstance(subtitle_content, dict) and 'error' in subtitle_content:
            logger.error(f"Job {job_id}: {subtitle_content['error']}")
            available_fonts = subtitle_content.get('available_fonts', [])
            error_message = subtitle_content.get('error', 'Unknown font error.')
            return {"error": error_message, "available_fonts": available_fonts}

        # Save subtitle content
        subtitle_filename = f"{job_id}.{subtitle_type}"
        subtitle_path = os.path.join(STORAGE_PATH, subtitle_filename)
        with open(subtitle_path, 'w', encoding='utf-8') as f:
            f.write(subtitle_content)
        logger.info(f"Job {job_id}: Subtitle file saved to {subtitle_path}")

        # Prepare output path
        output_filename = f"{job_id}_captioned.mp4"
        output_path = os.path.join(STORAGE_PATH, output_filename)

        # Process video with subtitles
        try:
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
