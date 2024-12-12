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
    # If x and y are provided, we use them directly. Otherwise, we just return center by default.
    if x is not None and y is not None:
        logger.info(f"Using custom coordinates: x={x}, y={y}")
        return int(x), int(y)
    return video_width // 2, video_height // 2

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

def determine_alignment_code(position_str, alignment_str, x, y):
    """
    Determine the final \an alignment code based on x,y, position, and alignment.
    """
    horizontal_map = {
        'left': 1,
        'center': 2,
        'right': 3
    }

    if x is not None and y is not None:
        # x,y provided: ignore position, default vertical = middle row (4–6)
        vertical_code = 4  # middle-left as base
        horiz_code = horizontal_map.get(alignment_str, 2)  # default center if not given
        an_code = vertical_code + (horiz_code - 1)
        return an_code, True

    # No x,y: use position
    base_code = POSITION_ALIGNMENT_MAP.get(position_str.lower(), 5)  # default middle_center
    if alignment_str in horizontal_map:
        # Derive vertical from base_code
        if base_code in [7,8,9]:
            vertical_base = 7
        elif base_code in [4,5,6]:
            vertical_base = 4
        else:
            vertical_base = 1
        horiz_code = horizontal_map[alignment_str]
        an_code = vertical_base + (horiz_code - 1)
    else:
        # No alignment given, use base_code as is
        an_code = base_code
    return an_code, False

def create_style_line(style_options, video_resolution):
    """
    Create the style line for ASS subtitles based on style_options.
    Includes SecondaryColour after PrimaryColour.
    """
    font_family = style_options.get('font_family', 'Arial')
    available_fonts = get_available_fonts()
    if font_family not in available_fonts:
        logger.warning(f"Font '{font_family}' not found. Available fonts: {', '.join(available_fonts)}")
        return {'error': f"Font '{font_family}' not available.", 'available_fonts': available_fonts}

    # Convert colors to ASS format
    line_color = rgb_to_ass_color(style_options.get('line_color', '#FFFFFF'))
    # Use line_color as secondary_color for simplicity
    secondary_color = line_color
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
    border_style = style_options.get('border_style', '1')
    outline_width = style_options.get('outline_width', '2')
    shadow_offset = style_options.get('shadow_offset', '0')

    margin_l = style_options.get('margin_l', '20')
    margin_r = style_options.get('margin_r', '20')
    margin_v = style_options.get('margin_v', '20')

    # position sets a default alignment for the style
    position = style_options.get('position', 'middle_center')
    alignment = POSITION_ALIGNMENT_MAP.get(position.lower(), 5)

    style_line = (f"Style: Default,{font_family},{font_size},{line_color},{secondary_color},"
                  f"{outline_color},{box_color},{bold},{italic},{underline},{strikeout},"
                  f"{scale_x},{scale_y},{spacing},{angle},{border_style},{outline_width},"
                  f"{shadow_offset},{alignment},{margin_l},{margin_r},{margin_v},0")

    return style_line

def generate_ass_header(style_options, video_resolution):
    """
    Generate the ASS file header with styles.
    """
    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_resolution[0]}
PlayResY: {video_resolution[1]}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""
    style_line = create_style_line(style_options, video_resolution)
    if isinstance(style_line, dict) and 'error' in style_line:
        return style_line

    ass_header += style_line + "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    return ass_header

def handle_classic(transcription_result, style_options, replace_dict, video_resolution):
    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)
    if style_options['font_size'] is None:
        style_options['font_size'] = int(video_resolution[1] * 0.05)
    font_size = style_options['font_size']

    position_str = style_options.get('position', 'middle_center')
    alignment_str = style_options.get('alignment', None)
    x = style_options.get('x')
    y = style_options.get('y')

    logger.info(f"[Classic] position={position_str}, alignment={alignment_str}, x={x}, y={y}")
    an_code, use_pos = determine_alignment_code(position_str, alignment_str, x, y)
    logger.info(f"[Classic] an_code={an_code}, use_pos={use_pos}")

    line_height = int(font_size * 1.2)
    events = []

    for segment in transcription_result['segments']:
        text = segment['text'].strip().replace('\n', ' ')
        lines = split_lines(text, max_words_per_line)
        for line_number, line in enumerate(lines):
            processed_text = process_subtitle_text(line, replace_dict, all_caps, max_words_per_line)
            if use_pos:
                line_y = y + (line_number * line_height) if y is not None else (line_number * line_height)
                position_tag = f"{{\\an{an_code}\\pos({x},{line_y})}}"
            else:
                position_tag = f"{{\\an{an_code}}}"
            start_time = format_ass_time(segment['start'])
            end_time = format_ass_time(segment['end'])
            events.append(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{position_tag}{processed_text}")
    return "\n".join(events)

def handle_karaoke(transcription_result, style_options, replace_dict, video_resolution):
    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)
    if style_options['font_size'] is None:
        style_options['font_size'] = int(video_resolution[1] * 0.05)
    font_size = style_options['font_size']

    position_str = style_options.get('position', 'middle_center')
    alignment_str = style_options.get('alignment', None)
    x = style_options.get('x')
    y = style_options.get('y')

    logger.info(f"[Karaoke] position={position_str}, alignment={alignment_str}, x={x}, y={y}")
    an_code, use_pos = determine_alignment_code(position_str, alignment_str, x, y)
    logger.info(f"[Karaoke] an_code={an_code}, use_pos={use_pos}")

    word_color = rgb_to_ass_color(style_options.get('word_color', '#FFFF00'))
    line_height = int(font_size * 1.2)
    events = []

    for segment in transcription_result['segments']:
        words = segment.get('words', [])
        if not words:
            continue

        if max_words_per_line > 0:
            lines_content = []
            current_line = []
            current_line_words = 0
            for w_info in words:
                word = w_info.get('word', '').strip().replace('\n', ' ')
                word = process_subtitle_text(word, replace_dict, all_caps, 0)
                duration_cs = int(round((w_info['end'] - w_info['start']) * 100))
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
            line_content = []
            for w_info in words:
                word = w_info.get('word', '').strip().replace('\n', ' ')
                word = process_subtitle_text(word, replace_dict, all_caps, 0)
                duration_cs = int(round((w_info['end'] - w_info['start']) * 100))
                highlighted_word = f"{{\\k{duration_cs}}}{word} "
                line_content.append(highlighted_word)
            lines_content = [''.join(line_content).strip()]

        dialogue_text = '\\N'.join(lines_content)
        if use_pos:
            position_tag = f"{{\\an{an_code}\\pos({x},{y})}}"
        else:
            position_tag = f"{{\\an{an_code}}}"

        start_time = format_ass_time(words[0]['start'])
        end_time = format_ass_time(words[-1]['end'])
        events.append(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{position_tag}{{\\c{word_color}}}{dialogue_text}")
    return "\n".join(events)

def handle_highlight(transcription_result, style_options, replace_dict, video_resolution):
    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)
    if style_options['font_size'] is None:
        style_options['font_size'] = int(video_resolution[1] * 0.05)
    font_size = style_options['font_size']

    position_str = style_options.get('position', 'middle_center')
    alignment_str = style_options.get('alignment', None)
    x = style_options.get('x')
    y = style_options.get('y')

    logger.info(f"[Highlight] position={position_str}, alignment={alignment_str}, x={x}, y={y}")
    an_code, use_pos = determine_alignment_code(position_str, alignment_str, x, y)
    logger.info(f"[Highlight] an_code={an_code}, use_pos={use_pos}")

    word_color = rgb_to_ass_color(style_options.get('word_color', '#FFFF00'))
    line_color = rgb_to_ass_color(style_options.get('line_color', '#FFFFFF'))
    events = []

    for segment in transcription_result['segments']:
        words = segment.get('words', [])
        if not words:
            continue
        processed_words = []
        for w_info in words:
            w = w_info.get('word', '').strip().replace('\n', ' ')
            w = process_subtitle_text(w, replace_dict, all_caps, 0)
            if w:
                processed_words.append((w, w_info['start'], w_info['end']))

        if not processed_words:
            continue

        if max_words_per_line > 0:
            line_sets = [processed_words[i:i+max_words_per_line] for i in range(0, len(processed_words), max_words_per_line)]
        else:
            line_sets = [processed_words]

        for line_set in line_sets:
            for idx, (word, w_start, w_end) in enumerate(line_set):
                highlighted_lines = []
                line_words = []
                for w_idx, (w_text, _, _) in enumerate(line_set):
                    if w_idx == idx:
                        line_words.append(f"{{\\c{word_color}}}{w_text}{{\\c{line_color}}}")
                    else:
                        line_words.append(w_text)
                highlighted_lines.append(' '.join(line_words))
                full_text = '\\N'.join(highlighted_lines)

                if use_pos:
                    position_tag = f"{{\\an{an_code}\\pos({x},{y})}}"
                else:
                    position_tag = f"{{\\an{an_code}}}"

                start_time = format_ass_time(w_start)
                end_time = format_ass_time(w_end)
                events.append(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{position_tag}{{\\c{line_color}}}{full_text}")
    return "\n".join(events)

def handle_underline(transcription_result, style_options, replace_dict, video_resolution):
    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)
    if style_options['font_size'] is None:
        style_options['font_size'] = int(video_resolution[1] * 0.05)
    font_size = style_options['font_size']

    position_str = style_options.get('position', 'middle_center')
    alignment_str = style_options.get('alignment', None)
    x = style_options.get('x')
    y = style_options.get('y')

    logger.info(f"[Underline] position={position_str}, alignment={alignment_str}, x={x}, y={y}")
    an_code, use_pos = determine_alignment_code(position_str, alignment_str, x, y)
    logger.info(f"[Underline] an_code={an_code}, use_pos={use_pos}")

    line_color = rgb_to_ass_color(style_options.get('line_color', '#FFFFFF'))
    events = []

    for segment in transcription_result['segments']:
        words = segment.get('words', [])
        if not words:
            continue

        processed_words = []
        for w_info in words:
            w = w_info.get('word', '').strip().replace('\n', ' ')
            w = process_subtitle_text(w, replace_dict, all_caps, 0)
            if w:
                processed_words.append((w, w_info['start'], w_info['end']))

        if not processed_words:
            continue

        if max_words_per_line > 0:
            line_sets = [processed_words[i:i+max_words_per_line] for i in range(0, len(processed_words), max_words_per_line)]
        else:
            line_sets = [processed_words]

        for line_set in line_sets:
            for idx, (word, w_start, w_end) in enumerate(line_set):
                underlined_lines = []
                line_words = []
                for w_idx, (w_text, _, _) in enumerate(line_set):
                    if w_idx == idx:
                        line_words.append(f"{{\\u1}}{w_text}{{\\u0}}")
                    else:
                        line_words.append(w_text)
                underlined_lines.append(' '.join(line_words))
                full_text = '\\N'.join(underlined_lines)

                if use_pos:
                    position_tag = f"{{\\an{an_code}\\pos({x},{y})}}"
                else:
                    position_tag = f"{{\\an{an_code}}}"

                start_time = format_ass_time(w_start)
                end_time = format_ass_time(w_end)
                events.append(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{position_tag}{{\\c{line_color}}}{full_text}")
    return "\n".join(events)

def handle_word_by_word(transcription_result, style_options, replace_dict, video_resolution):
    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)
    if style_options['font_size'] is None:
        style_options['font_size'] = int(video_resolution[1] * 0.05)
    font_size = style_options['font_size']

    position_str = style_options.get('position', 'middle_center')
    alignment_str = style_options.get('alignment', None)
    x = style_options.get('x')
    y = style_options.get('y')

    logger.info(f"[Word-by-Word] position={position_str}, alignment={alignment_str}, x={x}, y={y}")
    an_code, use_pos = determine_alignment_code(position_str, alignment_str, x, y)
    logger.info(f"[Word-by-Word] an_code={an_code}, use_pos={use_pos}")

    line_color = rgb_to_ass_color(style_options.get('line_color', '#FFFFFF'))
    word_color = rgb_to_ass_color(style_options.get('word_color', '#FFFF00'))
    line_height = int(font_size * 1.2)
    events = []

    for segment in transcription_result['segments']:
        words = segment.get('words', [])
        if not words:
            continue

        if max_words_per_line > 0:
            grouped_words = [words[i:i+max_words_per_line] for i in range(0, len(words), max_words_per_line)]
        else:
            grouped_words = [words]

        for line_num, word_group in enumerate(grouped_words):
            for w_info in word_group:
                w = w_info.get('word', '').strip().replace('\n', ' ')
                if not w:
                    continue
                w = process_subtitle_text(w, replace_dict, all_caps, 0)
                start_time = format_ass_time(w_info['start'])
                end_time = format_ass_time(w_info['end'])

                if use_pos:
                    y_coord = y + (line_num * line_height) if y is not None else (line_num * line_height)
                    position_tag = f"{{\\an{an_code}\\pos({x},{y_coord})}}"
                else:
                    position_tag = f"{{\\an{an_code}}}"

                events.append(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{position_tag}{{\\c{word_color}}}{w}")
    return "\n".join(events)

STYLE_HANDLERS = {
    'classic': handle_classic,
    'karaoke': handle_karaoke,
    'highlight': handle_highlight,
    'underline': handle_underline,
    'word_by_word': handle_word_by_word
}

def srt_to_ass(transcription_result, style_type, settings, replace_dict, video_resolution):
    """
    Convert transcription result to ASS format based on specified style type.
    """
    default_style_settings = {
        'line_color': '#FFFFFF',
        'word_color': '#FFFF00',
        'box_color': '#000000',
        'outline_color': '#000000',
        'all_caps': False,
        'max_words_per_line': 0,
        'font_size': None,
        'font_family': 'Arial',
        'bold': False,
        'italic': False,
        'underline': False,
        'strikeout': False,
        'outline_width': 2,
        'shadow_offset': 0,
        'border_style': 1,
        'x': None,
        'y': None,
        'position': 'middle_center',
        'alignment': None
    }
    style_options = {**default_style_settings, **settings}

    # Ensure font_size is numeric if None
    if style_options['font_size'] is None:
        style_options['font_size'] = int(video_resolution[1] * 0.05)

    ass_header = generate_ass_header(style_options, video_resolution)
    if isinstance(ass_header, dict) and 'error' in ass_header:
        return ass_header

    handler = STYLE_HANDLERS.get(style_type.lower())
    if not handler:
        logger.warning(f"Unknown style '{style_type}'. Defaulting to 'classic'.")
        handler = handle_classic

    dialogue_lines = handler(transcription_result, style_options, replace_dict, video_resolution)

    return ass_header + dialogue_lines + "\n"

def process_subtitle_events(transcription_result, style_type, settings, replace_dict, video_resolution):
    return srt_to_ass(transcription_result, style_type, settings, replace_dict, video_resolution)

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
            style_options['word_color'] = style_options.pop('highlight_color')

        # Early Font Availability Check
        font_family = style_options.get('font_family', 'Arial')
        available_fonts = get_available_fonts()
        if font_family not in available_fonts:
            logger.warning(f"Font '{font_family}' not found. Available fonts: {', '.join(available_fonts)}")
            return {'error': f"Font '{font_family}' not available.", 'available_fonts': available_fonts}

        logger.info(f"Job {job_id}: Font '{font_family}' is available.")

        # Proceed with downloading and processing the video
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
            return {"error": f"FFmpeg error: {stderr_output}"}

        return output_path

    except Exception as e:
        logger.error(f"Job {job_id}: Error in process_captioning_v1: {str(e)}")
        return {"error": str(e)}
