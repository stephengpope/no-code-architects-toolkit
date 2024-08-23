from flask import Blueprint, request, jsonify
import uuid
from services.transcription import process_transcription
from services.authentication import authenticate

transcribe_bp = Blueprint('transcribe', __name__)

@transcribe_bp.route('/transcribe', methods=['POST'])
@authenticate
def transcribe_media():
    data = request.json
    job_id = str(uuid.uuid4())  # Generate a job ID for tracking (optional)
    print(f"Processing Job ID: {job_id}")

    try:
        # Call the transcription process directly
        result = process_transcription(data['media_url'], data['output'])
        return jsonify({"job_id": job_id, "result": result}), 200
    except Exception as e:
        return jsonify({"job_id": job_id, "error": str(e)}), 500
