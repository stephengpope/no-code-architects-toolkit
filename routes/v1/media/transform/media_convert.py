# routes/v1/media/transform/media_convert.py
from flask import Blueprint, jsonify
from app_utils import validate_payload, queue_task_wrapper
import logging
from services.v1.media.transform.media_convert import process_media_convert
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
        "output_format": {"type": "string"},
        "video_codec": {"type": "string"},
        "audio_codec": {"type": "string"},
        "webhook_url": {"type": "string", "format": "uri"}
    },
    "required": ["media_url", "output_format"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def convert_media_format(job_id, data):
    media_url = data['media_url']
    output_format = data['output_format']
    video_codec = data.get('video_codec', 'copy')
    audio_codec = data.get('audio_codec', 'copy')
    webhook_url = data.get('webhook_url')

    logger.info(f"Job {job_id}: Received media conversion request for media URL: {media_url} to format: {output_format}")

    try:
        output_file = process_media_convert(
            media_url, 
            job_id, 
            output_format, 
            video_codec, 
            audio_codec,
            webhook_url
        )
        logger.info(f"Job {job_id}: Media format conversion completed successfully")

        cloud_url = upload_file(output_file)
        logger.info(f"Job {job_id}: Converted media uploaded to cloud storage: {cloud_url}")

        # Return JSON response with file URL
        response = {
            "file_url": cloud_url
        }
        
        return response, "/v1/media/convert", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during media conversion process - {str(e)}")
        return {"error": str(e)}, "/v1/media/convert", 500