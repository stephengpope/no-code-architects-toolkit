from flask import Blueprint, request, jsonify
from services.authentication import authenticate
from services.whisper_transcription import process_transcription

transcribe_bp = Blueprint('transcribe', __name__)

@transcribe_bp.route('/transcribe-media', methods=['POST'])
@authenticate
def transcribe_media():
    data = request.json
    media_url = data.get('media_url')
    output_type = data.get('output')
    webhook_url = data.get('webhook_url')

    if not media_url or not output_type:
        return jsonify({"error": "Missing media_url or output parameter"}), 400

    job_id = process_transcription(media_url, output_type, webhook_url)
    return jsonify({"job_id": job_id}), 202
