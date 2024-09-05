from flask import Blueprint, request, jsonify
import uuid
from services.audio_mixing import process_audio_mixing  # Correct import
from services.authentication import authenticate

audio_mixing_bp = Blueprint('audio_mixing', __name__)

@audio_mixing_bp.route('/audio-mixing', methods=['POST'])
@authenticate
def audio_mixing():
    data = request.json
    job_id = str(uuid.uuid4())  # Generate a job ID for tracking (optional)
    print(f"Processing Job ID: {job_id}")

    try:
        # Call the audio mixing process directly
        output_filename = process_audio_mixing(
            data['video_url'], data['audio_url'], data.get('video_vol', 100),
            data.get('audio_vol', 100), data.get('output_length', 'video'), job_id
        )
        return jsonify({"job_id": job_id, "output_filename": output_filename}), 200
    except Exception as e:
        return jsonify({"job_id": job_id, "error": str(e)}), 500