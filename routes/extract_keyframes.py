from flask import Blueprint, request, jsonify
from flask import current_app
from app_utils import *
import logging
from services.extract_keyframes import process_keyframe_extraction
from services.authentication import authenticate
from services.gcp_toolkit import upload_to_gcs

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
        image_urls = process_keyframe_extraction(video_url, job_id)
        response = {"image_urls": [{"image_url": url} for url in image_urls]}
        
        return response, "/extract-keyframes", 200
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error during keyframe extraction - {str(e)}")
        return str(e), "/extract-keyframes", 500