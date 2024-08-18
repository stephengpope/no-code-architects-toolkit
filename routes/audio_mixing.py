from flask import Blueprint, request, jsonify
from services.authentication import authenticate
from services.ffmpeg_processing import process_audio_mixing

audio_mixing_bp = Blueprint('audio_mixing', __name__)

@audio_mixing_bp.route('/audio-mixing', methods=['POST'])
@authenticate
def audio_mixing():
    data = request.json
    video_url = data.get('video_url')
    audio_url = data.get('audio_url')
    video_vol = data.get('video_vol', 100)
    audio_vol = data.get('audio_vol', 100)
    output_length = data.get('output_length', 'video')
    webhook_url = data.get('webhook_url')

    if not video_url or not audio_url:
        return jsonify({"error": "Missing video_url or audio_url parameter"}), 400

    job_id = process_audio_mixing(video_url, audio_url, video_vol, audio_vol, output_length, webhook_url)
    return jsonify({"job_id": job_id}), 202
