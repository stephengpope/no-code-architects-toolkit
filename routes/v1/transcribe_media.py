from flask import Blueprint
from app_utils import *
import logging
import os
from services.v1.transcribe_media import process_transcribe_media
from services.authentication import authenticate
from services.cloud_storage import upload_file

v1_transcribe_media_bp = Blueprint('v1_transcribe_media', __name__)
logger = logging.getLogger(__name__)

@v1_transcribe_media_bp.route('/v1/transcribe/media', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "media_url": {"type": "string", "format": "uri"},
        "task": {"type": "string", "enum": ["transcribe", "translate"]},
        "format_type": {"type": "string", "enum": ["text", "srt", "vtt"]},
        "word_timestamps": {"type": "boolean"},
        "segments": {"type": "boolean"},
        "response_type": {"type": "string", "enum": ["json", "cloud"]},
        "language": {"type": "string"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["media_url"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def transcribe(job_id, data):
    media_url = data['media_url']
    task = data.get('task', 'transcribe')
    format_type = data.get('format_type', 'text')
    word_timestamps = data.get('word_timestamps', False)
    segments = data.get('segments', False)
    response_type = data.get('response_type', 'json')
    language = data.get('language', None)
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    logger.info(f"Job {job_id}: Received transcription request for {media_url}")

    try:
        result = process_transcribe_media(media_url, task, format_type, word_timestamps, segments, response_type, language, job_id)
        logger.info(f"Job {job_id}: Transcription process completed successfully")

        # If the result is a file path, upload it using the unified upload_file() method
        if response_type == "json":
           
            result_json = {
                "text": result[0],
                "segments": result[1],
                "captions": result[2],
            }

            return result_json, "/v1/transcribe/media", 200

        else:

            cloud_urls = {
                "text_url": upload_file(result[0]),
                "segments_url": upload_file(result[1]) if segments is True else None,
                "captions_url": upload_file(result[2]) if format_type in ["srt", "vtt"] else None,
            }

            os.remove(result[0])  # Remove the temporary file after uploading
            
            if segments is True:
                os.remove(result[1])
            
            if format_type in ["srt", "vtt"]:
                os.remove(result[2]) 

            return cloud_urls, "/v1/transcribe/media", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during transcription process - {str(e)}")
        return str(e), "/v1/transcribe/media", 500
