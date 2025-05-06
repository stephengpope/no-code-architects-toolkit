# Copyright (c) 2025 Stephen G. Pope
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os
import subprocess
import logging
import re
from services.file_management import download_file
from services.cloud_storage import upload_file
from config import LOCAL_STORAGE_PATH

logger = logging.getLogger(__name__)

def is_youtube_url(url):
    """Check if the URL is a YouTube URL."""
    # Explicitly double backslashes for escapes in regex
    youtube_regex = (
        r'(https?://)?(www\.)?' # Optional http/https and www.
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/' # Domain
        r'(watch\?v=|embed/|v/|.+\?v=|live/)?' # Optional path parts
        r'([^&=%\?]{11})' # Video ID (11 chars excluding & = % ?)
    )
    return re.match(youtube_regex, url) is not None

def download_youtube_video(url, output_template, job_id):
    """Downloads video (no audio) from YouTube using yt-dlp."""
    output_path = output_template.format(job_id=job_id, timestamp="video", ext="mp4") # Predictable name
    # -f 'bv*[ext=mp4]': best video-only stream with mp4 extension
    # --no-audio: Explicitly try to avoid audio download/muxing if separate
    # Using a temporary template first to get the final name
    temp_output_template = os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_temp.%(ext)s")
    final_output_path = os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_video.mp4")

    cmd = [
        'yt-dlp',
        '-f', 'bv*[ext=mp4]', # Best video-only mp4
        '--no-audio', # Attempt to ensure no audio track included
        '--output', temp_output_template,
        url
    ]
    logger.info(f"Job {job_id}: Running yt-dlp command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Job {job_id}: yt-dlp stdout: {result.stdout}")
        logger.info(f"Job {job_id}: yt-dlp stderr: {result.stderr}")

        # Find the actually downloaded file (yt-dlp might adjust extension)
        downloaded_file = None
        for f in os.listdir(LOCAL_STORAGE_PATH):
            if f.startswith(f"{job_id}_temp"):
                 downloaded_file = os.path.join(LOCAL_STORAGE_PATH, f)
                 break

        if not downloaded_file or not os.path.exists(downloaded_file):
             raise Exception("yt-dlp completed but output file not found.")

        # Rename to predictable final path
        os.rename(downloaded_file, final_output_path)
        logger.info(f"Job {job_id}: YouTube video downloaded and renamed to {final_output_path}")
        return final_output_path

    except subprocess.CalledProcessError as e:
        logger.error(f"Job {job_id}: yt-dlp command failed. Error: {e.stderr}")
        raise Exception(f"yt-dlp failed: {e.stderr}")
    except Exception as e:
        logger.error(f"Job {job_id}: Error during YouTube download: {str(e)}")
        raise

def process_get_scenes(video_url, timestamps, job_id):
    """
    Downloads a video (handles YouTube URLs) and extracts frames at specified timestamps.
    Uploads frames to cloud storage and returns their URLs.
    """
    local_video_path = None
    generated_files = []
    scene_urls = []

    output_template = os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_scene_{{timestamp}}.jpg")

    try:
        # --- 1. Download Video ---
        if is_youtube_url(video_url):
            logger.info(f"Job {job_id}: Detected YouTube URL. Downloading with yt-dlp...")
            local_video_path = download_youtube_video(video_url, output_template, job_id)
        else:
            logger.info(f"Job {job_id}: Downloading standard URL...")
            local_video_path = download_file(video_url, LOCAL_STORAGE_PATH)
            # Rename downloaded file for consistency if needed (optional)
            base, ext = os.path.splitext(local_video_path)
            consistent_path = os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_video{ext}")
            if local_video_path != consistent_path:
                 os.rename(local_video_path, consistent_path)
                 local_video_path = consistent_path
            logger.info(f"Job {job_id}: Video downloaded to {local_video_path}")

        if not local_video_path or not os.path.exists(local_video_path):
             raise Exception("Video download failed or file not found.")

        # --- 2. Extract Frames ---
        unique_timestamps = sorted(list(set(timestamps))) # Ensure uniqueness and order

        for ts in unique_timestamps:
            if not isinstance(ts, (int, float)) or ts < 0:
                logger.warning(f"Job {job_id}: Skipping invalid timestamp {ts}")
                continue
            
            # Ensure timestamp string is safe for filenames
            ts_str = str(ts).replace('.', '_') 
            scene_filename = output_template.format(timestamp=ts_str)
            generated_files.append(scene_filename)

            # Use -ss before -i for faster seeking
            cmd = [
                'ffmpeg',
                '-ss', str(ts),
                '-i', local_video_path,
                '-vframes', '1',
                '-q:v', '2', # Good quality JPEG
                scene_filename
            ]
            logger.info(f"Job {job_id}: Extracting frame at {ts}s: {' '.join(cmd)}")
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                 # Log error but try to continue with other timestamps
                 logger.error(f"Job {job_id}: Failed to extract frame at {ts}s. Error: {e.stderr}")
                 # Remove potentially incomplete file
                 if os.path.exists(scene_filename):
                     os.remove(scene_filename)
                 generated_files.remove(scene_filename) # Don't try to upload it

        # --- 3. Upload Frames ---
        logger.info(f"Job {job_id}: Uploading {len(generated_files)} extracted scenes...")
        for scene_file in generated_files:
             if os.path.exists(scene_file):
                 try:
                     cloud_url = upload_file(scene_file)
                     # Extract timestamp safely from filename
                     try:
                         base_name = os.path.basename(scene_file)
                         # Split by the last occurrence of '_scene_' before the extension
                         parts = base_name.rsplit('_scene_', 1)
                         if len(parts) == 2:
                             ts_part = parts[1].replace('.jpg', '')
                             original_ts = float(ts_part.replace('_', '.'))
                             scene_urls.append({"timestamp": original_ts, "url": cloud_url})
                         else:
                              logger.warning(f"Job {job_id}: Could not parse timestamp from filename {scene_file}")
                     except Exception as parse_err:
                         logger.error(f"Job {job_id}: Error parsing timestamp from {scene_file}: {parse_err}")
                 except Exception as upload_err:
                     logger.error(f"Job {job_id}: Failed to upload scene {scene_file}. Error: {upload_err}")
                     # Optionally collect failed uploads info? For now, just log.

        logger.info(f"Job {job_id}: Scene extraction and upload complete.")
        return scene_urls

    except Exception as e:
        logger.error(f"Job {job_id}: Error in process_get_scenes: {str(e)}", exc_info=True)
        raise # Re-raise the exception to be caught by the route handler

    finally:
        # --- 4. Cleanup ---
        logger.info(f"Job {job_id}: Cleaning up temporary files...")
        if local_video_path and os.path.exists(local_video_path):
            try:
                os.remove(local_video_path)
                logger.debug(f"Job {job_id}: Removed video file {local_video_path}")
            except OSError as e:
                logger.error(f"Job {job_id}: Error removing video file {local_video_path}: {e}")
        for scene_file in generated_files:
            if os.path.exists(scene_file):
                try:
                    os.remove(scene_file)
                    logger.debug(f"Job {job_id}: Removed scene file {scene_file}")
                except OSError as e:
                    logger.error(f"Job {job_id}: Error removing scene file {scene_file}: {e}") 
