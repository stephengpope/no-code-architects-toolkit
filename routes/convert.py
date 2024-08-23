from flask import Blueprint, request, jsonify
import uuid
import threading
import logging
import os
from services.ffmpeg_processing import process_conversion
from services.authentication import authenticate
from services.webhook import send_webhook
from services.gdrive_service import upload_to_gdrive, upload_to_gcs, move_to_local_storage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
STORAGE_PATH = os.getenv('STORAGE_PATH', 'local').lower()
GCP_BUCKET_NAME = os.getenv('GCP_BUCKET_NAME')
GDRIVE_USER = os.getenv('GDRIVE_USER')

convert_bp = Blueprint('convert', __name__)

@convert_bp.route('/media-to-mp3', methods=['POST'])
@authenticate
def convert_media_to_mp3():
    data = request.json
    media_url = data.get('media_url')
    webhook_url = data.get('webhook_url')

    if not media_url:
        logger.error("Received API call with missing media_url parameter.")
        return jsonify({"error": "Missing media_url parameter"}), 400

    job_id = str(uuid.uuid4())
    output_filename = f"{job_id}.mp3"
    logger.info(f"Job {job_id}: Starting conversion for {media_url}")

    def process_and_notify():
        logger.info(f"Job {job_id}: Entering process_and_notify function.")
        try:
            # Process the conversion
            logger.info(f"Job {job_id}: Initiating media conversion...")
            output_path = process_conversion(media_url, job_id)
            logger.info(f"Job {job_id}: Conversion completed. Output file: {output_path}")

            uploaded_file_url = None

            # Handle different storage methods
            if STORAGE_PATH == 'gcp':
                if GCP_BUCKET_NAME:
                    logger.info(f"Job {job_id}: Uploading to Google Cloud Storage bucket '{GCP_BUCKET_NAME}'...")
                    uploaded_file_url = upload_to_gcs(output_path, GCP_BUCKET_NAME, output_filename)
                else:
                    raise Exception("GCP_BUCKET_NAME is not set while STORAGE_PATH is set to GCP")
            elif STORAGE_PATH == 'drive':
                if GDRIVE_USER:
                    logger.info(f"Job {job_id}: STORAGE_PATH is set to Drive. File already in Google Drive.")
                    uploaded_file_url = output_path  # No need to upload again
                else:
                    raise Exception("GDRIVE_USER is not set while STORAGE_PATH is set to Drive")
            elif STORAGE_PATH == 'local':
                logger.info(f"Job {job_id}: STORAGE_PATH is set to local. Moving file to local storage...")
                uploaded_file_url = move_to_local_storage(output_path, output_filename)
            else:
                raise Exception(f"Invalid STORAGE_PATH: {STORAGE_PATH}")

            if not uploaded_file_url:
                raise Exception(f"Failed to upload/move the output file {output_path}")

            logger.info(f"Job {job_id}: File uploaded/moved successfully. URL/Path: {uploaded_file_url}")

            # Send success webhook
            if webhook_url:
                send_webhook(webhook_url, {
                    "endpoint": "/media-to-mp3",
                    "job_id": job_id,
                    "response": uploaded_file_url,
                    "code": 200,
                    "message": "success"
                })

        except Exception as e:
            logger.error(f"Job {job_id}: Error during processing - {e}")

            # Send failure webhook
            if webhook_url:
                send_webhook(webhook_url, {
                    "endpoint": "/media-to-mp3",
                    "job_id": job_id,
                    "error": str(e),
                    "code": 500,
                    "message": "failed"
                })
        finally:
            logger.info(f"Job {job_id}: Exiting process_and_notify function.")

    if webhook_url:
        threading.Thread(target=process_and_notify).start()
        return jsonify({"job_id": job_id, "filename": output_filename}), 202
    else:
        try:
            output_path = process_conversion(media_url, job_id)
            return jsonify({"job_id": job_id, "filename": output_filename}), 200
        except Exception as e:
            logger.error(f"Job {job_id}: Error during processing - {e}")
            return jsonify({"error": str(e)}), 500