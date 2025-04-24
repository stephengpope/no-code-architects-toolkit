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



# routes/media_to_mp3.py
from flask import Blueprint, current_app
from app_utils import *
import logging
from services.v1.media.convert.media_to_mp3 import process_media_to_mp3
from services.authentication import authenticate
from services.cloud_storage import upload_file
import os

v1_media_convert_mp3_bp = Blueprint('v1_media_convert_mp3', __name__)
logger = logging.getLogger(__name__)

@v1_media_convert_mp3_bp.route('/v1/media/convert/mp3', methods=['POST'])
@v1_media_convert_mp3_bp.route('/v1/media/transform/mp3', methods=['POST']) #depleft for backwards compatibility, do not use.
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "media_url": {"type": "string", "format": "uri"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"},
        "bitrate": {"type": "string", "pattern": "^[0-9]+k$"},
        "sample_rate": {"type": "number"}
    },
    "required": ["media_url"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def convert_media_to_mp3(job_id, data):
    media_url = data['media_url']
    webhook_url = data.get('webhook_url')
    id = data.get('id')
    bitrate = data.get('bitrate', '128k')
    sample_rate = data.get('sample_rate')

    logger.info(f"Job {job_id}: Received media-to-mp3 request for media URL: {media_url}")

    try:
        output_file = process_media_to_mp3(media_url, job_id, bitrate, sample_rate)
        logger.info(f"Job {job_id}: Media conversion process completed successfully")

        cloud_url = upload_file(output_file)
        logger.info(f"Job {job_id}: Converted media uploaded to cloud storage: {cloud_url}")

        return cloud_url, "/v1/media/transform/mp3", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during media conversion process - {str(e)}")
        return str(e), "/v1/media/transform/mp3", 500