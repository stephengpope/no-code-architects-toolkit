from flask import Blueprint, current_app
from app_utils import *
import logging
from services.caption_video import process_captioning
from services.authentication import authenticate
from services.cloud_storage import upload_file
import os

caption_bp = Blueprint('caption', __name__)
logger = logging.getLogger(__name__)

@caption_bp.route('/caption-video', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "video_url": {"type": "string", "format": "uri"},
        "srt": {"type": "string"},
        "ass": {"type": "string"},
        "options": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "option": {"type": "string"},
                    "value": {}  # Allow any type for value
                },
                "required": ["option", "value"]
            }
        },
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["video_url"],
    "oneOf": [
        {"required": ["srt"]},
        {"required": ["ass"]}
    ],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def caption_video(job_id, data):
    video_url = data['video_url']
    caption_srt = data.get('srt')
    caption_ass = data.get('ass')
    options = data.get('options', [])
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    logger.info(f"Job {job_id}: Received captioning request for {video_url}")
    logger.info(f"Job {job_id}: Options received: {options}")

    if caption_ass is not None:
        captions = caption_ass
        caption_type = "ass"
    else:
        captions = caption_srt
        caption_type = "srt"

    try:
        output_filename = process_captioning(video_url, captions, caption_type, options, job_id)
        logger.info(f"Job {job_id}: Captioning process completed successfully")

        # Upload the captioned video using the unified upload_file() method
        cloud_url = upload_file(output_filename)

        logger.info(f"Job {job_id}: Captioned video uploaded to cloud storage: {cloud_url}")

        # Return the cloud URL for the uploaded file
        return cloud_url, "/caption-video", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during captioning process - {str(e)}", exc_info=True)
        return str(e), "/caption-video", 500
