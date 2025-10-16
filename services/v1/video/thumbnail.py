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
from config import LOCAL_STORAGE_PATH

def extract_thumbnail(video_url, job_id, second=0):
    """
    Extract a thumbnail from a video at the specified timestamp.
    Uses ffmpeg direct streaming to avoid downloading the entire video file.

    Args:
        video_url (str): URL of the video to extract thumbnail from
        job_id (str): Unique identifier for the job
        second (float): Timestamp in seconds to extract the thumbnail from (default: 0)

    Returns:
        str: Path to the extracted thumbnail image
    """
    # Set output path for the thumbnail
    thumbnail_path = os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_thumbnail.jpg")

    try:
        # Extract thumbnail directly from URL using ffmpeg streaming
        # analyzeduration and probesize are set low to reduce initial buffering
        (
            ffmpeg
            .input(video_url, ss=second, analyzeduration='100K', probesize='100K')
            .output(thumbnail_path, vframes=1, update=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )

        # Ensure the thumbnail file exists
        if not os.path.exists(thumbnail_path):
            raise FileNotFoundError(f"Thumbnail file {thumbnail_path} was not created")

        return thumbnail_path

    except Exception as e:
        print(f"Thumbnail extraction failed: {str(e)}")
        # Clean up partial thumbnail file on error
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        raise
