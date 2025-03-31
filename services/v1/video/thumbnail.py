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
import ffmpeg
from services.file_management import download_file
from config import LOCAL_STORAGE_PATH

def extract_thumbnail(video_url, job_id, second=0):
    """
    Extract a thumbnail from a video at the specified timestamp.
    
    Args:
        video_url (str): URL of the video to extract thumbnail from
        job_id (str): Unique identifier for the job
        second (float): Timestamp in seconds to extract the thumbnail from (default: 0)
        
    Returns:
        str: Path to the extracted thumbnail image
    """
    # Download the video from the provided URL
    video_path = download_file(video_url, os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_input"))
    
    # Set output path for the thumbnail
    thumbnail_path = os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_thumbnail.jpg")
    
    try:
        # Extract thumbnail using ffmpeg at the specified timestamp
        (
            ffmpeg
            .input(video_path, ss=second)  # 'ss' is the seek parameter for the timestamp
            .output(thumbnail_path, vframes=1)  # vframes=1 extracts a single frame
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        # Clean up the downloaded video file
        os.remove(video_path)
        
        # Ensure the thumbnail file exists
        if not os.path.exists(thumbnail_path):
            raise FileNotFoundError(f"Thumbnail file {thumbnail_path} was not created")
            
        return thumbnail_path
        
    except Exception as e:
        print(f"Thumbnail extraction failed: {str(e)}")
        # Clean up any downloaded files on error
        if os.path.exists(video_path):
            os.remove(video_path)
        raise
