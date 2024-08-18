from flask import Blueprint, request, jsonify
from services.authentication import authenticate
from services.gdrive_service import process_gdrive_upload

gdrive_upload_bp = Blueprint('gdrive_upload', __name__)

@gdrive_upload_bp.route('/gdrive-upload', methods=['POST'])
@authenticate
def gdrive_upload():
    data = request.json
    file_url = data.get('file_url')
    filename = data.get('filename')
    folder_id = data.get('folder_id')
    webhook_url = data.get('webhook_url')

    if not file_url or not filename or not folder_id:
        return jsonify({"error": "Missing file_url, filename, or folder_id parameter"}), 400

    job_id = process_gdrive_upload(file_url, filename, folder_id, webhook_url)
    return jsonify({"job_id": job_id}), 202
