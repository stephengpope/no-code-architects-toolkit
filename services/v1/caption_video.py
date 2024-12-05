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

def bgr_to_rgb(color):
    """Convert BGR color format to RGB."""
    if isinstance(color, str):
        # Remove '&H' prefix and '&' suffix if present
        color = color.replace('&H', '').replace('&', '')
        try:
            # Parse the hex value
            bgr = int(color, 16)
            b = (bgr >> 16) & 0xFF
            g = (bgr >> 8) & 0xFF
            r = bgr & 0xFF
            return f"&H{r:02X}{g:02X}{b:02X}&"
        except ValueError:
            # Return default white color if parsing fails
            return "&HFFFFFF&"
    return color

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

def srt_to_ass(srt_content, options=None, gap_time=0.01):
    """Convert SRT content to ASS format with truncated time precision."""
    if options is None:
        options = []

    # Helper function to format time
    def format_ass_time(time_obj):
        """Format datetime.timedelta for ASS time (hh:mm:ss.sss) with three decimal places."""
        total_seconds = int(time_obj.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        milliseconds = int(time_obj.microseconds / 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

    # Generate ASS header with style
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 384
PlayResY: 288
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""
    # Convert options array to dictionary
    style_options = {opt["option"]: opt["value"] for opt in options}
    
    # Generate style line with default colors
    style_line = "Style: Default"
    style_line += f",{style_options.get('font_name', 'Arial')}"
    style_line += f",{style_options.get('font_size', '20')}"
    style_line += f",&HFFFFFF&"  # Primary color (white)
    style_line += f",&H000000&"  # Secondary color (black)
    style_line += f",&H000000&"  # Outline color (black)
    style_line += f",&H000000&"  # Back color (black)
    style_line += f",{style_options.get('bold', '0')}"
    style_line += f",{style_options.get('italic', '0')}"
    style_line += f",{style_options.get('underline', '0')}"
    style_line += f",{style_options.get('strikeout', '0')}"
    style_line += f",{style_options.get('scale_x', '100')}"
    style_line += f",{style_options.get('scale_y', '100')}"
    style_line += f",{style_options.get('spacing', '0')}"
    style_line += f",{style_options.get('angle', '0')}"
    style_line += f",{style_options.get('border_style', '1')}"
    style_line += f",{style_options.get('outline', '2')}"
    style_line += f",{style_options.get('shadow', '0')}"
    style_line += f",{style_options.get('alignment', '2')}"
    style_line += f",{style_options.get('margin_l', '20')}"
    style_line += f",{style_options.get('margin_r', '20')}"
    style_line += f",{style_options.get('margin_v', '20')}"
    style_line += ",1"

    ass_content = ass_header + style_line + "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"

    # Convert SRT subtitles to ASS events
    try:
        srt_parsed = list(srt.parse(srt_content))
    except Exception as e:
        raise ValueError(f"Error parsing SRT content: {e}")

    for i, sub in enumerate(srt_parsed):
        start = format_ass_time(sub.start)
        end = format_ass_time(sub.end)

        # Add a gap of 0.1 seconds if this is not the last subtitle
        if i < len(srt_parsed) - 1:
            next_start = srt_parsed[i + 1].start
            if sub.end > next_start:
                end_time = min(sub.end - timedelta(milliseconds=100), next_start)
            else:
                end_time = sub.end
            end = format_ass_time(end_time)
        
        text = sub.content.replace('\n', '\\N')
        ass_content += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n"

    return ass_content

def process_captioning_v1(video_url, caption_srt, caption_ass, options, job_id):
    """Enhanced v1 captioning process with transcription fallback."""
    try:
        # Download video
        video_path = download_file(video_url, STORAGE_PATH)
        logger.info(f"Job {job_id}: Video downloaded to {video_path}")

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
            subtitle_content = srt_to_ass(subtitle_content, options)
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

        # Clean up temporary files
        # os.remove(video_path)
        # os.remove(subtitle_path)

        return output_path

    except Exception as e:
        logger.error(f"Job {job_id}: Error in process_captioning_v1: {str(e)}")
        raise