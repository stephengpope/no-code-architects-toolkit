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
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

STORAGE_PATH = "/tmp/"

# Mapping of position strings to ASS alignment numbers
# Note: We will always use \an5 now, so this map is only used for reference if needed.
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
    """Convert an RGB hex string to ASS color format (&HAABBGGRR)."""
    if isinstance(rgb_color, str):
        rgb_color = rgb_color.lstrip('#')
        if len(rgb_color) == 6:
            r = int(rgb_color[0:2], 16)
            g = int(rgb_color[2:4], 16)
            b = int(rgb_color[4:6], 16)
            return f"&H00{b:02X}{g:02X}{r:02X}"
    return "&H00FFFFFF"

def generate_transcription(video_path, language='auto'):
    """
    Generate a transcription with word-level timestamps using Whisper.
    If language != 'auto', forces a language. Otherwise detects automatically.
    """
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
    """Use ffprobe to determine the video's resolution."""
    try:
        probe = ffmpeg.probe(video_path)
        video_streams = [s for s in probe['streams'] if s['codec_type'] == 'video']
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
    """Get the list of available fonts on the system."""
    try:
        import matplotlib.font_manager as fm
    except ImportError:
        logger.error("matplotlib not installed. Please install via 'pip install matplotlib'.")
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
    """Convert float seconds to ASS time format H:MM:SS.cc"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centiseconds = int(round((seconds - int(seconds)) * 100))
    return f"{hours}:{minutes:02}:{secs:02}.{centiseconds:02}"

def calculate_position(position, video_width, video_height, x=None, y=None):
    """
    Deprecated in our new approach. Now we use determine_default_xy_for_position() instead.
    Keeping for reference. 
    """
    if x is not None and y is not None:
        logger.info(f"Using custom coordinates: x={x}, y={y}")
        return int(x), int(y)
    return video_width // 2, video_height // 2

def process_subtitle_text(text, replace_dict, all_caps, max_words_per_line):
    """Apply text transformations: replacements, all caps, and optional line splitting."""
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
    """Convert SRT content into a transcription-like structure for uniform processing."""
    subtitles = list(srt.parse(srt_content))
    segments = []
    for sub in subtitles:
        segments.append({
            'start': sub.start.total_seconds(),
            'end': sub.end.total_seconds(),
            'text': sub.content.strip(),
            'words': []
        })
    return {'segments': segments}

def split_lines(text, max_words_per_line):
    """
    Split text into multiple lines if max_words_per_line > 0.
    Otherwise, return [text] as a single line.
    """
    if max_words_per_line <= 0:
        return [text]
    words = text.split()
    lines = [' '.join(words[i:i+max_words_per_line]) for i in range(0, len(words), max_words_per_line)]
    return lines

def determine_default_xy_for_position(position_str, video_width, video_height):
    """
    Given a position string and the video dimensions, compute a default (x,y) coordinate
    that places the text in the corresponding 1/3 region of the screen, centered in that cell.
    """
    vertical, horizontal = position_str.split('_')  # e.g. top_center -> ['top','center']

    # Y-coordinate based on vertical
    if vertical == 'top':
        y = video_height * (1/6)    # slightly down from top
    elif vertical == 'middle':
        y = video_height * (1/2)    # middle of screen
    else:  # bottom
        y = video_height * (5/6)    # slightly up from bottom

    # X-coordinate based on horizontal
    if horizontal == 'left':
        x = video_width * (1/6)
    elif horizontal == 'center':
        x = video_width * (1/2)
    else:  # right
        x = video_width * (5/6)

    return int(x), int(y)

def adjust_lines_for_alignment(lines, alignment):
    """
    Adjust the text lines so that when rendered with \an5 (center point),
    they appear left-, center-, or right-aligned relative to (x,y).
    - center: no change (already centered)
    - left:   no change or minimal, as \an5 center is a midpoint. 
              True left alignment is tricky without width info. We'll do no change.
    - right:  prepend spaces to push text to the right visually.
    """
    if alignment == 'right':
        # Add some leading spaces to simulate right alignment
        adjusted = ["    " + line for line in lines]
    else:
        # left or center: do nothing
        adjusted = lines
    return adjusted

def create_style_line(style_options, video_resolution):
    """
    Create the style line for ASS subtitles. We still define it fully,
    but remember we always use \an5 at the event level now.
    """
    font_family = style_options.get('font_family', 'Arial')
    available_fonts = get_available_fonts()
    if font_family not in available_fonts:
        logger.warning(f"Font '{font_family}' not found. Available fonts: {', '.join(available_fonts)}")
        return {'error': f"Font '{font_family}' not available.", 'available_fonts': available_fonts}

    line_color = rgb_to_ass_color(style_options.get('line_color', '#FFFFFF'))
    secondary_color = line_color
    outline_color = rgb_to_ass_color(style_options.get('outline_color', '#000000'))
    box_color = rgb_to_ass_color(style_options.get('box_color', '#000000'))

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

    # Note: We'll event-level override \an5 always, so style alignment is less relevant.
    # Just use middle_center=5 in style.
    alignment = 5

    style_line = (
        f"Style: Default,{font_family},{font_size},{line_color},{secondary_color},"
        f"{outline_color},{box_color},{bold},{italic},{underline},{strikeout},"
        f"{scale_x},{scale_y},{spacing},{angle},{border_style},{outline_width},"
        f"{shadow_offset},{alignment},{margin_l},{margin_r},{margin_v},0"
    )
    return style_line

def generate_ass_header(style_options, video_resolution):
    """
    Generate the ASS file header with the Default style.
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

### STYLE HANDLERS (all follow the same \an5 center approach and adjust_lines_for_alignment) ###

def handle_classic(transcription_result, style_options, replace_dict, video_resolution):
    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)
    if style_options['font_size'] is None:
        style_options['font_size'] = int(video_resolution[1] * 0.05)

    font_size = style_options['font_size']
    position_str = style_options.get('position', 'middle_center')
    alignment_str = style_options.get('alignment', 'center')
    x = style_options.get('x')
    y = style_options.get('y')

    # Determine (x,y)
    if x is None or y is None:
        x, y = determine_default_xy_for_position(position_str, video_resolution[0], video_resolution[1])

    logger.info(f"[Classic] position={position_str}, alignment={alignment_str}, x={x}, y={y}")

    # an_code=5 and use_pos=True for all styles now
    an_code = 5
    use_pos = True

    events = []
    for segment in transcription_result['segments']:
        text = segment['text'].strip().replace('\n', ' ')
        lines = split_lines(text, max_words_per_line)
        processed_lines = [process_subtitle_text(line, replace_dict, all_caps, 0) for line in lines]
        adjusted_lines = adjust_lines_for_alignment(processed_lines, alignment_str)
        final_text = '\\N'.join(adjusted_lines)
        start_time = format_ass_time(segment['start'])
        end_time = format_ass_time(segment['end'])
        position_tag = f"{{\\an{an_code}\\pos({x},{y})}}"
        events.append(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{position_tag}{final_text}")
    return "\n".join(events)

def handle_karaoke(transcription_result, style_options, replace_dict, video_resolution):
    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)
    if style_options['font_size'] is None:
        style_options['font_size'] = int(video_resolution[1] * 0.05)

    font_size = style_options['font_size']
    position_str = style_options.get('position', 'middle_center')
    alignment_str = style_options.get('alignment', 'center')
    x = style_options.get('x')
    y = style_options.get('y')

    # Determine (x,y)
    if x is None or y is None:
        x, y = determine_default_xy_for_position(position_str, video_resolution[0], video_resolution[1])

    logger.info(f"[Karaoke] position={position_str}, alignment={alignment_str}, x={x}, y={y}")

    an_code = 5
    use_pos = True
    word_color = rgb_to_ass_color(style_options.get('word_color', '#FFFF00'))
    events = []

    for segment in transcription_result['segments']:
        words = segment.get('words', [])
        if not words:
            continue

        # Build karaoke lines
        # Group words per line if max_words_per_line > 0
        if max_words_per_line > 0:
            lines_content = []
            current_line = []
            current_line_words = 0
            for w_info in words:
                w = w_info.get('word', '').strip().replace('\n', ' ')
                w = process_subtitle_text(w, replace_dict, all_caps, 0)
                duration_cs = int(round((w_info['end'] - w_info['start']) * 100))
                highlighted_word = f"{{\\k{duration_cs}}}{w} "
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
                w = w_info.get('word', '').strip().replace('\n', ' ')
                w = process_subtitle_text(w, replace_dict, all_caps, 0)
                duration_cs = int(round((w_info['end'] - w_info['start']) * 100))
                highlighted_word = f"{{\\k{duration_cs}}}{w} "
                line_content.append(highlighted_word)
            lines_content = [''.join(line_content).strip()]

        # Adjust lines for alignment
        adjusted_lines = adjust_lines_for_alignment(lines_content, alignment_str)
        dialogue_text = '\\N'.join(adjusted_lines)

        start_time = format_ass_time(words[0]['start'])
        end_time = format_ass_time(words[-1]['end'])
        position_tag = f"{{\\an{an_code}\\pos({x},{y})}}"
        events.append(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{position_tag}{{\\c{word_color}}}{dialogue_text}")
    return "\n".join(events)

def handle_highlight(transcription_result, style_options, replace_dict, video_resolution):
    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)
    if style_options['font_size'] is None:
        style_options['font_size'] = int(video_resolution[1] * 0.05)
    font_size = style_options['font_size']

    position_str = style_options.get('position', 'middle_center')
    alignment_str = style_options.get('alignment', 'center')
    x = style_options.get('x')
    y = style_options.get('y')

    if x is None or y is None:
        x, y = determine_default_xy_for_position(position_str, video_resolution[0], video_resolution[1])

    logger.info(f"[Highlight] position={position_str}, alignment={alignment_str}, x={x}, y={y}")

    an_code = 5
    use_pos = True
    word_color = rgb_to_ass_color(style_options.get('word_color', '#FFFF00'))
    line_color = rgb_to_ass_color(style_options.get('line_color', '#FFFFFF'))
    events = []

    # Highlight style shows each word highlighted in sequence
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

        # Split into lines if max_words_per_line > 0
        if max_words_per_line > 0:
            line_sets = [processed_words[i:i+max_words_per_line] for i in range(0, len(processed_words), max_words_per_line)]
        else:
            line_sets = [processed_words]

        # For each word, show a line with that word highlighted
        for line_set in line_sets:
            # line_set is a list of (word, start, end)
            # We highlight each word in turn
            for idx, (word, w_start, w_end) in enumerate(line_set):
                # Build line with one word highlighted
                line_words = []
                for w_idx, (w_text, _, _) in enumerate(line_set):
                    if w_idx == idx:
                        line_words.append(f"{{\\c{word_color}}}{w_text}{{\\c{line_color}}}")
                    else:
                        line_words.append(w_text)
                # Before joining, adjust alignment if needed
                # First join words into a single line
                single_line = ' '.join(line_words)
                adjusted_line = adjust_lines_for_alignment([single_line], alignment_str)
                full_text = '\\N'.join(adjusted_line)

                start_time = format_ass_time(w_start)
                end_time = format_ass_time(w_end)
                position_tag = f"{{\\an{an_code}\\pos({x},{y})}}"
                events.append(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{position_tag}{{\\c{line_color}}}{full_text}")
    return "\n".join(events)

def handle_underline(transcription_result, style_options, replace_dict, video_resolution):
    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)
    if style_options['font_size'] is None:
        style_options['font_size'] = int(video_resolution[1] * 0.05)
    font_size = style_options['font_size']

    position_str = style_options.get('position', 'middle_center')
    alignment_str = style_options.get('alignment', 'center')
    x = style_options.get('x')
    y = style_options.get('y')

    if x is None or y is None:
        x, y = determine_default_xy_for_position(position_str, video_resolution[0], video_resolution[1])

    logger.info(f"[Underline] position={position_str}, alignment={alignment_str}, x={x}, y={y}")

    an_code = 5
    use_pos = True
    line_color = rgb_to_ass_color(style_options.get('line_color', '#FFFFFF'))
    events = []

    # Underline style: each word is displayed, underlining the currently "active" word
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
                line_words = []
                for w_idx, (w_text, _, _) in enumerate(line_set):
                    if w_idx == idx:
                        line_words.append(f"{{\\u1}}{w_text}{{\\u0}}")
                    else:
                        line_words.append(w_text)
                single_line = ' '.join(line_words)
                adjusted_line = adjust_lines_for_alignment([single_line], alignment_str)
                full_text = '\\N'.join(adjusted_line)

                start_time = format_ass_time(w_start)
                end_time = format_ass_time(w_end)
                position_tag = f"{{\\an{an_code}\\pos({x},{y})}}"
                events.append(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{position_tag}{{\\c{line_color}}}{full_text}")
    return "\n".join(events)

def handle_word_by_word(transcription_result, style_options, replace_dict, video_resolution):
    max_words_per_line = int(style_options.get('max_words_per_line', 0))
    all_caps = style_options.get('all_caps', False)
    if style_options['font_size'] is None:
        style_options['font_size'] = int(video_resolution[1] * 0.05)
    font_size = style_options['font_size']

    position_str = style_options.get('position', 'middle_center')
    alignment_str = style_options.get('alignment', 'center')
    x = style_options.get('x')
    y = style_options.get('y')

    if x is None or y is None:
        x, y = determine_default_xy_for_position(position_str, video_resolution[0], video_resolution[1])

    logger.info(f"[Word-by-Word] position={position_str}, alignment={alignment_str}, x={x}, y={y}")

    an_code = 5
    use_pos = True
    line_color = rgb_to_ass_color(style_options.get('line_color', '#FFFFFF'))
    word_color = rgb_to_ass_color(style_options.get('word_color', '#FFFF00'))
    line_height = int(font_size * 1.2)
    events = []

    # Word-by-word: each word is shown individually
    for segment in transcription_result['segments']:
        words = segment.get('words', [])
        if not words:
            continue

        if max_words_per_line > 0:
            grouped_words = [words[i:i+max_words_per_line] for i in range(0, len(words), max_words_per_line)]
        else:
            grouped_words = [words]

        for line_num, word_group in enumerate(grouped_words):
            # Each word in this group appears individually
            for w_info in word_group:
                w = w_info.get('word', '').strip().replace('\n', ' ')
                if not w:
                    continue
                w = process_subtitle_text(w, replace_dict, all_caps, 0)
                # Here we have just one line with one word
                adjusted_line = adjust_lines_for_alignment([w], alignment_str)
                final_text = '\\N'.join(adjusted_line)

                start_time = format_ass_time(w_info['start'])
                end_time = format_ass_time(w_info['end'])
                position_tag = f"{{\\an{an_code}\\pos({x},{y})}}"
                events.append(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{position_tag}{{\\c{word_color}}}{final_text}")
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
    Convert transcription result to ASS based on the specified style.
    Uses the updated logic where (x,y) is center and \an5 is used universally.
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
        'alignment': 'center'  # default alignment center if not provided
    }
    style_options = {**default_style_settings, **settings}

    if style_options['font_size'] is None:
        style_options['font_size'] = int(video_resolution[1] * 0.05)

    ass_header = generate_ass_header(style_options, video_resolution)
    if isinstance(ass_header, dict) and 'error' in ass_header:
        return ass_header

    handler = STYLE_HANDLERS.get(style_type.lower())
    if not handler:
        logger.warning(f"Unknown style '{style_type}', defaulting to 'classic'.")
        handler = handle_classic

    dialogue_lines = handler(transcription_result, style_options, replace_dict, video_resolution)
    return ass_header + dialogue_lines + "\n"

def process_subtitle_events(transcription_result, style_type, settings, replace_dict, video_resolution):
    return srt_to_ass(transcription_result, style_type, settings, replace_dict, video_resolution)

def process_captioning_v1(video_url, captions, settings, replace, job_id, language='auto'):
    """
    Captioning process with transcription fallback and multiple styles.
    Integrates with the updated logic for positioning and alignment.
    """
    try:
        if not isinstance(settings, dict):
            logger.error(f"Job {job_id}: 'settings' should be a dictionary.")
            return {"error": "'settings' should be a dictionary."}

        # Normalize keys
        style_options = {k.replace('-', '_'): v for k, v in settings.items()}

        if not isinstance(replace, list):
            logger.error(f"Job {job_id}: 'replace' should be a list.")
            return {"error": "'replace' should be a list of objects with 'find' and 'replace' keys."}

        replace_dict = {}
        for item in replace:
            if 'find' in item and 'replace' in item:
                replace_dict[item['find']] = item['replace']
            else:
                logger.warning(f"Job {job_id}: Invalid replace item {item}. Skipping.")

        if 'highlight_color' in style_options:
            logger.warning(f"Job {job_id}: 'highlight_color' deprecated, merging into 'word_color'.")
            style_options['word_color'] = style_options.pop('highlight_color')

        font_family = style_options.get('font_family', 'Arial')
        available_fonts = get_available_fonts()
        if font_family not in available_fonts:
            logger.warning(f"Font '{font_family}' not found.")
            return {'error': f"Font '{font_family}' not available.", 'available_fonts': available_fonts}

        logger.info(f"Job {job_id}: Font '{font_family}' is available.")
        video_path = download_file(video_url, STORAGE_PATH)
        logger.info(f"Job {job_id}: Video downloaded to {video_path}")

        video_resolution = get_video_resolution(video_path)
        logger.info(f"Job {job_id}: Video resolution = {video_resolution[0]}x{video_resolution[1]}")

        style_type = style_options.get('style', 'classic').lower()

        if captions:
            if '[Script Info]' in captions:
                subtitle_content = captions
                subtitle_type = 'ass'
            else:
                transcription_result = srt_to_transcription_result(captions)
                subtitle_content = process_subtitle_events(transcription_result, style_type, style_options, replace_dict, video_resolution)
                subtitle_type = 'ass'
        else:
            logger.info(f"Job {job_id}: No captions provided, generating transcription.")
            transcription_result = generate_transcription(video_path, language=language)
            subtitle_content = process_subtitle_events(transcription_result, style_type, style_options, replace_dict, video_resolution)
            subtitle_type = 'ass'

        if isinstance(subtitle_content, dict) and 'error' in subtitle_content:
            logger.error(f"Job {job_id}: {subtitle_content['error']}")
            available_fonts = subtitle_content.get('available_fonts', [])
            error_message = subtitle_content.get('error', 'Unknown font error.')
            return {"error": error_message, "available_fonts": available_fonts}

        subtitle_filename = f"{job_id}.{subtitle_type}"
        subtitle_path = os.path.join(STORAGE_PATH, subtitle_filename)
        with open(subtitle_path, 'w', encoding='utf-8') as f:
            f.write(subtitle_content)
        logger.info(f"Job {job_id}: Subtitle file saved to {subtitle_path}")

        output_filename = f"{job_id}_captioned.mp4"
        output_path = os.path.join(STORAGE_PATH, output_filename)

        try:
            ffmpeg.input(video_path).output(
                output_path,
                vf=f"subtitles='{subtitle_path}'",
                acodec='copy'
            ).run(overwrite_output=True)
            logger.info(f"Job {job_id}: FFmpeg done. Output: {output_path}")
        except ffmpeg.Error as e:
            stderr_output = e.stderr.decode('utf8') if e.stderr else 'Unknown error'
            logger.error(f"Job {job_id}: FFmpeg error: {stderr_output}")
            return {"error": f"FFmpeg error: {stderr_output}"}

        return output_path

    except Exception as e:
        logger.error(f"Job {job_id}: Error in process_captioning_v1: {str(e)}", exc_info=True)
        return {"error": str(e)}
