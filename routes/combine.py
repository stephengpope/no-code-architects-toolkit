from flask import Blueprint, request, jsonify
import uuid
from services.ffmpeg_processing import process_video_combination
from services.authentication import authenticate

combine_bp = Blueprint('combine', __name__)

@combine_bp.route('/combine-videos', methods=['POST'])
@authenticate
def combine_videos():
    data = request.json
    job_id = str(uuid.uuid4())  # Generate a job ID for tracking (optional)
    print(f"Processing Job ID: {job_id}")

    try:
        # Call the video combination process directly
        output_filename = process_video_combination(data['media_urls'], job_id)
        return jsonify({"job_id": job_id, "output_filename": output_filename}), 200
    except Exception as e:
        return jsonify({"job_id": job_id, "error": str(e)}), 500
