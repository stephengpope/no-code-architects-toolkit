from flask import Blueprint, request, jsonify
from app_utils import validate_payload, queue_task_wrapper
import logging
from services.authentication import authenticate
from services.cloud_storage import upload_file
from services.v1.audio.speech import generate_tts
import os

v1_audio_speech_bp = Blueprint("v1_audio_speech", __name__)
logger = logging.getLogger(__name__)

@v1_audio_speech_bp.route("/v1/audio/speech", methods=["POST"])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "tts": {"type": "string", "enum": ["edge-tts", "streamlabs-polly"]},
        "text": {"type": "string"},
        "voice": {"type": "string"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"},
    },
    "required": ["text"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def text_to_speech(job_id, data):
    tts = data.get("tts", "edge-tts")
    text = data["text"]
    voice = data.get("voice")
    webhook_url = data.get("webhook_url")
    id = data.get("id")

    logger.info(f"Job {job_id}: Received TTS request for text length {len(text)}")

    try:
        file = generate_tts(tts, text, voice, job_id)
        cloud_url = upload_file(file)
        logger.info(f"Job {job_id}: TTS audio uploaded to cloud storage: {cloud_url}")
        return cloud_url, "/v1/audio/speech", 200
    except Exception as e:
        logger.error(f"Job {job_id}: Error during TTS process - {str(e)}")
        return str(e), "/v1/audio/speech", 500
    finally:
        try:
            if os.path.exists(file):
                os.remove(file)
        except Exception as cleanup_error:
            logger.warning(f"Cleanup failed: {cleanup_error}")
