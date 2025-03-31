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
from services.ffmpeg_toolkit import process_video_combination
from services.authentication import authenticate
from services.cloud_storage import upload_file

combine_bp = Blueprint('combine', __name__)
logger = logging.getLogger(__name__)

@combine_bp.route('/combine-videos', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "video_urls": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "video_url": {"type": "string", "format": "uri"}
                },
                "required": ["video_url"]
            },
            "minItems": 1
        },
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["video_urls"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def combine_videos(job_id, data):
    media_urls = data['video_urls']
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    logger.info(f"Job {job_id}: Received combine-videos request for {len(media_urls)} videos")

    try:
        output_file = process_video_combination(media_urls, job_id)
        logger.info(f"Job {job_id}: Video combination process completed successfully")

        cloud_url = upload_file(output_file)
        logger.info(f"Job {job_id}: Combined video uploaded to cloud storage: {cloud_url}")

        return cloud_url, "/combine-videos", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during video combination process - {str(e)}")
        return str(e), "/combine-videos", 500