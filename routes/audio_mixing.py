from flask import Blueprint, request, jsonify
from flask import current_app
from queue_utils import *
import uuid
import threading
import logging
from services.audio_mixing import process_audio_mixing
from services.authentication import authenticate
from services.webhook import send_webhook
from services.gcp_toolkit import upload_to_gcs  # Ensure this import is present

audio_mixing_bp = Blueprint('audio_mixing', __name__)
logger = logging.getLogger(__name__)

@audio_mixing_bp.route('/audio-mixing', methods=['POST'])
@authenticate
@validate_payload('video_url', 'audio_url')
@queue_task_wrapper(bypass_queue=False)
def audio_mixing(job_id, data):
    
    video_url = data.get('video_url')
    audio_url = data.get('audio_url')
    video_vol = data.get('video_vol', 100)
    audio_vol = data.get('audio_vol', 100)
    output_length = data.get('output_length', 'video')
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    logger.info(f"Job {job_id}: Received audio mixing request for {video_url} and {audio_url}")

    try:
        output_filename = process_audio_mixing(
            video_url, audio_url, video_vol, audio_vol, output_length, job_id, webhook_url
        )
        gcs_url = upload_to_gcs(output_filename)

        response_json = {
            "endpoint": "/audio-mixing",
            "code": 200,
            "id": id,
            "job_id": job_id,
            "response": gcs_url,
            "message": "success"
        }

        if webhook_url:
            send_webhook(webhook_url, response_json)
        else:
            return response_json, 200
    except Exception as e:
        
        response_json = {
            "endpoint": "/audio-mixing",
            "code": 500,
            "id": id,
            "job_id": job_id,
            "response": None,
            "message": str(e)
        }

        current_app.logger.error(f"Job {job_id}: Error during processing - {e}")
        
        if webhook_url:
            send_webhook(webhook_url, response_json)
        else:
            return response_json, 200

