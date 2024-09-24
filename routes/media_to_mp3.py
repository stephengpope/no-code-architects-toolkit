from flask import Blueprint, current_app
from app_utils import *
import logging
from services.ffmpeg_toolkit import process_conversion
from services.authentication import authenticate
from services.gcp_toolkit import upload_to_gcs
import os

convert_bp = Blueprint('convert', __name__)
logger = logging.getLogger(__name__)

GCP_BUCKET_NAME = os.getenv('GCP_BUCKET_NAME')

@convert_bp.route('/media-to-mp3', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "media_url": {"type": "string", "format": "uri"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"},
        "bitrate": {"type": "string", "pattern": "^[0-9]+k$"}
    },
    "required": ["media_url"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def convert_media_to_mp3(job_id, data):
    media_url = data.get('media_url')
    webhook_url = data.get('webhook_url')
    id = data.get('id')
    bitrate = data.get('bitrate', '128k')  # Default to 128k if not provided

    logger.info(f"Job {job_id}: Received conversion request for {media_url} with bitrate {bitrate}")

    try:
        output_path = process_conversion(media_url, job_id, bitrate)
        logger.info(f"Job {job_id}: Conversion completed. Output file: {output_path}")

        if not GCP_BUCKET_NAME:
            raise Exception("GCP_BUCKET_NAME is not set.")

        logger.info(f"Job {job_id}: Uploading to Google Cloud Storage bucket '{GCP_BUCKET_NAME}'...")
        uploaded_file_url = upload_to_gcs(output_path, GCP_BUCKET_NAME)

        if not uploaded_file_url:
            raise Exception(f"Failed to upload the output file {output_path}")

        logger.info(f"Job {job_id}: File uploaded successfully. URL: {uploaded_file_url}")

        return uploaded_file_url, "/media-to-mp3", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during processing - {str(e)}")
        return str(e), "/media-to-mp3", 500