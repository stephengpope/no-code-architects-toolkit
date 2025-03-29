from flask import Blueprint
from app_utils import *
import logging
from services.v1.video.overlay import process_video_overlay
from services.authentication import authenticate
from services.cloud_storage import upload_file

v1_video_overlay_bp = Blueprint('v1_video_overlay', __name__)
logger = logging.getLogger(__name__)

@v1_video_overlay_bp.route('/v1/video/overlay', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "video_url": {"type": "string", "format": "uri"},
        "overlay_video_url": {"type": "string", "format": "uri"},
        "start_time": {"type": "number", "minimum": 0},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["video_url", "overlay_video_url", "start_time"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def overlay_videos(job_id, data):
    video_url = data['video_url']
    overlay_video_url = data['overlay_video_url']
    start_time = data['start_time']
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    logger.info(f"Job {job_id}: Received video overlay request")

    try:
        output_file = process_video_overlay(video_url, overlay_video_url, start_time, job_id, webhook_url)
        logger.info(f"Job {job_id}: Video overlay process completed successfully")

        cloud_url = upload_file(output_file)
        logger.info(f"Job {job_id}: Overlaid video uploaded to cloud storage: {cloud_url}")

        return cloud_url, "/v1/video/overlay", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during video overlay process - {str(e)}")
        return str(e), "/v1/video/overlay", 500