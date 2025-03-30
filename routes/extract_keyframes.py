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
from services.extract_keyframes import process_keyframe_extraction
from services.authentication import authenticate
from services.cloud_storage import upload_file

extract_keyframes_bp = Blueprint('extract_keyframes', __name__)
logger = logging.getLogger(__name__)

@extract_keyframes_bp.route('/extract-keyframes', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "video_url": {"type": "string", "format": "uri"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["video_url"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def extract_keyframes(job_id, data):
    video_url = data.get('video_url')
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    logger.info(f"Job {job_id}: Received keyframe extraction request for {video_url}")

    try:
        # Process keyframe extraction
        image_paths = process_keyframe_extraction(video_url, job_id)

        # Upload each extracted keyframe and collect the cloud URLs
        image_urls = []
        for image_path in image_paths:
            cloud_url = upload_file(image_path)
            image_urls.append({"image_url": cloud_url})

        logger.info(f"Job {job_id}: Keyframes uploaded to cloud storage")

        # Return the URLs of the uploaded keyframes
        return {"image_urls": image_urls}, "/extract-keyframes", 200
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error during keyframe extraction - {str(e)}")
        return str(e), "/extract-keyframes", 500
