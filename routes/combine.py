from flask import Blueprint, request, jsonify
import uuid
from services.ffmpeg_processing import process_video_combination
from services.authentication import authenticate
from services.webhook import send_webhook
import threading
import logging

combine_bp = Blueprint('combine', __name__)
logger = logging.getLogger(__name__)

def process_and_notify(media_urls, webhook_url, id, job_id):
    try:
        output_filename = process_video_combination(media_urls, job_id)
        
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/combine-videos",
                "id": id,
                "response": output_filename,
                "code": 200,
                "message": "success"
            })
    except Exception as e:
        logger.error(f"Job {job_id}: Error during processing - {e}")
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/combine-videos",
                "id": id,
                "error": str(e),
                "code": 500,
                "message": "failed"
            })

@combine_bp.route('/combine-videos', methods=['POST'])
@authenticate
def combine_videos():
    data = request.json
    media_urls = data.get('media_urls')
    webhook_url = data.get('webhook_url')
    id = data.get('id')
    job_id = str(uuid.uuid4())

    logger.info(f"Received combine-videos request: media_urls={media_urls}, webhook_url={webhook_url}, id={id}")

    if not media_urls or not isinstance(media_urls, list):
        logger.error("Invalid or missing media_urls parameter in request")
        return jsonify({"error": "Invalid or missing media_urls parameter"}), 400

    if webhook_url and not id:
        logger.warning("id is missing when webhook_url is provided")
        return jsonify({"message": "It appears that the id is missing. Please review your API call and try again."}), 400

    if webhook_url:
        # Asynchronous processing
        threading.Thread(target=process_and_notify, args=(media_urls, webhook_url, id, job_id)).start()
        logger.info(f"Job {job_id}: Started asynchronous processing")
        return jsonify({"message": "processing"}), 202
    else:
        # Synchronous processing
        try:
            output_filename = process_video_combination(media_urls, job_id)
            logger.info(f"Job {job_id}: Combine-videos completed successfully")
            return jsonify({"response": output_filename, "message": "success"}), 200
        except Exception as e:
            logger.error(f"Job {job_id}: Error during synchronous processing - {e}")
            return jsonify({"message": str(e)}), 500
