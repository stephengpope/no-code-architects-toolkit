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
from app_utils import validate_payload, queue_task_wrapper
import logging
from services.v1.media.convert.media_convert import process_media_convert
from services.authentication import authenticate
from services.cloud_storage import upload_file
import os

v1_media_convert_bp = Blueprint('v1_media_convert', __name__)
logger = logging.getLogger(__name__)

@v1_media_convert_bp.route('/v1/media/convert', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "media_url": {"type": "string", "format": "uri"},
        "format": {"type": "string"},
        "video_codec": {"type": "string"},
        "video_preset": {"type": "string"},
        "video_crf": {"type": "number", "minimum": 0, "maximum": 51},
        "audio_codec": {"type": "string"},
        "audio_bitrate": {"type": "string"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["media_url", "format"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def convert_media_format(job_id, data):
    media_url = data['media_url']
    output_format = data['format']
    video_codec = data.get('video_codec', 'libx264')
    video_preset = data.get('video_preset', 'medium')
    video_crf = data.get('video_crf', 23)
    audio_codec = data.get('audio_codec', 'aac')
    audio_bitrate = data.get('audio_bitrate', '128k')
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    logger.info(f"Job {job_id}: Received media conversion request for media URL: {media_url} to format: {output_format}")

    try:
        output_file = process_media_convert(
            media_url, 
            job_id, 
            output_format, 
            video_codec, 
            video_preset,
            video_crf,
            audio_codec,
            audio_bitrate,
            webhook_url
        )
        logger.info(f"Job {job_id}: Media format conversion completed successfully")

        cloud_url = upload_file(output_file)
        logger.info(f"Job {job_id}: Converted media uploaded to cloud storage: {cloud_url}")
        
        return cloud_url, "/v1/media/convert", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during media conversion process - {str(e)}")
        return {"error": str(e)}, "/v1/media/convert", 500 