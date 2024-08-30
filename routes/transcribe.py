from flask import Blueprint, request, jsonify, after_this_request
import uuid
import threading
import logging
import queue
from services.transcription import process_transcription
from services.authentication import authenticate
from services.webhook import send_webhook

transcribe_bp = Blueprint('transcribe', __name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a queue for transcription jobs
transcription_queue = queue.Queue()

def transcription_worker():
    while True:
        job = transcription_queue.get()
        try:
            process_and_notify(**job)
        except Exception as e:
            logger.error(f"Error processing job: {e}")
        finally:
            transcription_queue.task_done()

# Start the worker thread
worker_thread = threading.Thread(target=transcription_worker, daemon=True)
worker_thread.start()

def process_and_notify(**kwargs):
    media_url = kwargs['media_url']
    output = kwargs['output']
    webhook_url = kwargs['webhook_url']
    id = kwargs['id']
    job_id = kwargs['job_id']
    
    try:
        logger.info(f"Job {job_id}: Starting transcription process for {media_url}")
        result = process_transcription(media_url, output)
        logger.info(f"Job {job_id}: Transcription process completed successfully")

        if webhook_url:
            logger.info(f"Job {job_id}: Sending success webhook to {webhook_url}")
            send_webhook(webhook_url, {
                "endpoint": "/transcribe",
                "id": id,
                "response": result,
                "code": 200,
                "message": "success"
            })
    except Exception as e:
        logger.error(f"Job {job_id}: Error during transcription - {e}")
        if webhook_url:
            logger.info(f"Job {job_id}: Sending failure webhook to {webhook_url}")
            send_webhook(webhook_url, {
                "endpoint": "/transcribe",
                "id": id,
                "response": None,
                "code": 500,
                "message": str(e)
            })

@transcribe_bp.route('/transcribe', methods=['POST'])
@authenticate
def transcribe():
    data = request.json
    media_url = data.get('media_url')
    output = data.get('output', 'transcript').lower()
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    logger.info(f"Received transcription request: media_url={media_url}, output={output}, webhook_url={webhook_url}, id={id}")

    if not media_url:
        logger.error("Missing media_url parameter in request")
        return jsonify({"error": "Missing media_url parameter"}), 400

    # Check if either webhook_url or id is missing and return the appropriate message
    if webhook_url and not id:
        logger.warning("id is missing when webhook_url is provided")
        return jsonify({"message": "It appears that the id is missing. Please review your API call and try again."}), 500
    elif id and not webhook_url:
        logger.warning("webhook_url is missing when id is provided")
        return jsonify({"message": "It appears that the webhook_url is missing. Please review your API call and try again."}), 500

    job_id = str(uuid.uuid4())
    logger.info(f"Generated job_id: {job_id}")

    # If webhook_url and id are provided, add the job to the queue
    if webhook_url and id:
        transcription_queue.put({
            'media_url': media_url,
            'output': output,
            'webhook_url': webhook_url,
            'id': id,
            'job_id': job_id
        })
        logger.info(f"Job {job_id}: Added to queue for background processing")
        return jsonify({"message": "processing"}), 202
    else:
        try:
            logger.info(f"Job {job_id}: No webhook provided, processing synchronously")
            result = process_transcription(media_url, output)
            logger.info(f"Job {job_id}: Returning transcription result")
            return jsonify({"response": result, "message": "success"}), 200
        except Exception as e:
            logger.error(f"Job {job_id}: Error during synchronous transcription - {e}")
            return jsonify({"message": str(e)}), 500
