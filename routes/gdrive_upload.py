from flask import Blueprint, request, jsonify
import uuid
from services.gdrive_service import process_gdrive_upload
from services.authentication import authenticate

gdrive_upload_bp = Blueprint('gdrive_upload', __name__)

@gdrive_upload_bp.route('/gdrive-upload', methods=['POST'])
@authenticate
def gdrive_upload():
    data = request.json
    job_id = str(uuid.uuid4())  # Generate a job ID for tracking (optional)
    print(f"Processing Job ID: {job_id}")

    try:
        # Call the Google Drive upload process directly
        file_id = process_gdrive_upload(
            data['file_url'], f"{job_id}_{data['filename']}", data['filename'], data['folder_id'], data.get('webhook_url'), job_id
        )
        return jsonify({"job_id": job_id, "file_id": file_id}), 200
    except Exception as e:
        return jsonify({"job_id": job_id, "error": str(e)}), 500
