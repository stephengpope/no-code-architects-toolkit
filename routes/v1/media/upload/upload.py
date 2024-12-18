from flask import Blueprint, jsonify, request
import logging
from app_utils import validate_payload, queue_task_wrapper
from services.v1.media.upload.upload import upload_file_service
from services.authentication import authenticate

v1_media_upload_bp = Blueprint('v1_media_upload', __name__)
logger = logging.getLogger(__name__)

@v1_media_upload_bp.route('/v1/media/upload', methods=['POST'])
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
def upload_media_v1():
    data = request.get_json()
    file_url = data.get('file_url')
    file_name = data.get('file_name')
    bucket_name = data.get('bucket_name')  # Optional bucket name
    content_type = data.get('content_type')

    logger.info(f"Received media upload request for {file_url}")

    try:
        uploaded_file_url = upload_file_service(
            file_url=file_url,
            file_name=file_name,
            bucket_name=bucket_name,
            content_type=content_type
        )

        logger.info(f"File uploaded successfully: {uploaded_file_url}")

        return jsonify({"file_url": uploaded_file_url}), 200

    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    