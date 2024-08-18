from flask import Blueprint, request, jsonify
from services.authentication import authenticate
from services.ffmpeg_processing import process_conversion

convert_bp = Blueprint('convert', __name__)

@convert_bp.route('/convert-media-to-mp3', methods=['POST'])
@authenticate
def convert_media_to_mp3():
    data = request.json
    media_url = data.get('media_url')
    webhook_url = data.get('webhook_url')

    if not media_url:
        return jsonify({"error": "Missing media_url parameter"}), 400

    job_id = process_conversion(media_url, webhook_url)
    return jsonify({"job_id": job_id}), 202
