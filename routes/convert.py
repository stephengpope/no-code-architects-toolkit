from flask import Blueprint, request, jsonify
import uuid
import threading
import logging
import queue
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

# Create a queue for conversion jobs
conversion_queue = queue.Queue()

def conversion_worker():
    while True:
        job = conversion_queue.get()
        try:
            process_and_notify(**job)
        except Exception as e:
            logger.error(f"Error processing job: {e}")
        finally:
            conversion_queue.task_done()

# Start the worker thread
worker_thread = threading.Thread(target=conversion_worker, daemon=True)
worker_thread.start()

def process_and_notify(media_url, job_id, output_filename, id, webhook_url=None):
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

        # If webhook_url is provided, send a success webhook
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/media-to-mp3",
                "id": id,  # Include the original id
                "response": uploaded_file_url,
                "code": 200,
                "message": "success"
            })
        else:
            return {
                "response": uploaded_file_url,
                "message": "success",
                "id": id  # Include the original id in the synchronous response
            }

    except Exception as e:
        logger.error(f"Job {job_id}: Error during processing - {e}")

        # If webhook_url is provided, send a failure webhook
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/media-to-mp3",
                "id": id,  # Include the original id
                "error": str(e),
                "code": 500,
                "message": "failed"
            })
        else:
            raise e  # Re-raise the exception to handle it in the synchronous request
    finally:
        logger.info(f"Job {job_id}: Exiting process_and_notify function.")

@convert_bp.route('/media-to-mp3', methods=['POST'])
@authenticate
def convert_media_to_mp3():
    data = request.json
    media_url = data.get('media_url')
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    if not media_url or not id:
        logger.error("Received API call with missing media_url or id parameter.")
        return jsonify({"error": "Missing media_url or id parameter"}), 400

    job_id = str(uuid.uuid4())
    output_filename = f"{job_id}.mp3"
    logger.info(f"Job {job_id}: Received conversion request for {media_url}")

    if webhook_url:
        # Add the job to the queue for background processing
        conversion_queue.put({
            'media_url': media_url,
            'job_id': job_id,
            'output_filename': output_filename,
            'id': id,
            'webhook_url': webhook_url
        })
        logger.info(f"Job {job_id}: Added to queue for background processing")
        return jsonify({ "message": "processing" }), 202
    else:
        try:
            # Process the conversion synchronously and return the URL with the original id
            response = process_and_notify(media_url, job_id, output_filename, id)
            return jsonify(response), 200
        except Exception as e:
            return jsonify({ "message": str(e) }), 500
