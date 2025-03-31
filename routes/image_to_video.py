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
from services.image_to_video import process_image_to_video
from services.authentication import authenticate
from services.cloud_storage import upload_file

image_to_video_bp = Blueprint('image_to_video', __name__)
logger = logging.getLogger(__name__)

@image_to_video_bp.route('/image-to-video', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "image_url": {"type": "string", "format": "uri"},
        "length": {"type": "number", "minimum": 1, "maximum": 60},
        "frame_rate": {"type": "integer", "minimum": 15, "maximum": 60},
        "zoom_speed": {"type": "number", "minimum": 0, "maximum": 100},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["image_url"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def image_to_video(job_id, data):
    image_url = data.get('image_url')
    length = data.get('length', 5)
    frame_rate = data.get('frame_rate', 30)
    zoom_speed = data.get('zoom_speed', 3) / 100
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    logger.info(f"Job {job_id}: Received image to video request for {image_url}")

    try:
        # Process image to video conversion
        output_filename = process_image_to_video(
            image_url, length, frame_rate, zoom_speed, job_id, webhook_url
        )

        # Upload the resulting file using the unified upload_file() method
        cloud_url = upload_file(output_filename)

        # Log the successful upload
        logger.info(f"Job {job_id}: Converted video uploaded to cloud storage: {cloud_url}")

        # Return the cloud URL for the uploaded file
        return cloud_url, "/image-to-video", 200
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error processing image to video: {str(e)}", exc_info=True)
        return str(e), "/image-to-video", 500
