from flask import Blueprint
from app_utils import validate_payload, queue_task_wrapper
from services.authentication import authenticate
from services.v1.media.media_duration import get_media_duration_from_url
import logging

v1_media_duration_bp = Blueprint("v1_media_duration_bp", __name__)
logger = logging.getLogger(__name__)

@v1_media_duration_bp.route("/v1/media/media-duration", methods=["POST"])
@authenticate
@validate_payload(
    {
        "type": "object",
        "properties": {
            "media_url": {"type": "string", "format": "uri"},
            "webhook_url": {"type": "string", "format": "uri"},
            "id": {"type": "string"}
        },
        "required": ["media_url"],
        "additionalProperties": False
    }
)
@queue_task_wrapper(bypass_queue=False)
def get_media_duration(job_id, data):
    media_url = data.get("media_url")
    try:
        logger.info(f"Job {job_id}: Received media duration request for {media_url}")
        duration = get_media_duration_from_url(media_url)
        logger.info(f"Job {job_id}: media duration is {duration} seconds")
        return duration, "/v1/media/media-duration", 200
    except Exception as e:
        logger.exception(f"Job {job_id}: Exception - {str(e)}")
        return str(e), "/v1/media/media-duration", 500