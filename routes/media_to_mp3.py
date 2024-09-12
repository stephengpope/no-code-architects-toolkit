from flask import Blueprint, request, jsonify
import uuid
import threading
import logging
import queue
import os
from services.ffmpeg_tools import process_conversion
from services.authentication import authenticate
from services.webhook import send_webhook
from services.gdrive_service import process_gdrive_upload, upload_to_gdrive, upload_to_gcs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the storage path to /tmp/ permanently
STORAGE_PATH ="/tmp/"
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

def process_and_notify(media_url, job_id, id, webhook_url):
    try:
        logger.info(f"Job {job_id}: Initiating media conversion...")
        output_path = process_conversion(media_url, job_id)
        logger.info(f"Job {job_id}: Conversion completed. Output file: {output_path}")

        # Proceed with upload to GCS or Google Drive
        uploaded_file_url = None
        if GCP_BUCKET_NAME:
            logger.info(f"Job {job_id}: Uploading to Google Cloud Storage bucket '{GCP_BUCKET_NAME}'...")
            uploaded_file_url = upload_to_gcs(output_path, GCP_BUCKET_NAME)
        else:
            logger.error(f"Job {job_id}: GCP_BUCKET_NAME is not set.")
            raise Exception("No valid storage destination is set (GCS or Google Drive).")

        if not uploaded_file_url:
            logger.error(f"Job {job_id}: Failed to upload the output file {output_path}.")
            raise Exception(f"Failed to upload the output file {output_path}")

        logger.info(f"Job {job_id}: File uploaded successfully. URL: {uploaded_file_url}")

        # Send success webhook if applicable
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/media-to-mp3",
                "id": id,
                "job_id": job_id,
                "response": uploaded_file_url,
                "code": 200,
                "message": "success"
            })

        return uploaded_file_url

    except Exception as e:
        logger.error(f"Job {job_id}: Error during processing - {e}")
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/media-to-mp3",
                "id": id,
                "job_id": job_id,
                "response": None,
                "message": str(e),
                "code": 500
            })
        else:
            raise

    finally:
        logger.info(f"Job {job_id}: Exiting process_and_notify function.")

@convert_bp.route('/media-to-mp3', methods=['POST'])
@authenticate
def convert_media_to_mp3():
    data = request.json
    media_url = data.get('media_url')
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    # Ensure media_url is present
    if not media_url:
        logger.error("Received API call with missing media_url parameter.")
        return jsonify({"message": "Missing media_url parameter"}), 400

    # Only check for id if webhook_url is provided
    #if webhook_url and not id:
    #    logger.error("Received API call with webhook_url but missing id parameter.")
    #    return jsonify({"message": "Missing id parameter for webhook"}), 400

    job_id = str(uuid.uuid4())
    logger.info(f"Job {job_id}: Received conversion request for {media_url}")

    if webhook_url:
        # Add the job to the queue for background processing
        conversion_queue.put({
            'media_url': media_url,
            'job_id': job_id,
            'id': id,
            'webhook_url': webhook_url
        })
        logger.info(f"Job {job_id}: Added to queue for background processing")
        return jsonify(
            {
                "code": 202,
                "id": id,
                "job_id": job_id,
                "message": "processing"
            }
        ), 202
    else:
        try:
            # Process the conversion synchronously and return the URL
            uploaded_file_url = process_and_notify(media_url=media_url, job_id=job_id, id=id, webhook_url=None)

            return jsonify({
                "code": 200,
                "response": uploaded_file_url,
                "message": "success"
            }), 200
            
        except Exception as e:
            logger.error(f"Job {job_id}: Error during synchronous processing - {e}")
            return jsonify({
                "code": 500,
                "message": str(e)
            }), 500
