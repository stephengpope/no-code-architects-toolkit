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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the blueprint
gdrive_upload_bp = Blueprint('gdrive_upload', __name__)

# Import settings from environment variables
STORAGE_PATH = os.getenv('STORAGE_PATH')
GCP_SA_CREDENTIALS = os.getenv('GCP_SA_CREDENTIALS')
GDRIVE_USER = os.getenv('GDRIVE_USER')

def download_file(file_url, storage_path):
    try:
        logger.info(f"Downloading file from URL: {file_url}")
        response = requests.get(file_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        file_path = f"{storage_path}/{file_url.split('/')[-1]}"
        with open(file_path, 'wb') as file:
            file.write(response.content)
        logger.info(f"File downloaded successfully to: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise

def get_or_create_folder(service, folder_name):
    try:
        # Search for the folder by name
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        
        if items:
            # Folder found, return the first match
            folder_id = items[0]['id']
            logger.info(f"Folder '{folder_name}' found with ID: {folder_id}")
        else:
            # Folder not found, create it
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = service.files().create(body=file_metadata, fields='id').execute()
            folder_id = folder.get('id')
            logger.info(f"Folder '{folder_name}' created with ID: {folder_id}")
        
        # Set folder permissions to be publicly accessible and to the specific user
        set_file_public(service, folder_id)
        set_file_permissions(service, folder_id, GDRIVE_USER)
        
        return folder_id
    except Exception as e:
        logger.error(f"Error getting or creating folder: {e}")
        raise

def upload_to_gdrive(file_path, filename, folder_name):
    try:
        logger.info(f"Uploading file to Google Drive: {file_path}")
        credentials_info = json.loads(GCP_SA_CREDENTIALS)
        credentials = Credentials.from_service_account_info(credentials_info)
        service = build('drive', 'v3', credentials=credentials)
        
        # Get or create the folder
        folder_id = get_or_create_folder(service, folder_name)
        
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        logger.info(f"File uploaded successfully with ID: {file_id}")
        
        # Set file permissions to be publicly accessible and to the specific user
        set_file_public(service, file_id)
        set_file_permissions(service, file_id, GDRIVE_USER)
        
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

def process_request(data, job_id):
    try:
        logger.info(f"Processing request with Job ID: {job_id}")
        file_path = download_file(data['file_url'], STORAGE_PATH)
        file_id = upload_to_gdrive(file_path, data['filename'], data['folder_id'])
        file_url = f"https://drive.google.com/file/d/{file_id}/view"
        
        if 'webhook_url' in data:
            webhook_payload = {
                'endpoint': '/gdrive-upload',
                'id': data['id'],
                'response': file_url,
                'code': 200,
                'message': 'success'
            }
            logger.info(f"Sending success webhook to: {data['webhook_url']}")
            requests.post(data['webhook_url'], json=webhook_payload)
        else:
            return jsonify({"response": file_url, "message": "success"}), 200
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        if 'webhook_url' in data:
            webhook_payload = {
                'endpoint': '/gdrive-upload',
                'id': data['id'],
                'response': None,
                'code': 500,
                'message': str(e)
            }
            logger.info(f"Sending failure webhook to: {data['webhook_url']}")
            requests.post(data['webhook_url'], json=webhook_payload)
        else:
            return jsonify({"message": str(e)}), 500

@gdrive_upload_bp.route('/gdrive-upload', methods=['POST'])
def gdrive_upload():
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
        threading.Thread(target=process_request, args=(data, job_id)).start()
        return jsonify({"message": "processing"}), 202
    else:
        return process_request(data, job_id)