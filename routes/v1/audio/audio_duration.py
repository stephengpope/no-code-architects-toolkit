from flask import Blueprint, request, jsonify
from app_utils import validate_payload, queue_task_wrapper
from services.authentication import authenticate
import subprocess
import requests
from tempfile import NamedTemporaryFile
import logging

v1_audio_duration_bp = Blueprint("v1_audio_duration_bp", __name__)
logger = logging.getLogger(__name__)

@v1_audio_duration_bp.route("/v1/audio/audio-duration", methods=["POST"])
@authenticate
@validate_payload(
    {
        "type": "object",
        "properties": {
            "file_url": {"type": "string", "format": "uri"},
            "webhook_url": {"type": "string", "format": "uri"},
            "id": {"type": "string"}
        },
        "required": ["file_url"],
        "additionalProperties": False
    }
)
@queue_task_wrapper(bypass_queue=False)
def get_audio_duration(job_id, data):
    file_url = data.get("file_url")
    webhook_url = data.get("webhook_url")
    id = data.get("id")

    logger.info(f"Job {job_id}: Received duration request for {file_url}")

    try:
        response = requests.get(file_url)
        response.raise_for_status()

        with NamedTemporaryFile(suffix=".mp3") as tmp:
            tmp.write(response.content)
            tmp.flush()

            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                tmp.name
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"Job {job_id}: ffprobe error - {error_msg}")
                return error_msg, "/v1/audio/audio-duration", 500

            duration = float(result.stdout.strip())
            logger.info(f"Job {job_id}: duration is {duration} seconds")
            return {"duration": round(duration, 2)}, "/v1/audio/audio-duration", 200

    except Exception as e:
        logger.exception(f"Job {job_id}: Exception - {str(e)}")
        return str(e), "/v1/audio/audio-duration", 500
