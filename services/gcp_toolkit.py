import os
import requests
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.cloud import storage
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import settings from environment variables
STORAGE_PATH =  "/tmp/"
GCP_SA_CREDENTIALS = os.getenv('GCP_SA_CREDENTIALS')
GDRIVE_USER = os.getenv('GDRIVE_USER')
GCP_BUCKET_NAME = os.getenv('GCP_BUCKET_NAME')

# Define the required scopes
GCS_SCOPES = ['https://www.googleapis.com/auth/devstorage.full_control']

# Initialize Google Cloud Storage client with explicit credentials if provided
if GCP_SA_CREDENTIALS:
    credentials_info = json.loads(GCP_SA_CREDENTIALS)
    
    gcs_credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=GCS_SCOPES
    )
    gcs_client = storage.Client(credentials=gcs_credentials)
else:
    drive_credentials = None
    gcs_client = storage.Client()

def upload_to_gcs(file_path, bucket_name=GCP_BUCKET_NAME):
    try:
        logger.info(f"Uploading file to Google Cloud Storage: {file_path}")
        bucket = gcs_client.bucket(bucket_name)
        blob = bucket.blob(os.path.basename(file_path))
        blob.upload_from_filename(file_path)
        logger.info(f"File uploaded successfully to GCS: {blob.public_url}")
        return blob.public_url
    except Exception as e:
        logger.error(f"Error uploading file to GCS: {e}")
        raise
