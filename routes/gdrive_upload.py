import os
import logging
from flask import Blueprint, request, jsonify
import threading
import requests
import uuid
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload
import json
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the blueprint
gdrive_upload_bp = Blueprint('gdrive_upload', __name__)

# Import settings from environment variables
STORAGE_PATH ="/tmp/"
GCP_SA_CREDENTIALS = os.getenv('GCP_SA_CREDENTIALS')
GDRIVE_USER = os.getenv('GDRIVE_USER')

def get_gdrive_service():
    # Decode the service account credentials
    credentials_info = json.loads(GCP_SA_CREDENTIALS)
    credentials = Credentials.from_service_account_info(credentials_info, scopes=['https://www.googleapis.com/auth/drive'])

    # Impersonate the GDRIVE_USER
    delegated_credentials = credentials.with_subject(GDRIVE_USER)

    # Build and return the Google Drive API service
    return build('drive', 'v3', credentials=delegated_credentials)

def generate_unique_filename(original_filename):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_string = uuid.uuid4().hex[:6]
    file_extension = os.path.splitext(original_filename)[1]
    return f"{timestamp}_{random_string}{file_extension}"

def download_file(file_url, storage_path, chunk_size=8192):
    try:
        logger.info(f"Downloading file from URL: {file_url}")
        
        unique_filename = generate_unique_filename(file_url.split('/')[-1])
        temp_file_path = os.path.join(storage_path, unique_filename)

        # Download file
        with requests.get(file_url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            downloaded_size = 0
            last_logged_percentage = 0

            with open(temp_file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        percentage = int((downloaded_size / total_size) * 100)
                        if percentage // 10 > last_logged_percentage // 10:
                            logger.info(f"Downloaded {percentage}% of the file from {file_url}")
                            last_logged_percentage = percentage

        logger.info(f"File downloaded successfully to: {temp_file_path} from {file_url}")
        return temp_file_path
    except Exception as e:
        logger.error(f"Error downloading file from {file_url}: {e}")
        raise

def upload_to_gdrive(file_path, filename, folder_id):
    try:
        logger.info(f"Uploading file to Google Drive: {file_path}")

        # Get the Google Drive service with impersonation
        service = get_gdrive_service()

        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        logger.info(f"File uploaded successfully with ID: {file_id}")

        return file_id
    except Exception as e:
        logger.error(f"Error uploading file to Google Drive: {e}")
        raise

def process_job(data, job_id):
    try:
        logger.info(f"Processing request with Job ID: {job_id}")
        file_path = download_file(data['file_url'], STORAGE_PATH)
        file_id = upload_to_gdrive(file_path, data['filename'], data['folder_id'])
        file_url = f"https://drive.google.com/file/d/{file_id}/view"

        if 'webhook_url' in data:
            webhook_payload = {
                'endpoint': '/gdrive-upload',
                'code': 200,
                'id': data.get("id"),
                'job_id': job_id,
                'response': file_id,
                'message': 'success'
            }
            logger.info(f"Sending success webhook to: {data['webhook_url']}")
            requests.post(data['webhook_url'], json=webhook_payload)
        else:
            return file_id

    except Exception as e:

        logger.error(f"Error processing request: {e}")
        if 'webhook_url' in data:
            webhook_payload = {
                'endpoint': '/gdrive-upload',
                'code': 500,
                'id': data['id'],
                'job_id': job_id,
                'response': None,
                'message': str(e)
            }
            logger.info(f"Sending failure webhook to: {data['webhook_url']}")
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
        return jsonify({"message": "GDRIVE_USER environment variable is not set. Please set it up as an environment variable in Docker."}), 400

    data = request.json
    if not all(k in data for k in ('file_url', 'filename', 'folder_id')):
        logger.error("file_url, filename, and folder_id are required")
        return jsonify({"message": "file_url, filename, and folder_id are required"}), 400

    job_id = str(uuid.uuid4())
    logger.info(f"Processing Job ID: {job_id}")

    if 'webhook_url' in data:
        threading.Thread(target=process_job, args=(data, job_id)).start()
        return jsonify(
            {
                "code": 202,
                "id": data.get("id"),
                "job_id": job_id,
                "message": "processing"
            }
        ), 202
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
