from flask import Blueprint, request, jsonify
from services.authentication import authenticate
from services.ffmpeg_processing import process_video_combination

combine_bp = Blueprint('combine', __name__)

@combine_bp.route('/combine-videos', methods=['POST'])
@authenticate
def combine_videos():
    data = request.json
    media_urls = data.get('media_urls')
    webhook_url = data.get('webhook_url')

    if not media_urls or not isinstance(media_urls, list):
        return jsonify({"error": "Missing or invalid media_urls parameter"}), 400

    job_id = process_video_combination(media_urls, webhook_url)
    return jsonify({"job_id": job_id}), 202
