import os
import json
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.cloud import storage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load credentials from environment variable
GCP_SA_CREDENTIALS = os.getenv('GCP_SA_CREDENTIALS')
GDRIVE_USER = os.getenv('GDRIVE_USER')
STORAGE_PATH = os.getenv('STORAGE_PATH', '/tmp/')
GCP_BUCKET_NAME = os.getenv('GCP_BUCKET_NAME')
GDRIVE_FOLDER_ID = os.getenv('GDRIVE_FOLDER_ID')

drive_service = None
gcs_client = None  # Ensure gcs_client is defined globally

if GCP_SA_CREDENTIALS:
    try:
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(GCP_SA_CREDENTIALS),
            scopes=['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/devstorage.full_control']
        )

        if GDRIVE_USER:
            logger.info("Initializing Google Drive service...")
            drive_service = build('drive', 'v3', credentials=credentials)
            logger.info("Google Drive service initialized successfully.")

        if GCP_BUCKET_NAME:
            logger.info("Initializing Google Cloud Storage client...")
            gcs_client = storage.Client(credentials=credentials)  # Correctly initialize gcs_client
            logger.info("Google Cloud Storage client initialized successfully.")

    except Exception as e:
        logger.error(f"Failed to initialize cloud services: {e}")
else:
    logger.warning("No cloud credentials provided. Using local storage only.")

def upload_to_gdrive(file_path, file_name):
    if drive_service:
        try:
            logger.info(f"Uploading {file_name} to Google Drive...")

            file_metadata = {'name': file_name}
            if GDRIVE_FOLDER_ID:
                file_metadata['parents'] = [GDRIVE_FOLDER_ID]

            media = MediaFileUpload(file_path, mimetype='application/octet-stream')

            uploaded_file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            # Get the file ID
            file_id = uploaded_file.get('id')

            # Set permissions to allow anyone with the link to view
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            drive_service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()

            logger.info(f"File {file_name} uploaded to Google Drive with ID: {file_id}")
            return f"https://drive.google.com/file/d/{file_id}/view"

        except Exception as e:
            logger.error(f"Failed to upload {file_name} to Google Drive: {e}")
            return None
    else:
        logger.warning("Google Drive service is not initialized. Skipping upload.")
        return None


def upload_to_gcs(file_path, bucket_name, blob_name=None):
    if gcs_client:
        try:
            # Preserve the original file extension or allow specifying blob_name
            if blob_name is None:
                blob_name = os.path.basename(file_path) 

            bucket = gcs_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            logger.info(f"Uploading {file_path} to Google Cloud Storage bucket {bucket_name} at root level...")
            blob.upload_from_filename(file_path)
            
            public_url = f"https://storage.googleapis.com/{bucket_name}/{blob_name}"
            
            logger.info(f"File {blob_name} uploaded to Google Cloud Storage with public URL: {public_url}")
            return public_url
        except Exception as e:
            logger.error(f"Failed to upload {file_path} to Google Cloud Storage: {e}")
            return None
    else:
        logger.warning("Google Cloud Storage client is not initialized. Skipping upload.")
        return None

def move_to_local_storage(file_path, file_name):
    try:
        local_file_path = os.path.join(STORAGE_PATH, file_name)
        if not os.path.exists(file_path):
            logger.error(f"File {file_path} does not exist.")
            return None
        
        os.rename(file_path, local_file_path)
        logger.info(f"File {file_name} moved to local storage at {local_file_path}")
        return local_file_path
    except Exception as e:
        logger.error(f"Failed to move {file_name} to local storage: {e}")
        return None
