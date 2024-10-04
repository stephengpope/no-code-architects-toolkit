import os
import ffmpeg
import logging
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from services.file_management import download_file

# Set the default local storage directory
STORAGE_PATH = "/tmp/"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the font paths
FONT_PATHS = {
    'Arial': '/usr/share/fonts/truetype/custom/Arial.ttf',
    'Libre Baskerville': '/usr/share/fonts/truetype/custom/LibreBaskerville-Regular.ttf',
    'Lobster': '/usr/share/fonts/truetype/custom/Lobster-Regular.ttf',
    'Luckiest Guy': '/usr/share/fonts/truetype/custom/LuckiestGuy-Regular.ttf',
    'Nanum Pen Script': '/usr/share/fonts/truetype/custom/NanumPenScript-Regular.ttf',
    'Nunito': '/usr/share/fonts/truetype/custom/Nunito-Regular.ttf',
    'Pacifico': '/usr/share/fonts/truetype/custom/Pacifico-Regular.ttf',
    'Roboto': '/usr/share/fonts/truetype/custom/Roboto-Regular.ttf',
    'Comic Neue': '/usr/share/fonts/truetype/custom/ComicNeue-Regular.ttf',
    'Oswald': '/usr/share/fonts/truetype/custom/Oswald-Regular.ttf',
    'Oswald Bold': '/usr/share/fonts/truetype/custom/Oswald-Bold.ttf',
    'Shrikhand': '/usr/share/fonts/truetype/custom/Shrikhand-Regular.ttf',
    'Fredericka the Great': '/usr/share/fonts/truetype/custom/FrederickatheGreat-Regular.ttf',
    'Permanent Marker': '/usr/share/fonts/truetype/custom/PermanentMarker-Regular.ttf',
    'Simplified Chinese': '/usr/share/fonts/truetype/custom/SimplifiedChinese.ttf',
    'Traditional Chinese': '/usr/share/fonts/truetype/custom/TraditionalChinese.ttf',
    'Japanese': '/usr/share/fonts/truetype/custom/Japanese.ttf',
    'Korean': '/usr/share/fonts/truetype/custom/Korean.ttf',
    'Korean Bold': '/usr/share/fonts/truetype/custom/Korean-Bold.ttf'
}

def process_captioning(file_url, caption_srt, caption_type, options, job_id):
    """Process video captioning using FFmpeg."""
    try:
        logger.info(f"Job {job_id}: Starting download of file from {file_url}")
        video_path = download_file(file_url, STORAGE_PATH)
        logger.info(f"Job {job_id}: File downloaded to {video_path}")

        subtitle_extension = '.' + caption_type
        srt_path = os.path.join(STORAGE_PATH, f"{job_id}{subtitle_extension}")
        options = convert_array_to_collection(options)
        caption_style = ""

        if caption_type == 'ass':
            style_string = generate_style_line(options)
            caption_style = f"""
[Script Info]
Title: Highlight Current Word
ScriptType: v4.00+
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{style_string}
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        if caption_srt.startswith("https"):
            # Download the file if caption_srt is a URL
            logger.info(f"Job {job_id}: Downloading caption file from {caption_srt}")
            response = requests.get(caption_srt)
            response.raise_for_status()  # Raise an exception for bad status codes
            if caption_type in ['srt','vtt']:
                with open(srt_path, 'wb') as srt_file:
                    srt_file.write(response.content)
            else:
                subtitle_content = caption_style + response.text
                with open(srt_path, 'w') as srt_file:
                    srt_file.write(subtitle_content)
            
            logger.info(f"Job {job_id}: Caption file downloaded to {srt_path}")
        else:
            # Write caption_srt content directly to file
            subtitle_content = caption_style + caption_srt
            with open(srt_path, 'w') as srt_file:
                srt_file.write(subtitle_content)
        
        logger.info(f"Job {job_id}: SRT file created at {srt_path}")

        output_path = os.path.join(STORAGE_PATH, f"{job_id}_captioned.mp4")


        # Default FFmpeg options
        ffmpeg_options = {
            'font_name': None,
            'font_size': 12,
            'primary_color': None,
            'secondary_color': None,
            'outline_color': None,
            'back_color': None,
            'bold': None,
            'italic': None,
            'underline': None,
            'strikeout': None,
            'alignment': None,
            'margin_v': None,
            'margin_l': None,
            'margin_r': None,
            'outline': None,
            'shadow': None,
            'blur': None,
            'border_style': None,
            'encoding': None,
            'spacing': None,
            'angle': None,
            'uppercase': None
        }

        # Update ffmpeg_options with provided options
        ffmpeg_options.update(options)

        # For ASS subtitles, we should avoid overriding styles
        if subtitle_extension == '.ass':
            # Use the subtitles filter without force_style
            subtitle_filter = f"subtitles='{srt_path}'"
        else:
            # Construct FFmpeg filter options for subtitles with detailed styling
            subtitle_filter = f"subtitles={srt_path}:force_style='"
            style_options = {
                'FontFile': ffmpeg_options['font_name'],
                'FontSize': ffmpeg_options['font_size'],
                'PrimaryColour': ffmpeg_options['primary_color'],
                'SecondaryColour': ffmpeg_options['secondary_color'],
                'OutlineColour': ffmpeg_options['outline_color'],
                'BackColour': ffmpeg_options['back_color'],
                'Bold': ffmpeg_options['bold'],
                'Italic': ffmpeg_options['italic'],
                'Underline': ffmpeg_options['underline'],
                'StrikeOut': ffmpeg_options['strikeout'],
                'Alignment': ffmpeg_options['alignment'],
                'MarginV': ffmpeg_options['margin_v'],
                'MarginL': ffmpeg_options['margin_l'],
                'MarginR': ffmpeg_options['margin_r'],
                'Outline': ffmpeg_options['outline'],
                'Shadow': ffmpeg_options['shadow'],
                'Blur': ffmpeg_options['blur'],
                'BorderStyle': ffmpeg_options['border_style'],
                'Encoding': ffmpeg_options['encoding'],
                'Spacing': ffmpeg_options['spacing'],
                'Angle': ffmpeg_options['angle'],
                'UpperCase': ffmpeg_options['uppercase']
            }

            # Add only populated options to the subtitle filter
            subtitle_filter += ','.join(f"{k}={v}" for k, v in style_options.items() if v is not None)
            subtitle_filter += "'"

        try:
            # Log the FFmpeg command for debugging
            logger.info(f"Job {job_id}: Running FFmpeg with filter: {subtitle_filter}")

            # Run FFmpeg to add subtitles to the video
            ffmpeg.input(video_path).output(
                output_path,
                vf=subtitle_filter,
                acodec='copy',
            ).run()
            logger.info(f"Job {job_id}: FFmpeg processing completed, output file at {output_path}")
        except ffmpeg.Error as e:
            # Log the FFmpeg stderr output
            logger.error(f"Job {job_id}: FFmpeg error: {e.stderr.decode('utf8')}")
            raise

        # The upload process will be handled by the calling function
        return output_path

        # Clean up local files
        os.remove(video_path)
        os.remove(srt_path)
        os.remove(output_path)
        logger.info(f"Job {job_id}: Local files cleaned up")
    except Exception as e:
        logger.error(f"Job {job_id}: Error in process_captioning: {str(e)}")
        raise

def convert_array_to_collection(options):
    return {item["option"]: item["value"] for item in options}

def parse_format_line(format_line):
    # Remove 'Format: ' prefix and split by ', '
    fields = format_line.replace('Format: ', '').split(', ')
    return fields

def parse_style_line(style_line):
    # Remove 'Style: ' prefix and split by ', '
    values = style_line.replace('Style: ', '').split(', ')
    return values

def generate_style_line(option_dict):
    # The default Format and Style lines
    format_line = 'Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding'
    style_line = 'Style: Default, Arial Black, 32, &H00FFFFFF, &H00000000, &H64000000, 1, 0, 0, 0, 100, 100, 0, 0, 1, 2, 1, 2, 10, 10, 30, 1'

    # Parse the format line and style line
    fields = parse_format_line(format_line)
    values = parse_style_line(style_line)
    default_style = dict(zip(fields, values))

    # Mapping from API option names to style field names
    api_to_style_field_map = {
        "font_name": "Fontname",
        "font_size": "Fontsize",
        "primary_colour": "PrimaryColour",
        "outline_colour": "OutlineColour",
        "back_colour": "BackColour",
        "bold": "Bold",
        "italic": "Italic",
        "underline": "Underline",
        "strikeout": "StrikeOut",
        "scalex": "ScaleX",
        "scaley": "ScaleY",
        "spacing": "Spacing",
        "angle": "Angle",
        "border_style": "BorderStyle",
        "outline": "Outline",
        "shadow": "Shadow",
        "alignment": "Alignment",
        "margin_l": "MarginL",
        "margin_r": "MarginR",
        "margin_v": "MarginV",
        "encoding": "Encoding"
    }

    # Override default style with options provided
    for api_option_name, option_value in option_dict.items():
        field_name = api_to_style_field_map.get(api_option_name)
        if field_name:
            default_style[field_name] = str(option_value)
        else:
            # Option not recognized, could log or ignore
            pass

    # Reconstruct the style line with updated values
    updated_values = [default_style[field] for field in fields]
    updated_style_line = 'Style: ' + ', '.join(updated_values)
    return updated_style_line
