import os
import logging
from flask import Blueprint
from app_utils import *
from services.authentication import authenticate
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload
import json
import requests
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the blueprint
gdrive_upload_bp = Blueprint('gdrive_upload', __name__)

# Import settings from environment variables
STORAGE_PATH = "/tmp/"
GCP_SA_CREDENTIALS = os.getenv('GCP_SA_CREDENTIALS')
GDRIVE_USER = os.getenv('GDRIVE_USER')

# Create STORAGE_PATH if it doesn't exist
os.makedirs(STORAGE_PATH, exist_ok=True)

def get_gdrive_service():
    # Decode the service account credentials
    credentials_info = json.loads(GCP_SA_CREDENTIALS)
    credentials = Credentials.from_service_account_info(credentials_info, scopes=['https://www.googleapis.com/auth/drive'])

    # Impersonate the GDRIVE_USER
    delegated_credentials = credentials.with_subject(GDRIVE_USER)

    # Build and return the Google Drive API service
    return build('drive', 'v3', credentials=delegated_credentials)

def download_file(file_url, storage_path, chunk_size=8192):
    try:
        logger.info(f"Downloading file from URL: {file_url}")
        
        unique_filename = str(uuid.uuid4())
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
                        if total_size > 0:
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

        # Set chunksize to 10MB for efficient memory usage
        chunksize = 10 * 1024 * 1024  # 10MB

        media = MediaFileUpload(file_path, chunksize=chunksize, resumable=True)

        request = service.files().create(body=file_metadata, media_body=media, fields='id')

        response = None
        last_logged_percentage = 0
        while response is None:
            status, response = request.next_chunk()
            if status:
                percentage = int(status.progress() * 100)
                if percentage // 20 > last_logged_percentage // 20:  # Log every 20% instead of 10%
                    logger.info(f"Uploaded {percentage}% of file {filename}")
                    last_logged_percentage = percentage

        file_id = response.get('id')
        logger.info(f"File uploaded successfully with ID: {file_id}")

        return file_id
    except Exception as e:
        logger.error(f"Error uploading file to Google Drive: {e}")
        raise
    finally:
        # Ensure the temporary file is deleted after upload
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Temporary file {file_path} deleted.")

@gdrive_upload_bp.route('/gdrive-upload', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "file_url": {"type": "string", "format": "uri"},
        "filename": {"type": "string"},
        "folder_id": {"type": "string"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["file_url", "filename", "folder_id"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def gdrive_upload(job_id, data):
    file_url = data['file_url']
    filename = data['filename']
    folder_id = data['folder_id']
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    logger.info(f"Job {job_id}: Received Google Drive upload request for {file_url}")

    if not GDRIVE_USER:
        logger.error("GDRIVE_USER environment variable is not set")
        return "GDRIVE_USER environment variable is not set. Please set it up as an environment variable in Docker.", "/gdrive-upload", 400

    try:
        file_path = download_file(file_url, STORAGE_PATH)
        file_id = upload_to_gdrive(file_path, filename, folder_id)

        return file_id, "/gdrive-upload", 200
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error during Google Drive upload process - {str(e)}")
        return str(e), "/gdrive-upload", 500