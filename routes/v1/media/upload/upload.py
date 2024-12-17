# routes/v1/media/upload/upload.py
from flask import Blueprint, request, jsonify
import jsonschema
from functools import wraps
import os
import requests
from google.auth.exceptions import GoogleAuthError
from services.v1.media.upload.upload import GCPStorageProvider

v1_media_upload_bp = Blueprint('v1_media_upload', __name__)

def validate_payload(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                jsonschema.validate(instance=request.json, schema=schema)
            except jsonschema.exceptions.ValidationError as e:
                return jsonify({"error": str(e)}), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@v1_media_upload_bp.route('/media/upload', methods=['POST'])
@validate_payload({
    "type": "object",
    "properties": {
        "file_url": {"type": ["string", "null"], "format": "uri"},
        "file_name": {"type": "string"},
        "bucket_name": {"type": "string"},
        "content_type": {"type": "string"}
    },
    "oneOf": [
        {"required": ["file_url", "file_name"]},
        {"required": ["file_name"]}
    ],
    "additionalProperties": False
})
def media_upload():
    try:
        file_url = request.json.get('file_url')
        file_name = request.json.get('file_name')
        bucket_name = request.json.get('bucket_name', os.getenv('GCP_BUCKET_NAME'))
        content_type = request.json.get('content_type')

        if 'file' in request.files:
            # Handle binary file upload
            file_data = request.files['file'].read()
            file_name = request.files['file'].filename
        elif file_url:
            # Handle file URL download and upload
            response = requests.get(file_url)
            response.raise_for_status()  # Raise an error for bad responses
            file_data = response.content
        else:
            return jsonify({"error": "Either 'file' or 'file_url' must be provided"}), 400

        gcp_storage_provider = GCPStorageProvider()
        blob_name = gcp_storage_provider.upload_file(file_data, file_name)

        return jsonify({"bucket_name": bucket_name, "blob_name": blob_name}), 200

    except requests.RequestException as e:
        return jsonify({"error": f"Error downloading file from URL: {str(e)}"}), 500
    except GoogleAuthError as e:
        return jsonify({"error": f"Google Authentication Error: {str(e)}"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500