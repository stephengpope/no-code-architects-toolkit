import os
import ffmpeg
import logging
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

def split_lines(text, max_words_per_line):
    """Split text into multiple lines based on max_words_per_line."""
    if max_words_per_line <= 0:
        return [text]
    
    words = text.split()
    lines = [' '.join(words[i:i + max_words_per_line]) for i in range(0, len(words), max_words_per_line)]
    return lines

def create_style_line(style_options, video_resolution, is_karaoke=False, style_type='classic'):
    """
    Create the style line for ASS subtitles based on style_options.

    Parameters:
        style_options (dict): Dictionary containing style settings.
        video_resolution (tuple): Tuple of (width, height) of the video.
        is_karaoke (bool): Whether to create a karaoke style.
        style_type (str): Type of the style ('classic', 'karaoke', 'highlight', 'underline', 'word_by_word').

    Returns:
        str or dict: ASS style line string or error dictionary if font is unavailable.
    """
    font_family = style_options.get('font_family', 'Arial')
    available_fonts = get_available_fonts()
    if font_family not in available_fonts:
        logger.warning(f"Font '{font_family}' not found. Available fonts: {', '.join(available_fonts)}")
        return {'error': f"Font '{font_family}' not available.", 'available_fonts': available_fonts}

    # Convert colors to ASS format
    line_color = rgb_to_ass_color(style_options.get('line_color', '#FFFFFF'))
    word_color = rgb_to_ass_color(style_options.get('word_color', '#FFFF00'))
    outline_color = rgb_to_ass_color(style_options.get('outline_color', '#000000'))
    box_color = rgb_to_ass_color(style_options.get('box_color', '#000000'))

    # Font styles
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

    # Margins
    margin_l = style_options.get('margin_l', '20')
    margin_r = style_options.get('margin_r', '20')
    margin_v = style_options.get('margin_v', '20')

    # Alignment based on position
    position = style_options.get('position', 'middle_center')
    alignment = POSITION_ALIGNMENT_MAP.get(position.lower(), 5)

    # Base style line
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

def generate_ass_header(style_options, video_resolution, style_type='classic'):
    """
    Generate the ASS file header with styles.

    Parameters:
        style_options (dict): Dictionary containing style settings.
        video_resolution (tuple): Tuple of (width, height) of the video.
        style_type (str): Type of the style ('classic', 'karaoke', etc.).

    Returns:
        str or dict: The ASS file header or an error dictionary.
    """
    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_resolution[0]}
PlayResY: {video_resolution[1]}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""
    style_line = create_style_line(style_options, video_resolution, style_type=style_type)
    if isinstance(style_line, dict) and 'error' in style_line:
        return style_line

    ass_header += style_line + "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    return ass_header

def srt_to_ass_classic(transcription_result, settings=None, replace_dict=None, video_resolution=(384, 288)):
    """Convert transcription result to ASS classic style."""
    if settings is None:
        settings = {}
    if replace_dict is None:
        replace_dict = {}

    style_options = settings.copy()

    ass_header = generate_ass_header(style_options, video_resolution, style_type='classic')
    if isinstance(ass_header, dict) and 'error' in ass_header:
        return ass_header

    ass_content = ass_header

    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)

    # Calculate (x, y) based on position or x and y
    x = style_options.get('x')
    y = style_options.get('y')
    position = style_options.get('position', 'middle_center')
    base_x, base_y = calculate_position(position, video_resolution[0], video_resolution[1], x, y)

    # Define line height
    font_size = style_options.get('font_size', int(video_resolution[1] * 0.05))
    line_height = int(font_size * 1.2)

    for segment in transcription_result['segments']:
        text = segment['text'].strip().replace('\n', ' ')
        lines = split_lines(text, max_words_per_line)
        for line_number, line in enumerate(lines):
            processed_text = process_subtitle_text(line, replace_dict, all_caps, max_words_per_line)
            y_coord = base_y + (line_number * line_height)
            position_tag = f"{{\\pos({base_x},{y_coord})}}"
            ass_content += f"Dialogue: 0,{format_ass_time(segment['start'])},{format_ass_time(segment['end'])},Default,,0,0,0,,{position_tag}{processed_text}\n"

    return ass_content

def srt_to_ass_karaoke(transcription_result, settings=None, replace_dict=None, video_resolution=(384, 288)):
    """Convert transcription result to ASS karaoke style with proper handling of max_words_per_line."""
    if settings is None:
        settings = {}
    if replace_dict is None:
        replace_dict = {}

    style_options = settings.copy()
    ass_header = generate_ass_header(style_options, video_resolution, style_type='karaoke')
    if isinstance(ass_header, dict) and 'error' in ass_header:
        return ass_header

    ass_content = ass_header
    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)

    # Base position
    x = style_options.get('x')
    y = style_options.get('y')
    position = style_options.get('position', 'middle_center')
    base_x, base_y = calculate_position(position, video_resolution[0], video_resolution[1], x, y)
    
    word_color = rgb_to_ass_color(style_options.get('word_color', '#FFFF00'))
    font_size = style_options.get('font_size', int(video_resolution[1] * 0.05))
    line_height = int(font_size * 1.2)

    # Calculate base position and spacing
    font_size = style_options.get('font_size', int(video_resolution[1] * 0.05))
    line_height = int(font_size * 1.2)
    base_x = video_resolution[0] // 2  # Center horizontally
    base_y = video_resolution[1] // 2  # Start at vertical center

    for segment in transcription_result['segments']:
        words = segment.get('words', [])
        if not words:
            continue

        # Group words for this segment
        segment_words = []
        for word_info in words:
            word = word_info.get('word', '').strip().replace('\n', ' ')
            if word:
                segment_words.append(word_info)

        if not segment_words:
            continue

        # Split into lines but keep as one dialogue event
        lines_content = []
        if max_words_per_line > 0:
            current_line = []
            current_line_words = 0
            
            for word_info in segment_words:
                word = word_info.get('word', '').strip().replace('\n', ' ')
                word = process_subtitle_text(word, replace_dict, all_caps, max_words_per_line=0)
                duration_cs = int(round((word_info['end'] - word_info['start']) * 100))
                highlighted_word = f"{{\\k{duration_cs}}}{word} "
                
                current_line.append(highlighted_word)
                current_line_words += 1
                
                if current_line_words >= max_words_per_line:
                    lines_content.append(''.join(current_line).strip())
                    current_line = []
                    current_line_words = 0
                    
            if current_line:
                lines_content.append(''.join(current_line).strip())
        else:
            # Single line karaoke
            line_content = []
            for word_info in segment_words:
                word = word_info.get('word', '').strip().replace('\n', ' ')
                word = process_subtitle_text(word, replace_dict, all_caps, max_words_per_line=0)
                duration_cs = int(round((word_info['end'] - word_info['start']) * 100))
                highlighted_word = f"{{\\k{duration_cs}}}{word} "
                line_content.append(highlighted_word)
            lines_content = [''.join(line_content).strip()]

        # Join lines with \N and create single dialogue event
        karaoke_text = '\\N'.join(lines_content)
        position_tag = f"{{\\pos({base_x},{base_y})}}"
        
        # One dialogue event for all lines
        word_color = rgb_to_ass_color(style_options.get('word_color', '#FFFF00'))
        line_color = rgb_to_ass_color(style_options.get('line_color', '#FFFFFF'))
        
        # Use both colors in dialogue lines
        ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{position_tag}{{\\c{word_color}}}{karaoke_text}{{\\c{line_color}}}\n"

    return ass_content

def srt_to_ass_highlight(transcription_result, settings=None, replace_dict=None, video_resolution=(384, 288)):
    """Convert transcription result to ASS format with highlight style."""
    if settings is None:
        settings = {}
    if replace_dict is None:
        replace_dict = {}

    style_options = settings.copy()
    ass_header = generate_ass_header(style_options, video_resolution, style_type='highlight')
    if isinstance(ass_header, dict) and 'error' in ass_header:
        return ass_header

    ass_content = ass_header
    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)

    # Base position
    x = style_options.get('x')
    y = style_options.get('y')
    position = style_options.get('position', 'middle_center')
    base_x, base_y = calculate_position(position, video_resolution[0], video_resolution[1], x, y)
    position_tag = f"{{\\pos({base_x},{base_y})}}"

    word_color = rgb_to_ass_color(style_options.get('word_color', '#FFFF00'))
    line_color = rgb_to_ass_color(style_options.get('line_color', '#FFFFFF'))

    for segment in transcription_result['segments']:
        words = segment.get('words', [])
        if not words:
            continue

        # Group words and process text
        segment_words = []
        processed_words = []
        for word_info in words:
            word = word_info.get('word', '').strip().replace('\n', ' ')
            if word:
                processed_word = process_subtitle_text(word, replace_dict, all_caps, max_words_per_line=0)
                segment_words.append(word_info)
                processed_words.append(processed_word)

        if not segment_words:
            continue

        # Split into lines
        lines = []
        if max_words_per_line > 0:
            for i in range(0, len(processed_words), max_words_per_line):
                lines.append(processed_words[i:i + max_words_per_line])
        else:
            lines = [processed_words]

        # Process each word timing
        for i, word_info in enumerate(segment_words):
            # Find which line and position the word is in
            word_line_index = i // max_words_per_line if max_words_per_line > 0 else 0
            word_index_in_line = i % max_words_per_line if max_words_per_line > 0 else i

            # Create highlighted version of all lines
            highlighted_lines = []
            for line_idx, line in enumerate(lines):
                if line_idx == word_line_index:
                    # This is the line containing the current word
                    highlighted_words = []
                    for w_idx, w in enumerate(line):
                        if w_idx == word_index_in_line:
                            # This is the current word - highlight it
                            highlighted_words.append(f"{{\\c{word_color}}}{w}{{\\c{line_color}}}")
                        else:
                            # Other words in their original color
                            highlighted_words.append(f"{{\\c{word_color}}}{w}{{\\c{line_color}}}")
                    highlighted_lines.append(' '.join(highlighted_words))
                else:
                    # Other lines remain unchanged
                    highlighted_lines.append(' '.join(line))

            # Join lines with \N
            full_text = '\\N'.join(highlighted_lines)

            # Add dialogue event
            start_time = format_ass_time(word_info['start'])
            end_time = format_ass_time(word_info['end'])
            ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{position_tag}{full_text}\n"

    return ass_content

def srt_to_ass_underline(transcription_result, settings=None, replace_dict=None, video_resolution=(384, 288)):
    """Convert transcription result to ASS format with an underline style."""
    if settings is None:
        settings = {}
    if replace_dict is None:
        replace_dict = {}

    style_options = settings.copy()
    ass_header = generate_ass_header(style_options, video_resolution, style_type='underline')
    if isinstance(ass_header, dict) and 'error' in ass_header:
        return ass_header

    ass_content = ass_header
    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)

    # Base position
    x = style_options.get('x')
    y = style_options.get('y')
    position = style_options.get('position', 'middle_center')
    base_x, base_y = calculate_position(position, video_resolution[0], video_resolution[1], x, y)
    position_tag = f"{{\\pos({base_x},{base_y})}}"
    line_color = rgb_to_ass_color(style_options.get('line_color', '#FFFFFF'))

    for segment in transcription_result['segments']:
        words = segment.get('words', [])
        if not words:
            continue

        # Group words and process text
        segment_words = []
        processed_words = []
        for word_info in words:
            word = word_info.get('word', '').strip().replace('\n', ' ')
            if word:
                processed_word = process_subtitle_text(word, replace_dict, all_caps, max_words_per_line=0)
                segment_words.append(word_info)
                processed_words.append(processed_word)

        if not segment_words:
            continue

        # Split into lines
        lines = []
        if max_words_per_line > 0:
            for i in range(0, len(processed_words), max_words_per_line):
                lines.append(processed_words[i:i + max_words_per_line])
        else:
            lines = [processed_words]

        # Process each word timing
        for i, word_info in enumerate(segment_words):
            # Find which line and position the word is in
            word_line_index = i // max_words_per_line if max_words_per_line > 0 else 0
            word_index_in_line = i % max_words_per_line if max_words_per_line > 0 else i

            # Create underlined version of all lines
            underlined_lines = []
            for line_idx, line in enumerate(lines):
                if line_idx == word_line_index:
                    # This is the line containing the current word
                    words_in_line = []
                    for w_idx, w in enumerate(line):
                        if w_idx == word_index_in_line:
                            # This is the current word - underline it
                            words_in_line.append(f"{{\\u1}}{w}{{\\u0}}")
                        else:
                            # Other words without underline
                            words_in_line.append(w)
                    underlined_lines.append(' '.join(words_in_line))
                else:
                    # Other lines remain unchanged
                    underlined_lines.append(' '.join(line))

            # Join lines with \N
            full_text = '\\N'.join(underlined_lines)

            # Add dialogue event
            start_time = format_ass_time(word_info['start'])
            end_time = format_ass_time(word_info['end'])
            ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{position_tag}{{\\c{line_color}}}{full_text}\n"

    return ass_content

def srt_to_ass_word_by_word(transcription_result, settings=None, replace_dict=None, video_resolution=(384, 288)):
    """Convert transcription result to ASS format with one word displayed at a time."""
    if settings is None:
        settings = {}
    if replace_dict is None:
        replace_dict = {}

    style_options = settings.copy()
    ass_header = generate_ass_header(style_options, video_resolution, style_type='word_by_word')
    if isinstance(ass_header, dict) and 'error' in ass_header:
        return ass_header

    ass_content = ass_header
    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)

    # Calculate base position and spacing
    font_size = style_options.get('font_size', int(video_resolution[1] * 0.05))
    line_height = int(font_size * 1.2)
    position_str = style_options.get('position', 'middle_center')
    base_x, base_y = calculate_position(position_str, video_resolution[0], video_resolution[1],
                              style_options.get('x'), style_options.get('y'))

    word_color = rgb_to_ass_color(style_options.get('word_color', '#FFFF00'))

    for segment in transcription_result['segments']:
        words = segment.get('words', [])
        if not words:
            continue

        # Group words for max_words_per_line
        grouped_words = []
        if max_words_per_line > 0:
            for i in range(0, len(words), max_words_per_line):
                grouped_words.append(words[i:i + max_words_per_line])
        else:
            grouped_words = [words]  # Single group if no line limit

        # Process each group of words
        for line_num, word_group in enumerate(grouped_words):
            y_coord = base_y + (line_num * line_height)
            position_tag = f"{{\\pos({base_x},{y_coord})}}"

            # Process each word in the group
            for word_info in word_group:
                word = word_info.get('word', '').strip().replace('\n', ' ')
                if not word:
                    continue
                
                word = process_subtitle_text(word, replace_dict, all_caps, max_words_per_line=0)
                start_time = format_ass_time(word_info['start'])
                end_time = format_ass_time(word_info['end'])
                
                ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{position_tag}{{\\c{word_color}}}{word}\n"

    return ass_content

def process_subtitle_events(transcription_result, style_type, settings, replace_dict, video_resolution):
    """
    Process transcription result into ASS subtitle content based on the selected style.

    Parameters:
        transcription_result (dict): The transcription result containing segments and words.
        style_type (str): The type of subtitle style ('classic', 'karaoke', 'highlight', 'underline', 'word_by_word').
        settings (dict): Style settings.
        replace_dict (dict): Dictionary for text replacements.
        video_resolution (tuple): (width, height) of the video.

    Returns:
        str or dict: The ASS subtitle content or an error dictionary.
    """
    style_functions = {
        'classic': srt_to_ass_classic,
        'karaoke': srt_to_ass_karaoke,
        'highlight': srt_to_ass_highlight,
        'underline': srt_to_ass_underline,
        'word_by_word': srt_to_ass_word_by_word
    }

    func = style_functions.get(style_type.lower())
    if not func:
        logger.warning(f"Unknown style '{style_type}'. Defaulting to 'classic'.")
        func = srt_to_ass_classic

    return func(transcription_result, settings=settings, replace_dict=replace_dict, video_resolution=video_resolution)

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
                subtitle_content = process_subtitle_events(transcription_result, style_type, style_options, replace_dict, video_resolution)
                subtitle_type = 'ass'
        else:
            # No captions provided, generate transcription
            logger.info(f"Job {job_id}: No captions provided, generating transcription")
            transcription_result = generate_transcription(video_path, language=language)
            subtitle_content = process_subtitle_events(transcription_result, style_type, style_options, replace_dict, video_resolution)
            subtitle_type = 'ass'

        # Check for font availability and return available fonts if not
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
