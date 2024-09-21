from flask import Blueprint, request, jsonify
from flask import current_app
import uuid
import threading
import logging
from services.extract_keyframes import process_keyframe_extraction
from services.authentication import authenticate
from services.webhook import send_webhook
from services.gcp_toolkit import upload_to_gcs

extract_keyframes_bp = Blueprint('extract_keyframes', __name__)
logger = logging.getLogger(__name__)

@extract_keyframes_bp.route('/extract-keyframes', methods=['POST'])
@authenticate
def extract_keyframes():
    data = request.json
    video_url = data.get('video_url')
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    if not video_url:
        return jsonify({"message": "Missing video_url parameter"}), 400

    job_id = str(uuid.uuid4())
    current_app.logger.info(f"Job {job_id}: Received keyframe extraction request for {video_url}")

    app = current_app._get_current_object()

    def process_job():
        with app.app_context():
            try:
                image_urls = process_keyframe_extraction(video_url, job_id)
                response = [{"image_url": url} for url in image_urls]
                
                #print(f"Images: {response}")
                
                response = str({"image_urls": response})
                
                print(f"Images: {response}")

                if webhook_url:
                    send_webhook(webhook_url, {
                        "endpoint": "/extract-keyframes",
                        "code": 200,
                        "id": id,
                        "job_id": job_id,
                        "response": response,
                        "message": "success"
                    })
                else:
                    return jsonify({
                        "code": 200,
                        "id": id,
                        "job_id": job_id,
                        "response": jsonify(response),
                        "message": "success"
                    })
            except Exception as e:
                current_app.logger.error(f"Job {job_id}: Error during processing - {e}")
                error_response = {
                    "endpoint": "/extract-keyframes",
                    "code": 500,
                    "id": id,
                    "job_id": job_id,
                    "response": None,
                    "message": str(e)
                }
                if webhook_url:
                    send_webhook(webhook_url, error_response)
                else:
                    return jsonify(error_response), 500

    threading.Thread(target=process_job, daemon=True).start()
    return jsonify(
        {
            "code": 202,
            "id": data.get("id"),
            "job_id": job_id,
            "message": "processing"
        }
    ), 202