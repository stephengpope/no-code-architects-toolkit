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

def generate_transcription(video_path):
    """Generate transcription from video file."""
    try:
        model = whisper.load_model("base")
        result = model.transcribe(video_path)
        
        # Convert to SRT format
        srt_subtitles = []
        for i, segment in enumerate(result['segments'], start=1):
            start = timedelta(seconds=segment['start'])
            end = timedelta(seconds=segment['end'])
            text = segment['text'].strip()
            srt_subtitles.append(srt.Subtitle(i, start, end, text))
        
        return srt.compose(srt_subtitles)
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

def srt_to_ass(srt_content, options=None, gap_time=0.01, video_resolution=(384, 288)):
    """Convert SRT content to ASS format with proper time formatting."""
    if options is None:
        options = []

    # Helper function to format time
    def format_ass_time(time_obj):
        """Format datetime.timedelta for ASS time (H:MM:SS.cs) with centiseconds."""
        total_seconds = time_obj.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        centiseconds = int((total_seconds - int(total_seconds)) * 100)
        return f"{hours}:{minutes:02}:{seconds:02}.{centiseconds:02}"

    # Generate ASS header with style
    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_resolution[0]}
PlayResY: {video_resolution[1]}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""

    # Convert options array to dictionary
    style_options = {opt["option"]: opt["value"] for opt in options}
    
    # Handle font availability
    font_name = style_options.get('font_name', 'Arial')
    available_fonts = get_available_fonts()
    if font_name not in available_fonts:
        logger.warning(f"Font '{font_name}' not found. Available fonts are: {', '.join(available_fonts)}")
        # Return the list of available fonts
        return {'error': f"Font '{font_name}' not available.", 'available_fonts': available_fonts}
    
    # Convert colors from RGB to ASS color format (&HAABBGGRR)
    primary_colour = rgb_to_ass_color(style_options.get('primary_colour', '#FFFFFF'))
    secondary_colour = rgb_to_ass_color(style_options.get('secondary_colour', '#000000'))
    outline_colour = rgb_to_ass_color(style_options.get('outline_colour', '#000000'))
    back_colour = rgb_to_ass_color(style_options.get('back_colour', '#000000'))
    
    # Generate style line with updated color codes and encoding
    style_line = "Style: Default"
    style_line += f",{font_name}"  # Fontname
    style_line += f",{style_options.get('font_size', '20')}"  # Fontsize
    style_line += f",{primary_colour}"  # PrimaryColour
    style_line += f",{secondary_colour}"  # SecondaryColour
    style_line += f",{outline_colour}"  # OutlineColour
    style_line += f",{back_colour}"  # BackColour
    style_line += f",{style_options.get('bold', '0')}"  # Bold
    style_line += f",{style_options.get('italic', '0')}"  # Italic
    style_line += f",{style_options.get('underline', '0')}"  # Underline
    style_line += f",{style_options.get('strikeout', '0')}"  # StrikeOut
    style_line += f",{style_options.get('scale_x', '100')}"  # ScaleX
    style_line += f",{style_options.get('scale_y', '100')}"  # ScaleY
    style_line += f",{style_options.get('spacing', '0')}"  # Spacing
    style_line += f",{style_options.get('angle', '0')}"  # Angle
    style_line += f",{style_options.get('border_style', '1')}"  # BorderStyle
    style_line += f",{style_options.get('outline', '2')}"  # Outline
    style_line += f",{style_options.get('shadow', '0')}"  # Shadow
    style_line += f",{style_options.get('alignment', '2')}"  # Alignment
    style_line += f",{style_options.get('margin_l', '20')}"  # MarginL
    style_line += f",{style_options.get('margin_r', '20')}"  # MarginR
    style_line += f",{style_options.get('margin_v', '20')}"  # MarginV
    style_line += ",0"  # Encoding set to 0 (ANSI)

    ass_content = ass_header + style_line + "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"

    # Convert SRT subtitles to ASS events
    try:
        srt_parsed = list(srt.parse(srt_content))
    except Exception as e:
        raise ValueError(f"Error parsing SRT content: {e}")

    for i, sub in enumerate(srt_parsed):
        start = format_ass_time(sub.start)
        end = format_ass_time(sub.end)

        # Adjust end time if it overlaps with the next subtitle's start time
        if i < len(srt_parsed) - 1:
            next_start_time = srt_parsed[i + 1].start
            if sub.end > next_start_time - timedelta(seconds=gap_time):
                sub.end = next_start_time - timedelta(seconds=gap_time)
                if sub.end < sub.start:
                    sub.end = sub.start
                end = format_ass_time(sub.end)

        text = sub.content.replace('\n', '\\N')
        ass_content += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n"

    return ass_content

def process_captioning_v1(video_url, caption_srt, caption_ass, options, job_id):
    """Enhanced v1 captioning process with transcription fallback."""
    try:
        # Download video
        video_path = download_file(video_url, STORAGE_PATH)
        logger.info(f"Job {job_id}: Video downloaded to {video_path}")

        # Get video resolution
        video_resolution = get_video_resolution(video_path)
        logger.info(f"Job {job_id}: Video resolution detected as {video_resolution[0]}x{video_resolution[1]}")

        # Determine subtitle content and type
        if caption_ass:
            subtitle_content = caption_ass
            subtitle_type = 'ass'
        elif caption_srt:
            subtitle_content = caption_srt
            subtitle_type = 'srt'
        else:
            # Generate transcription if no subtitles provided
            logger.info(f"Job {job_id}: No subtitles provided, generating transcription")
            subtitle_content = generate_transcription(video_path)
            subtitle_type = 'srt'

        # Convert SRT to ASS if needed
        if subtitle_type == 'srt':
            logger.info(f"Job {job_id}: Converting SRT to ASS format")
            result = srt_to_ass(subtitle_content, options, video_resolution=video_resolution)
            if isinstance(result, dict) and 'error' in result:
                # Font not available, return the list of available fonts
                logger.error(f"Job {job_id}: {result['error']}")
                return result
            else:
                subtitle_content = result
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
