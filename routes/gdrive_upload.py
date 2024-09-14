import os
import logging
from flask import Blueprint, request, jsonify
import threading
import requests
import uuid
import json
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from datetime import datetime
import time
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the blueprint
gdrive_upload_bp = Blueprint('gdrive_upload', __name__)

# Environment variables
GCP_SA_CREDENTIALS = os.getenv('GCP_SA_CREDENTIALS')
GDRIVE_USER = os.getenv('GDRIVE_USER')

# Class to track upload progress
class UploadProgress:
    def __init__(self, job_id, total_size):
        self.job_id = job_id
        self.total_size = total_size
        self.bytes_uploaded = 0
        self.start_time = time.time()
        self.lock = threading.Lock()
        self.last_logged_percentage = 0
        self.last_logged_resource_percentage = 0  # For memory/disk logging every 5%

# Global list to keep track of active uploads
active_uploads = []
uploads_lock = threading.Lock()

def get_access_token():
    """
    Retrieves an access token for Google APIs using service account credentials.
    """
    credentials_info = json.loads(GCP_SA_CREDENTIALS)
    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    delegated_credentials = credentials.with_subject(GDRIVE_USER)
    if not delegated_credentials.valid or delegated_credentials.expired:
        delegated_credentials.refresh(Request())
    access_token = delegated_credentials.token
    return access_token

def initiate_resumable_upload(filename, folder_id, mime_type='application/octet-stream'):
    """
    Initiates a resumable upload session with Google Drive and returns the upload URL.
    """
    url = 'https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable'
    headers = {
        'Authorization': f'Bearer {get_access_token()}',
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Upload-Content-Type': mime_type
    }
    metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    response = requests.post(url, headers=headers, data=json.dumps(metadata))
    response.raise_for_status()
    upload_url = response.headers['Location']
    return upload_url

def upload_file_in_chunks(file_url, upload_url, total_size, job_id, chunk_size):
    """
    Uploads the file to Google Drive in chunks by streaming data directly from the source URL.
    """
    bytes_uploaded = 0
    max_retries = 5
    retry_delay = 5  # seconds

    progress = UploadProgress(job_id, total_size)

    # Add progress to active_uploads
    with uploads_lock:
        active_uploads.append(progress)

    try:
        with requests.get(file_url, stream=True) as r:
            r.raise_for_status()
            iterator = r.iter_content(chunk_size=chunk_size)
            for chunk in iterator:
                if chunk:
                    for attempt in range(max_retries):
                        start = bytes_uploaded
                        end = bytes_uploaded + len(chunk) - 1
                        content_range = f'bytes {start}-{end}/{total_size}'
                        headers = {
                            'Content-Length': str(len(chunk)),
                            'Content-Range': content_range,
                        }
                        try:
                            upload_response = requests.put(
                                upload_url,
                                headers=headers,
                                data=chunk
                            )
                            if upload_response.status_code in (200, 201):
                                # Upload complete
                                logger.info(f"Job {job_id}: Upload complete.")
                                with progress.lock:
                                    progress.bytes_uploaded = end + 1
                                return upload_response.json()['id']
                            elif upload_response.status_code == 308:
                                # Resumable upload incomplete
                                bytes_uploaded = end + 1
                                with progress.lock:
                                    progress.bytes_uploaded = bytes_uploaded
                                break  # Break retry loop and continue with next chunk
                            else:
                                # Handle unexpected status codes
                                logger.error(f"Job {job_id}: Unexpected status code: {upload_response.status_code}")
                                raise Exception(f"Upload failed with status code {upload_response.status_code}")
                        except requests.exceptions.RequestException as e:
                            logger.error(f"Job {job_id}: Network error during upload: {e}")
                            if attempt < max_retries - 1:
                                logger.info(f"Job {job_id}: Retrying upload chunk after {retry_delay} seconds...")
                                time.sleep(retry_delay)
                                continue
                            else:
                                logger.error(f"Job {job_id}: Max retries reached. Upload failed.")
                                raise
                    else:
                        # If we exhausted retries, exit the function
                        raise Exception("Failed to upload chunk after multiple retries.")
    finally:
        # Remove progress from active_uploads
        with uploads_lock:
            if progress in active_uploads:
                active_uploads.remove(progress)

def process_job(data, job_id):
    """
    Processes the upload job by initiating the upload session and streaming the file.
    """
    try:
        logger.info(f"Processing request with Job ID: {job_id}")
        filename = data['filename']
        folder_id = data['folder_id']
        file_url = data['file_url']
        mime_type = data.get('mime_type', 'application/octet-stream')
        chunk_size = data.get('chunk_size', 5 * 1024 * 1024)  # Default to 1 MB

        # Get the total size of the file
        head_response = requests.head(file_url)
        head_response.raise_for_status()
        total_size = int(head_response.headers.get('Content-Length', 0))
        if total_size == 0:
            raise Exception("Failed to retrieve file size from the URL.")

        # Initiate upload session
        upload_url = initiate_resumable_upload(filename, folder_id, mime_type)
        logger.info(f"Job {job_id}: Resumable upload session initiated with chunk size {chunk_size} bytes.")

        # Upload file in chunks
        file_id = upload_file_in_chunks(file_url, upload_url, total_size, job_id, chunk_size)

        if 'webhook_url' in data:
            webhook_payload = {
                'endpoint': '/gdrive-upload',
                'code': 200,
                'id': data.get("id"),
                'job_id': job_id,
                'response': file_id,
                'message': 'success'
            }
            logger.info(f"Job {job_id}: Sending success webhook to: {data['webhook_url']}")
            requests.post(data['webhook_url'], json=webhook_payload)
        else:
            return file_id

    except Exception as e:
        logger.error(f"Job {job_id}: Error processing request: {e}")
        if 'webhook_url' in data:
            webhook_payload = {
                'endpoint': '/gdrive-upload',
                'code': 500,
                'id': data.get("id"),
                'job_id': job_id,
                'response': None,
                'message': str(e)
            }
            logger.info(f"Job {job_id}: Sending failure webhook to: {data['webhook_url']}")
            requests.post(data['webhook_url'], json=webhook_payload)
        else:
            raise

@gdrive_upload_bp.route('/gdrive-upload', methods=['POST'])
def gdrive_upload():
    data = request.json

    if 'X-API-Key' not in request.headers:
        logger.error("Missing X-API-Key header")
        return jsonify({"message": "Missing X-API-Key header"}), 400

    if not GDRIVE_USER:
        logger.error("GDRIVE_USER environment variable is not set")
        return jsonify({
            "message": "GDRIVE_USER environment variable is not set. Please set it up as an environment variable."
        }), 400

    if not all(k in data for k in ('file_url', 'filename', 'folder_id')):
        logger.error("file_url, filename, and folder_id are required")
        return jsonify({"message": "file_url, filename, and folder_id are required"}), 400

    job_id = str(uuid.uuid4())
    logger.info(f"Processing Job ID: {job_id}")

    if 'webhook_url' in data:
        threading.Thread(target=process_job, args=(data, job_id)).start()
        return jsonify({
            "code": 202,
            "id": data.get("id"),
            "job_id": job_id,
            "message": "processing"
        }), 202
    else:
        try:
            file_id = process_job(data, job_id)
            return jsonify({
                "code": 200,
                "response": file_id,
                "message": "success"
            }), 200
        except Exception as e:
            logger.error(f"Job {job_id}: Error during synchronous processing - {e}")
            return jsonify({
                "code": 500,
                "message": str(e)
            }), 500

def log_system_resources():
    """
    Logs system resource usage and upload progress at regular intervals.
    """
    while True:
        # Get memory and disk usage
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')

        with uploads_lock:
            for progress in active_uploads:
                with progress.lock:
                    # Calculate the percentage uploaded
                    percentage = (progress.bytes_uploaded / progress.total_size) * 100 if progress.total_size > 0 else 0
                    elapsed_time = time.time() - progress.start_time

                    # Log upload progress every 1%
                    if int(percentage) >= progress.last_logged_percentage + 1:
                        progress.last_logged_percentage = int(percentage)
                        logger.info(
                            f"Job {progress.job_id}: Uploaded {progress.bytes_uploaded} of {progress.total_size} bytes "
                            f"({percentage:.2f}%), Elapsed Time: {int(elapsed_time)} seconds"
                        )

                    # Log system resource usage every 5%
                    if int(percentage) >= progress.last_logged_resource_percentage + 5:
                        progress.last_logged_resource_percentage = int(percentage)
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        logger.info(f"[{current_time}] Memory Usage: {memory_info.percent}% used")
                        logger.info(f"[{current_time}] Disk Usage: {disk_info.percent}% used")

        # Sleep for 1 second before the next update
        time.sleep(1)

# Start the resource logging in a separate thread
resource_logging_thread = threading.Thread(
    target=log_system_resources,
    daemon=True
)
resource_logging_thread.start()
