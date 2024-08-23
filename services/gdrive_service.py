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

# Load optional credentials from the environment variable
GCP_SA_CREDENTIALS = os.getenv('GCP_SA_CREDENTIALS')
GDRIVE_USER = os.getenv('GDRIVE_USER')
STORAGE_PATH = os.getenv('STORAGE_PATH', '/tmp/')
GCP_BUCKET_NAME = os.getenv('GCP_BUCKET_NAME')

drive_service = None
gcs_client = None

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
            gcs_client = storage.Client(credentials=credentials)
            logger.info("Google Cloud Storage client initialized successfully.")

    except Exception as e:
        logger.error(f"Failed to initialize cloud services: {e}")
else:
    logger.warning("No cloud credentials provided. Using local storage only.")

def upload_to_gdrive(file_path, file_name):
    if drive_service:
        try:
            logger.info(f"Uploading {file_name} to Google Drive...")

            # If you want to upload to a specific folder, replace [] with the folder ID
            file_metadata = {'name': file_name, 'parents': []}

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


def upload_to_gcs(file_path, bucket_name, blob_name):
    if gcs_client:
        try:
            # Correctly check if the file path exists only if it's a local path
            if not os.path.isfile(file_path):
                logger.error(f"Local file {file_path} does not exist before upload.")
                return None

            # Ensure the blob_name does not include any unintended directory structures like /tmp
            blob_name = os.path.basename(file_path)

            # Handle the case where the file might have an extra .mp3
            if blob_name.endswith('.mp3.mp3'):
                blob_name = blob_name.replace('.mp3.mp3', '.mp3')
            elif not blob_name.endswith('.mp3'):
                blob_name += '.mp3'

            bucket = gcs_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            logger.info(f"Uploading {file_path} to Google Cloud Storage bucket {bucket_name} at root level...")
            blob.upload_from_filename(file_path)
            
            # Generate the correct public URL
            public_url = f"https://storage.cloud.google.com/{bucket_name}/{blob_name}"
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
