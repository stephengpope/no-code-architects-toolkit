from flask import Blueprint
from app_utils import *
import logging
from services.v1.caption_video import process_captioning_v1
from services.authentication import authenticate
from services.cloud_storage import upload_file
import os

v1_caption_bp = Blueprint('v1_caption', __name__)
logger = logging.getLogger(__name__)

@v1_caption_bp.route('/v1/caption-video', methods=['POST'])
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
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def caption_video_v1(job_id, data):
    video_url = data['video_url']
    caption_srt = data.get('srt')
    caption_ass = data.get('ass')
    options = data.get('options', [])
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    logger.info(f"Job {job_id}: Received v1 captioning request for {video_url}")
    logger.info(f"Job {job_id}: Options received: {options}")

    try:
        # Process video with the enhanced v1 service
        output_filename = process_captioning_v1(video_url, caption_srt, caption_ass, options, job_id)
        logger.info(f"Job {job_id}: Captioning process completed successfully")

        # Upload the captioned video
        cloud_url = upload_file(output_filename)
        logger.info(f"Job {job_id}: Captioned video uploaded to cloud storage: {cloud_url}")

        # Clean up the output file after upload
        os.remove(output_filename)
        logger.info(f"Job {job_id}: Cleaned up local output file")

        return cloud_url, "/v1/caption-video", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during captioning process - {str(e)}", exc_info=True)
        return str(e), "/v1/caption-video", 500