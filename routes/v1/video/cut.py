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
from services.v1.video.cut import cut_media
from services.authentication import authenticate

v1_video_cut_bp = Blueprint('v1_video_cut', __name__)
logger = logging.getLogger(__name__)

@v1_video_cut_bp.route('/v1/video/cut', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "video_url": {"type": "string", "format": "uri"},
        "cuts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start": {"type": "string"},
                    "end": {"type": "string"}
                },
                "required": ["start", "end"],
                "additionalProperties": False
            },
            "minItems": 1
        },
        "video_codec": {"type": "string"},
        "video_preset": {"type": "string"},
        "video_crf": {"type": "number", "minimum": 0, "maximum": 51},
        "audio_codec": {"type": "string"},
        "audio_bitrate": {"type": "string"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["video_url", "cuts"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def video_cut(job_id, data):
    """Cut specified segments from a video file with optional encoding settings."""
    video_url = data['video_url']
    cuts = data['cuts']
    
    # Extract encoding settings with defaults
    video_codec = data.get('video_codec', 'libx264')
    video_preset = data.get('video_preset', 'medium')
    video_crf = data.get('video_crf', 23)
    audio_codec = data.get('audio_codec', 'aac')
    audio_bitrate = data.get('audio_bitrate', '128k')
    
    logger.info(f"Job {job_id}: Received video cut request for {video_url}")
    
    try:
        # Process the video file and get local file paths
        output_filename, input_filename = cut_media(
            video_url=video_url,
            cuts=cuts,
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
        
        logger.info(f"Job {job_id}: Video cut operation completed successfully")
        return cloud_url, "/v1/video/cut", 200
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error during video cut process - {str(e)}")
        return str(e), "/v1/video/cut", 500