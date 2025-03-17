from flask import Blueprint, request, jsonify
from services.authentication import authenticate
from app_utils import validate_payload, queue_task_wrapper
from services.v1.s3.upload import stream_upload_to_s3
import os
import json
import logging

logger = logging.getLogger(__name__)
v1_s3_upload_bp = Blueprint('v1_s3_upload', __name__)

@v1_s3_upload_bp.route('/v1/s3/upload', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "file_url": {"type": "string", "format": "uri"},
        "filename": {"type": "string"},
        "public": {"type": "boolean"}
    },
    "required": ["file_url"]
})
@queue_task_wrapper(bypass_queue=False)
def s3_upload_endpoint(job_id, data):
    try:
        file_url = data.get('file_url')
        filename = data.get('filename')  # Optional, will default to original filename if not provided
        make_public = data.get('public', False)  # Default to private
        
        logger.info(f"Job {job_id}: Starting S3 streaming upload from {file_url}")
        
        # Call the service function to handle the upload
        result = stream_upload_to_s3(file_url, filename, make_public)
        
        logger.info(f"Job {job_id}: Successfully uploaded to S3")
        
        return result, "/v1/s3/upload", 200
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error streaming upload to S3 - {str(e)}")
        return str(e), "/v1/s3/upload", 500