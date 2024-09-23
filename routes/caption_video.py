from flask import Blueprint, current_app
from app_utils import *
import logging
from services.caption_video import process_captioning
from services.authentication import authenticate
from services.gcp_toolkit import upload_to_gcs

caption_bp = Blueprint('caption', __name__)
logger = logging.getLogger(__name__)

@caption_bp.route('/caption-video', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "video_url": {"type": "string", "format": "uri"},
        "srt": {"type": "string"},
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
    "required": ["video_url", "srt"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def caption_video(job_id, data):
    video_url = data['video_url']
    caption_srt = data['srt']
    options = data.get('options', [])
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    logger.info(f"Job {job_id}: Received captioning request for {video_url}")
    logger.info(f"Job {job_id}: Options received: {options}")

    try:
        output_filename = process_captioning(video_url, caption_srt, options, job_id)
        logger.info(f"Job {job_id}: Captioning process completed successfully")

        return output_filename, "/caption-video", 200
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error during captioning process - {str(e)}", exc_info=True)
        return str(e), "/caption-video", 500