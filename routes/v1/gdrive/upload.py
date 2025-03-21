from flask import Blueprint, request, jsonify
from services.authentication import authenticate
from app_utils import validate_payload, queue_task_wrapper
from services.v1.gdrive.upload import stream_upload_to_gdrive
import os
import json
import logging

logger = logging.getLogger(__name__)
v1_gdrive_upload_bp = Blueprint('v1_gdrive_upload', __name__)

@v1_gdrive_upload_bp.route('/v1/gdrive/upload', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "file_url": {"type": "string", "format": "uri"},
        "folder_id": {"type": "string"},
        "filename": {"type": "string"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["file_url", "folder_id"]
})
@queue_task_wrapper(bypass_queue=False)
def gdrive_upload_endpoint(job_id, data):
    try:
        file_url = data.get('file_url')
        folder_id = data.get('folder_id')
        filename = data.get('filename')  # Optional, will default to original filename if not provided
        webhook_url = data.get('webhook_url')  # Optional webhook URL
        
        # Get bearer token from the authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return "Missing or invalid Google Drive OAuth token in Authorization header", "/v1/gdrive/upload", 401
        
        # Extract the token from the header
        access_token = auth_header.split(' ')[1]
        
        logger.info(f"Job {job_id}: Starting Google Drive streaming upload from {file_url}")
        
        # Call the service function to handle the upload
        result = stream_upload_to_gdrive(file_url, folder_id, access_token, filename)
        
        logger.info(f"Job {job_id}: Successfully uploaded to Google Drive")
        
        return result, "/v1/gdrive/upload", 200
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error streaming upload to Google Drive - {str(e)}")
        return str(e), "/v1/gdrive/upload", 500