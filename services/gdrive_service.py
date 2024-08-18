import os
import uuid
import base64
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from services.webhook import send_webhook
from services.file_management import download_file, STORAGE_PATH
from config import GCP_SA_CREDENTIALS, GDRIVE_USER

def get_gdrive_service():
    """
    Authenticate and return a Google Drive service object.
    """
    # Decode the base64-encoded service account credentials
    credentials_json = json.loads(base64.b64decode(GCP_SA_CREDENTIALS))
    
    # Create credentials object
    credentials = service_account.Credentials.from_service_account_info(
        credentials_json,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    
    # Delegate the credentials to the specified user
    delegated_credentials = credentials.with_subject(GDRIVE_USER)
    
    # Build and return the Google Drive service object
    return build('drive', 'v3', credentials=delegated_credentials)

def process_gdrive_upload(file_url, filename, folder_id, webhook_url):
    """
    Download a file from a URL and upload it to a specified Google Drive folder.

    :param file_url: URL of the file to download
    :param filename: Name of the file to be saved on Google Drive
    :param folder_id: Google Drive folder ID where the file will be uploaded
    :param webhook_url: Optional URL to send a webhook notification upon completion
    :return: The Google Drive file ID of the uploaded file
    """
    try:
        # Generate a unique job ID
        job_id = str(uuid.uuid4())
        
        # Download the file from the given URL
        local_file_path = download_file(file_url, os.path.join(STORAGE_PATH, f"{job_id}_{filename}"))
        
        # Get the Google Drive service object
        drive_service = get_gdrive_service()
        
        # Define the metadata for the file upload
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        
        # Create a MediaFileUpload object for the file to be uploaded
        media = MediaFileUpload(local_file_path, resumable=True)
        
        # Upload the file to Google Drive and get the file ID
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')

        # Clean up the local file after upload
        os.remove(local_file_path)

        # Send a webhook notification if a webhook URL is provided
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/gdrive-upload",
                "job_id": job_id,
                "response": file_id,
                "code": 200,
                "message": "success"
            })

        # Return the Google Drive file ID
        return file_id
    except Exception as e:
        # Send a failure webhook notification if an error occurs
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/gdrive-upload",
                "job_id": None,
                "response": None,
                "code": 500,
                "message": str(e)
            })
        # Raise the exception to propagate the error
        raise
