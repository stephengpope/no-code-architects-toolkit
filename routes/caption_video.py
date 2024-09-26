from flask import Blueprint, current_app
from app_utils import *
import logging
from services.caption_video import process_captioning
from services.authentication import authenticate
from services.gcp_toolkit import upload_to_gcs, GCP_BUCKET_NAME, gcs_client
from services.s3_toolkit import upload_to_s3
import os

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
        # Process captioning
        output_filename = process_captioning(video_url, caption_srt, options, job_id)

        # Determine which storage provider to use
        s3_url = os.getenv('S3_URL')
        s3_access_key = os.getenv('S3_ACCESS_KEY')
        s3_secret_key = os.getenv('S3_SECRET_KEY')
        gcp_bucket_name = os.getenv('GCP_BUCKET_NAME')

        if s3_url and s3_access_key and s3_secret_key:
            # Log S3 environment variables for debugging
            logger.info(f"Job {job_id}: S3_URL={s3_url}, S3_ACCESS_KEY={s3_access_key}, S3_SECRET_KEY={s3_secret_key}")

            # Upload to S3
            cloud_url = upload_to_s3(output_filename, s3_url, s3_access_key, s3_secret_key)
        elif gcp_bucket_name and gcs_client:
            # Log GCP environment variables for debugging
            logger.info(f"Job {job_id}: GCP_BUCKET_NAME={gcp_bucket_name}")

            # Upload to GCS
            cloud_url = upload_to_gcs(output_filename, gcp_bucket_name)
        else:
            raise ValueError("No valid storage provider is configured. Ensure either S3 or GCP environment variables are set.")

        logger.info(f"Job {job_id}: File uploaded to cloud storage: {cloud_url}")

        return cloud_url, "/caption-video", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during captioning process - {str(e)}", exc_info=True)
        return str(e), "/caption-video", 500