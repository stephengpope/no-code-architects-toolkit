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
    logger.info(f"Job {job_id}: Starting conversion for media URL: {media_url}")
    logger.info(f"Job {job_id}: Output filename set to: {output_filename}")

    def process_and_notify():
        logger.info(f"Job {job_id}: Entering process_and_notify function.")
        try:
            # Process the conversion
            logger.info(f"Job {job_id}: Initiating media conversion...")
            output_path = process_conversion(media_url, job_id)
            logger.info(f"Job {job_id}: Conversion completed. Output file: {output_path}")

            # Check if the output file exists after conversion (only if local)
            if STORAGE_PATH == 'local' and not os.path.exists(output_path):
                logger.error(f"Job {job_id}: Output file not found at: {output_path}")
                raise Exception(f"Output file not found after conversion: {output_path}")

            uploaded_file_url = None

            # Handle different storage methods
            if STORAGE_PATH == 'gcp':
                logger.info(f"Job {job_id}: STORAGE_PATH is set to GCP. Using existing Google Cloud Storage file URL.")
                uploaded_file_url = output_path
            elif STORAGE_PATH == 'drive':
                if GDRIVE_USER:
                    logger.info(f"Job {job_id}: Uploading to Google Drive for user: {GDRIVE_USER}")
                    logger.info(f"Job {job_id}: Uploading file from path: {output_path}")
                    uploaded_file_url = upload_to_gdrive(output_path, output_filename)
                    logger.info(f"Job {job_id}: Uploaded file to Google Drive. URL: {uploaded_file_url}")
                else:
                    logger.error(f"Job {job_id}: GDRIVE_USER environment variable is not set.")
                    raise Exception("GDRIVE_USER is not set while STORAGE_PATH is set to Drive")
            elif STORAGE_PATH == 'local':
                logger.info(f"Job {job_id}: Moving file to local storage.")
                uploaded_file_url = move_to_local_storage(output_path, output_filename)
                logger.info(f"Job {job_id}: File moved to local storage. Path: {uploaded_file_url}")
            else:
                logger.error(f"Job {job_id}: Invalid STORAGE_PATH value: {STORAGE_PATH}")
                raise Exception(f"Invalid STORAGE_PATH: {STORAGE_PATH}")

            if not uploaded_file_url:
                logger.error(f"Job {job_id}: Failed to upload/move the output file.")
                raise Exception(f"Failed to upload/move the output file {output_path}")

            logger.info(f"Job {job_id}: File uploaded/moved successfully. Final URL/Path: {uploaded_file_url}")

            # Now it's safe to remove the local file if it's not already uploaded
            if STORAGE_PATH == 'local':
                os.remove(output_path)
                logger.info(f"Job {job_id}: Removed local file {output_path}")

            # Send success webhook
            if webhook_url:
                logger.info(f"Job {job_id}: Sending success webhook to {webhook_url}")
                send_webhook(webhook_url, {
                    "endpoint": "/media-to-mp3",
                    "job_id": job_id,
                    "response": uploaded_file_url,
                    "code": 200,
                    "message": "success"
                })
                logger.info(f"Job {job_id}: Success webhook sent.")

        except Exception as e:
            logger.error(f"Job {job_id}: Error during processing - {e}")

            # Send failure webhook
            if webhook_url:
                logger.info(f"Job {job_id}: Sending failure webhook to {webhook_url}")
                send_webhook(webhook_url, {
                    "endpoint": "/media-to-mp3",
                    "job_id": job_id,
                    "error": str(e),
                    "code": 500,
                    "message": "failed"
                })
                logger.info(f"Job {job_id}: Failure webhook sent.")
        finally:
            logger.info(f"Job {job_id}: Exiting process_and_notify function.")

    if webhook_url:
        logger.info(f"Job {job_id}: Webhook URL provided. Starting processing in a separate thread.")
        threading.Thread(target=process_and_notify).start()
        return jsonify({"job_id": job_id, "filename": output_filename}), 202
    else:
        try:
            logger.info(f"Job {job_id}: No webhook URL provided. Starting synchronous processing.")
            output_path = process_conversion(media_url, job_id)
            logger.info(f"Job {job_id}: Returning successful response. Output file: {output_path}")
            return jsonify({"job_id": job_id, "filename": output_filename}), 200
        except Exception as e:
            logger.error(f"Job {job_id}: Error during processing - {e}")
            return jsonify({"error": str(e)}), 500