from flask import Blueprint, jsonify, request
import logging
from app_utils import validate_payload, queue_task_wrapper
from services.v1.storage.gcp.upload import upload_file_service
from services.authentication import authenticate

v1_media_upload_bp = Blueprint('v1_media_upload', __name__)
logger = logging.getLogger(__name__)

@v1_media_upload_bp.route('/v1/storage/gcp/upload', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "file_url": {"type": "string", "format": "uri"},
        "file_name": {"type": "string"},
        "bucket_name": {"type": "string"},
        "content_type": {"type": "string"}
    },
    "required": ["file_url"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)  # Add the queue_task_wrapper decorator
def upload_media_v1(job_id, data):
    """
    Handles the media upload to GCP storage.

    Parameters:
        job_id (str): Unique identifier for the job.
        data (dict): Parsed JSON payload from the request.

    Returns:
        tuple: (response, endpoint, status_code)
    """
    file_url = data.get('file_url')
    file_name = data.get('file_name')
    bucket_name = data.get('bucket_name')  # Optional bucket name
    content_type = data.get('content_type')

    logger.info(f"Job {job_id}: Received media upload request for {file_url}")

    try:
        # Call the service to handle the file upload
        uploaded_file_url = upload_file_service(
            file_url=file_url,
            file_name=file_name,
            bucket_name=bucket_name,
            content_type=content_type
        )

        logger.info(f"Job {job_id}: File uploaded successfully: {uploaded_file_url}")
        return uploaded_file_url, "/v1/storage/gcp/upload", 200  # Successful response

    except Exception as e:
        logger.error(f"Job {job_id}: Error uploading file: {str(e)}", exc_info=True)
        return str(e), "/v1/storage/gcp/upload", 500  # Error response