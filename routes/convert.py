from flask import Blueprint, request, jsonify
import uuid
from services.ffmpeg_processing import process_conversion
from services.authentication import authenticate

convert_bp = Blueprint('convert', __name__)

@convert_bp.route('/convert-media-to-mp3', methods=['POST'])
@authenticate
def convert_media_to_mp3():
    data = request.json
    job_id = str(uuid.uuid4())  # Generate a job ID for tracking (optional)
    print(f"Processing Job ID: {job_id}")

    try:
        # Call the conversion process directly
        output_filename = process_conversion(data['media_url'], job_id)
        return jsonify({"job_id": job_id, "output_filename": output_filename}), 200
    except Exception as e:
        return jsonify({"job_id": job_id, "error": str(e)}), 500
