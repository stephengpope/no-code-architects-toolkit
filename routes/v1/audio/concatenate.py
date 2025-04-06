from flask import Blueprint
from app_utils import *
import logging
from services.v1.audio.concatenate import process_audio_concatenate
from services.authentication import authenticate
from services.cloud_storage import upload_file

v1_audio_concatenate_bp = Blueprint("v1_audio_concatenate", __name__)
logger = logging.getLogger(__name__)


@v1_audio_concatenate_bp.route("/v1/audio/concatenate", methods=["POST"])
@authenticate
@validate_payload(
    {
        "type": "object",
        "properties": {
            "audio_urls": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"audio_url": {"type": "string", "format": "uri"}},
                    "required": ["audio_url"],
                },
                "minItems": 1,
            },
            "webhook_url": {"type": "string", "format": "uri"},
            "id": {"type": "string"},
        },
        "required": ["audio_urls"],
        "additionalProperties": False,
    }
)
@queue_task_wrapper(bypass_queue=False)
def combine_audio(job_id, data):
    media_urls = data["audio_urls"]
    webhook_url = data.get("webhook_url")
    id = data.get("id")

    logger.info(
        f"Job {job_id}: Received combine-audio request for {len(media_urls)} audio files"
    )

    try:
        output_file = process_audio_concatenate(media_urls, job_id)
        logger.info(f"Job {job_id}: Audio combination process completed successfully")

        cloud_url = upload_file(output_file)
        logger.info(
            f"Job {job_id}: Combined audio uploaded to cloud storage: {cloud_url}"
        )

        return cloud_url, "/v1/audio/concatenate", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during audio combination process - {str(e)}")
        return str(e), "/v1/audio/concatenate", 500
