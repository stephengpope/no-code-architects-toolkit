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



from flask import Blueprint, jsonify
from app_utils import *
import logging
from services.v1.video.thumbnail import extract_thumbnail
from services.authentication import authenticate
from services.cloud_storage import upload_file

v1_video_thumbnail_bp = Blueprint('v1_video_thumbnail', __name__)
logger = logging.getLogger(__name__)

@v1_video_thumbnail_bp.route('/v1/video/thumbnail', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "video_url": {"type": "string", "format": "uri"},
        "second": {"type": "number", "minimum": 0},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["video_url"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def generate_thumbnail(job_id, data):
    video_url = data.get('video_url')
    second = data.get('second', 0)  # Default to 0 if not provided
    webhook_url = data.get('webhook_url')

    logger.info(f"Job {job_id}: Received thumbnail extraction request for {video_url} at {second} seconds")

    try:
        # Process thumbnail extraction
        thumbnail_path = extract_thumbnail(video_url, job_id, second)

        # Upload the thumbnail to cloud storage
        file_url = upload_file(thumbnail_path)

        logger.info(f"Job {job_id}: Thumbnail uploaded to cloud storage at {file_url}")

        # Return the URL of the uploaded thumbnail
        return file_url, "/v1/video/thumbnail", 200
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error during thumbnail extraction - {str(e)}")
        return str(e), "/v1/video/thumbnail", 500
