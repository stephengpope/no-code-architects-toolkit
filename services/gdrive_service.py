import os
import base64
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from services.file_management import download_file, STORAGE_PATH

# Environment variables for Google Cloud authentication
GCP_SA_CREDENTIALS = os.environ.get('GCP_SA_CREDENTIALS', '')
GDRIVE_USER = os.environ.get('GDRIVE_USER', '')

USE_GDRIVE = GCP_SA_CREDENTIALS and GDRIVE_USER

if USE_GDRIVE:
    def get_gdrive_service():
        """Authenticate and return a Google Drive service client."""
        credentials_json = json.loads(base64.b64decode(GCP_SA_CREDENTIALS))
        credentials = service_account.Credentials.from_service_account_info(
            credentials_json,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        delegated_credentials = credentials.with_subject(GDRIVE_USER)
        return build('drive', 'v3', credentials=delegated_credentials)
else:
    def get_gdrive_service():
        raise RuntimeError("Google Drive service is not configured. Set GCP_SA_CREDENTIALS and GDRIVE_USER to enable it.")

def process_gdrive_upload(file_url, unique_filename, filename, folder_id, webhook_url=None, job_id=None):
    """Upload a file to Google Drive and optionally send a webhook notification."""
    try:
        local_file_path = download_file(file_url, os.path.join(STORAGE_PATH, unique_filename))

        if USE_GDRIVE:
            drive_service = get_gdrive_service()
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            media = MediaFileUpload(local_file_path, resumable=True)
            file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            file_id = file.get('id')

            os.remove(local_file_path)
            print(f"File uploaded to Google Drive: {filename}, File ID: {file_id}")

            if webhook_url:
                send_webhook(webhook_url, {
                    "endpoint": "/gdrive-upload",
                    "job_id": job_id,
                    "response": file_id,
                    "code": 200,
                    "message": "success"
                })

            return file_id
        else:
            print(f"File stored locally: {local_file_path} (Google Drive not configured)")
            return None

    except Exception as e:
        print(f"Error during file processing: {e}")
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/gdrive-upload",
                "job_id": job_id,
                "response": None,
                "code": 500,
                "message": str(e)
            })
        raise

def send_webhook(webhook_url, data):
    """Send a POST request to a webhook URL with the provided data."""
    import requests
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
        print(f"Webhook sent: {data}")
    except requests.RequestException as e:
        print(f"Webhook failed: {e}")
