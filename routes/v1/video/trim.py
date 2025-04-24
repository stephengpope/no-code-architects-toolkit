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



from flask import Blueprint
from app_utils import *
import logging
from services.v1.video.trim import trim_video
from services.authentication import authenticate

v1_video_trim_bp = Blueprint('v1_video_trim', __name__)
logger = logging.getLogger(__name__)

@v1_video_trim_bp.route('/v1/video/trim', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "video_url": {"type": "string", "format": "uri"},
        "start": {"type": "string"},
        "end": {"type": "string"},
        "video_codec": {"type": "string"},
        "video_preset": {"type": "string"},
        "video_crf": {"type": "number", "minimum": 0, "maximum": 51},
        "audio_codec": {"type": "string"},
        "audio_bitrate": {"type": "string"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["video_url"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def video_trim(job_id, data):
    """Trim a video by removing specified portions from the beginning and/or end with optional encoding settings."""
    video_url = data['video_url']
    start = data.get('start')
    end = data.get('end')
    
    # Extract encoding settings with defaults
    video_codec = data.get('video_codec', 'libx264')
    video_preset = data.get('video_preset', 'medium')
    video_crf = data.get('video_crf', 23)
    audio_codec = data.get('audio_codec', 'aac')
    audio_bitrate = data.get('audio_bitrate', '128k')
    
    logger.info(f"Job {job_id}: Received video trim request for {video_url}")
    
    try:
        # Process the video file and get local file paths
        output_filename, input_filename = trim_video(
            video_url=video_url,
            start=start,
            end=end,
            job_id=job_id,
            video_codec=video_codec,
            video_preset=video_preset,
            video_crf=video_crf,
            audio_codec=audio_codec,
            audio_bitrate=audio_bitrate
        )
        
        # Upload the processed file to cloud storage
        from services.cloud_storage import upload_file
        cloud_url = upload_file(output_filename)
        logger.info(f"Job {job_id}: Uploaded output to cloud: {cloud_url}")
        
        # Clean up temporary files
        import os
        os.remove(input_filename)
        os.remove(output_filename)
        logger.info(f"Job {job_id}: Removed temporary files")
        
        logger.info(f"Job {job_id}: Video trim operation completed successfully")
        return cloud_url, "/v1/video/trim", 200
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error during video trim process - {str(e)}")
        return str(e), "/v1/video/trim", 500