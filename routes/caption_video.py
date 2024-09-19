from flask import Blueprint, request, jsonify
import uuid
import threading
import logging
from services.caption_video import process_captioning
from services.authentication import authenticate
from services.webhook import send_webhook

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

caption_bp = Blueprint('caption', __name__)

def process_job(data, job_id):
    try:
        logger.info(f"Job {job_id}: Starting captioning process")
        file_url = data['video_url']
        caption_srt = data['srt']
        options = data.get('options', {})

        output_filename = process_captioning(file_url, caption_srt, options, job_id)

        if 'webhook_url' in data:
            send_webhook(data['webhook_url'], {
                "endpoint": "/caption-video",
                "code": 200,
                "id": data.get("id"),
                "job_id": job_id,
                "response": output_filename,
                "message": "success"
            })

        logger.info(f"Job {job_id}: Captioning process completed successfully")
        return output_filename

    except Exception as e:
        logger.error(f"Job {job_id}: Error during processing - {e}")
        if 'webhook_url' in data:
            send_webhook(data['webhook_url'], {
                "endpoint": "/caption-video",
                "code": 500,
                "id": data.get("id"),
                "job_id": job_id,
                "response": None,
                "message": str(e),
            })
        else:
            raise

@caption_bp.route('/caption-video', methods=['POST'])
@authenticate
def caption_video():
    data = request.json

    if 'X-API-Key' not in request.headers:
        logger.error("Missing X-API-Key header")
        return jsonify({"message": "Missing X-API-Key header"}), 400

    if not all(k in data for k in ('video_url', 'srt')):
        logger.error("video_url and srt are required")
        return jsonify({"message": "video_url and srt are required"}), 400

    job_id = str(uuid.uuid4())
    logger.info(f"Processing Job ID: {job_id}")

    if 'webhook_url' in data:
        threading.Thread(target=process_job, args=(data, job_id)).start()
        return jsonify({
            "code": 202,
            "id": data.get("id"),
            "job_id": job_id,
            "message": "processing"
        }), 202
    else:
        try:
            output_filename = process_job(data, job_id)
            return jsonify({
                "code": 200,
                "response": output_filename,
                "message": "success"
            }), 200
        except Exception as e:
            logger.error(f"Job {job_id}: Error during synchronous processing - {e}")
            return jsonify({
                "code": 500,
                "message": str(e)
            }), 500