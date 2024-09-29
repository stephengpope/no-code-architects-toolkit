import os
import subprocess
import logging
from services.file_management import download_file
from PIL import Image

STORAGE_PATH = "/tmp/"
logger = logging.getLogger(__name__)

def process_image_to_video(image_url, length, frames, zoom, job_id, webhook_url=None):
    try:
        # Download the image file
        image_path = download_file(image_url, STORAGE_PATH)
        logger.info(f"Downloaded image to {image_path}")

        # Get image dimensions using Pillow
        with Image.open(image_path) as img:
            width, height = img.size
        logger.info(f"Original image dimensions: {width}x{height}")

        # Prepare the output path
        output_path = os.path.join(STORAGE_PATH, f"{job_id}.mp4")

        if width > height:
            scale_dims = "7680:4320"
            output_dims = "1920x1080"
            zoom_speed = zoom
        else:
            scale_dims = "4320:7680"
            output_dims = "1080x1920"
            zoom_speed = zoom * (9/16)

        # Prepare FFmpeg command
        cmd = [
            'ffmpeg', '-loop', '1', '-i', image_path,
            '-vf', f"scale={scale_dims},zoompan=z='min(zoom+{zoom},1.5)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={output_dims}",
            '-c:v', 'libx264', '-t', str(length), '-pix_fmt', 'yuv420p', output_path
        ]

        logger.info(f"Running FFmpeg command: {' '.join(cmd)}")

        # Run FFmpeg command
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"FFmpeg command failed. Error: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)

        logger.info(f"Video created successfully: {output_path}")

        # Clean up input file
        os.remove(image_path)

        return output_path
    except Exception as e:
        logger.error(f"Error in process_image_to_video: {str(e)}", exc_info=True)
        raise