import os
import ffmpeg
import logging
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from services.file_management import download_file
from services.gcp_toolkit import upload_to_gcs, GCP_BUCKET_NAME

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

def process_captioning(file_url, caption_srt, options, job_id):
    """Process video captioning using FFmpeg."""
    try:
        logger.info(f"Job {job_id}: Starting download of file from {file_url}")
        video_path = download_file(file_url, STORAGE_PATH)
        logger.info(f"Job {job_id}: File downloaded to {video_path}")

        srt_path = os.path.join(STORAGE_PATH, f"{job_id}.srt")
        with open(srt_path, 'w') as srt_file:
            srt_file.write(caption_srt)
        logger.info(f"Job {job_id}: SRT file created at {srt_path}")

        output_path = os.path.join(STORAGE_PATH, f"{job_id}_captioned.mp4")

        # Default FFmpeg options
        ffmpeg_options = {
            'font_name': 'Arial',
            'font_size': 12,
            'primary_color': 'white',
            'secondary_color': 'yellow',
            'outline_color': 'black',
            'back_color': 'black',
            'bold': False,
            'italic': False,
            'underline': False,
            'strikeout': False,
            'alignment': 2,
            'margin_v': 10,
            'margin_l': 10,
            'margin_r': 10,
            'outline': 2,
            'shadow': 0,
            'blur': 0,
            'background_opacity': 0.5,
            'border_style': 1,
            'encoding': 1,
            'scale_x': 100,
            'scale_y': 100,
            'spacing': 0,
            'angle': 0,
            'uppercase': False
        }

        # Update options with user-provided values
        ffmpeg_options.update(options)

        # Get the font file path
        font_file = FONT_PATHS.get(ffmpeg_options['font_name'], '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')

        # Extract video details (dimensions)
        probe = ffmpeg.probe(video_path)
        video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
        width = video_info['width']
        height = video_info['height']

        # Construct FFmpeg filter options for subtitles with a simplified filter
        subtitle_filter = (
            f"subtitles={srt_path}:force_style='FontFile={font_file},"
            f"FontSize={ffmpeg_options['font_size']}'"
        )

        try:
            # Log the FFmpeg command for debugging
            logger.info(f"Job {job_id}: Running FFmpeg with filter: {subtitle_filter}")

            # Run FFmpeg to add subtitles to the video
            ffmpeg.input(video_path).output(
                output_path,
                vf=subtitle_filter,
                vcodec='libx264',
                acodec='aac',
                strict='experimental',
                video_bitrate='3000k',
                audio_bitrate='128k',
                format='mp4',
                pix_fmt='yuv420p',
                movflags='faststart',
                s=f"{width}x{height}"
            ).run(capture_stdout=True, capture_stderr=True)
            logger.info(f"Job {job_id}: FFmpeg processing completed, output file at {output_path}")
        except ffmpeg.Error as e:
            # Log the FFmpeg stderr output
            logger.error(f"Job {job_id}: FFmpeg error: {e.stderr.decode('utf8')}")
            raise

        # Upload the output video to GCP Storage
        output_filename = upload_to_gcs(output_path, GCP_BUCKET_NAME)
        logger.info(f"Job {job_id}: File uploaded to GCS at {output_filename}")

        # Clean up local files
        os.remove(video_path)
        os.remove(srt_path)
        os.remove(output_path)
        logger.info(f"Job {job_id}: Local files cleaned up")

        return output_filename

    except Exception as e:
        logger.error(f"Job {job_id}: Error in process_captioning: {str(e)}")
        raise

def download_file(file_url, storage_path):
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    if 'drive.google.com' in file_url:
        file_id = extract_drive_id(file_url)
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = session.get(download_url, stream=True)
    else:
        response = session.get(file_url, stream=True)

    response.raise_for_status()

    filename = os.path.join(storage_path, file_url.split('/')[-1])
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return filename

def extract_drive_id(file_url):
    """
    Extract the file ID from a Google Drive URL.
    """
    if 'id=' in file_url:
        return file_url.split('id=')[1].split('&')[0]
    elif '/d/' in file_url:
        return file_url.split('/d/')[1].split('/')[0]
    else:
        raise ValueError("Invalid URL: 'id' parameter not found in the URL")