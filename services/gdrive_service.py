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
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']
GCS_SCOPES = ['https://www.googleapis.com/auth/devstorage.full_control']

# Initialize Google Cloud Storage client with explicit credentials if provided
if GCP_SA_CREDENTIALS:
    credentials_info = json.loads(GCP_SA_CREDENTIALS)
    drive_credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=DRIVE_SCOPES,
        subject=GDRIVE_USER  # Impersonate the user
    )
    gcs_credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=GCS_SCOPES
    )
    gcs_client = storage.Client(credentials=gcs_credentials)
else:
    drive_credentials = None
    gcs_client = storage.Client()

# Check if the service account can impersonate the GDRIVE_USER
def check_impersonation_access():
    try:
        service = build('drive', 'v3', credentials=drive_credentials)
        # Attempt to list files in the user's Google Drive
        results = service.files().list(pageSize=1, fields="files(id, name)").execute()
        logger.info(f"Impersonation check successful. Found {len(results.get('files', []))} files.")
    except Exception as e:
        logger.error(f"Impersonation check failed: {e}")
        raise Exception("Service account does not have access to impersonate the GDRIVE_USER.")

# Perform the impersonation access check
check_impersonation_access()

def download_file(file_url, storage_path):
    try:
        logger.info(f"Downloading file from URL: {file_url}")
        response = requests.get(file_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        file_path = os.path.join(storage_path, file_url.split('/')[-1])
        with open(file_path, 'wb') as file:
            file.write(response.content)
        logger.info(f"File downloaded successfully to: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise

def upload_to_gdrive(file_path, filename, folder_id):
    try:
        logger.info(f"Uploading file to Google Drive: {file_path}")
        service = build('drive', 'v3', credentials=drive_credentials)
        
        # File metadata, with the folder ID where the file should be stored
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        logger.info(f"File uploaded successfully with ID: {file_id}")

        # Change ownership to the GDRIVE_USER after upload
        logger.info(f"Transferring ownership of the file to {GDRIVE_USER}")
        change_file_owner(service, file_id, GDRIVE_USER)  # Transfer ownership

        return file_id
    except Exception as e:
        logger.error(f"Error uploading file to Google Drive: {e}")
        raise

def set_file_public(service, file_id):
    try:
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        service.permissions().create(fileId=file_id, body=permission).execute()
        logger.info(f"Permissions set to public for file/folder ID: {file_id}")
    except Exception as e:
        logger.error(f"Error setting permissions: {e}")
        raise

def set_file_permissions(service, file_id, email):
    try:
        permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': email
        }
        service.permissions().create(fileId=file_id, body=permission, sendNotificationEmail=False).execute()
        logger.info(f"Full permissions granted to {email} for file/folder ID: {file_id}")
    except Exception as e:
        logger.error(f"Error setting permissions for {email}: {e}")
        raise

def change_file_owner(service, file_id, new_owner_email):
    try:
        logger.info(f"Changing owner of file ID: {file_id} to {new_owner_email}")
        permission = {
            'type': 'user',
            'role': 'owner',
            'emailAddress': new_owner_email
        }
        service.permissions().create(
            fileId=file_id,
            body=permission,
            transferOwnership=True
        ).execute()
        logger.info(f"Ownership transferred to {new_owner_email} for file ID: {file_id}")
    except Exception as e:
        logger.error(f"Error changing owner to {new_owner_email}: {e}")
        raise

def change_folder_files_owner(service, folder_id, new_owner_email):
    try:
        logger.info(f"Changing owner of all files in folder ID: {folder_id} to {new_owner_email}")
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        for file in files:
            change_file_owner(service, file['id'], new_owner_email)
        logger.info(f"Ownership transferred to {new_owner_email} for all files in folder ID: {folder_id}")
    except Exception as e:
        logger.error(f"Error changing owner for files in folder {folder_id}: {e}")
        raise

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

def move_to_local_storage(file_url, local_path):
    try:
        logger.info(f"Moving file from URL: {file_url} to local storage: {local_path}")
        response = requests.get(file_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        with open(local_path, 'wb') as file:
            file.write(response.content)
        logger.info(f"File moved successfully to: {local_path}")
        return local_path
    except Exception as e:
        logger.error(f"Error moving file to local storage: {e}")
        raise

def process_gdrive_upload(file_url, filename, folder_id, webhook_url, job_id):
    try:
        # Download the file from the provided URL
        file_path = download_file(file_url, STORAGE_PATH)
        
        # Upload the file to Google Drive
        file_id = upload_to_gdrive(file_path, filename, folder_id)
        
        # Get the public URL of the uploaded file
        service = build('drive', 'v3', credentials=drive_credentials)
        set_file_public(service, file_id)
        
        # Send success webhook if applicable
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/media-to-mp3",
                "id": job_id,
                "response": file_id,  # Return file_id instead of URL
                "code": 200,
                "message": "success"
            })
        
        return file_id

    except Exception as e:
        logger.error(f"Job {job_id}: Error during processing - {e}")
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/media-to-mp3",
                "id": job_id,
                "message": str(e),
                "code": 500,
                "message": "failed"
            })
        return None

    finally:
        logger.info(f"Job {job_id}: Exiting process_gdrive_upload function.")