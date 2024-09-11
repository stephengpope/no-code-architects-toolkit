from flask import Blueprint, request, jsonify
from flask import current_app
import uuid
import threading
import logging
from services.audio_mixing import process_audio_mixing
from services.authentication import authenticate
from services.webhook import send_webhook
from services.gdrive_service import upload_to_gcs  # Ensure this import is present

audio_mixing_bp = Blueprint('audio_mixing', __name__)
logger = logging.getLogger(__name__)

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
    id = data.get('id')

    if not video_url or not audio_url:
        return jsonify({"message": "Missing video_url or audio_url parameter"}), 400

    job_id = str(uuid.uuid4())
    current_app.logger.info(f"Job {job_id}: Received audio mixing request for {video_url} and {audio_url}")

    # Explicitly pass the app to the thread
    app = current_app._get_current_object()

    def process_job():
        with app.app_context():  # Pass the app context explicitly
            try:
                output_filename = process_audio_mixing(
                    video_url, audio_url, video_vol, audio_vol, output_length, job_id, webhook_url
                )
                gcs_url = upload_to_gcs(output_filename)
                if webhook_url:
                    send_webhook(webhook_url, {
                        "endpoint": "/audio-mixing",
                        "id": id,
                        "response": gcs_url,
                        "code": 200,
                        "message": "success"
                    })
            except Exception as e:
                current_app.logger.error(f"Job {job_id}: Error during processing - {e}")
                if webhook_url:
                    send_webhook(webhook_url, {
                        "endpoint": "/audio-mixing",
                        "id": id,
                        "response": None,
                        "code": 500,
                        "message": str(e)
                    })

    # Start the thread with the app context passed
    threading.Thread(target=process_job, daemon=True).start()
    return jsonify({"message": "processing"}), 202