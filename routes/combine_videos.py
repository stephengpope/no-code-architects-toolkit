from flask import Blueprint, request, jsonify
import uuid
import threading
import logging
import queue
from services.ffmpeg_toolkit import process_video_combination
from services.authentication import authenticate
from services.webhook import send_webhook

combine_bp = Blueprint('combine', __name__)
logger = logging.getLogger(__name__)

# Create a queue for combine jobs
combine_queue = queue.Queue()

def combine_worker():
    while True:
        job = combine_queue.get()
        try:
            process_job(**job)
        except Exception as e:
            logger.error(f"Error processing job: {e}")
        finally:
            combine_queue.task_done()

# Start the worker thread
worker_thread = threading.Thread(target=combine_worker, daemon=True)
worker_thread.start()

def process_job(media_urls, webhook_url, id, job_id):
    try:
        output_filename = process_video_combination(media_urls, job_id)
        
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/combine-videos",
                "code": 200,
                "id": id,
                "job_id": job_id,
                "response": output_filename,
                "message": "success"
            })

        return output_filename;

    except Exception as e:
        logger.error(f"Job {job_id}: Error during processing - {e}")
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/combine-videos",
                "code": 500,
                "id": id,
                "job_id": job_id,
                "response": None,
                "message": str(e),         
            })
        else:
            raise

@combine_bp.route('/combine-videos', methods=['POST'])
@authenticate
def combine_videos():
    data = request.json
    media_urls = data.get('media_urls')
    webhook_url = data.get('webhook_url')
    id = data.get('id')
    job_id = str(uuid.uuid4())

    logger.info(f"Received combine-videos request: media_urls={media_urls}, webhook_url={webhook_url}, id={id}")

    if not (isinstance(media_urls, list) and 
            all(isinstance(item, dict) and 
                isinstance(item.get('media_url'), str) 
                for item in media_urls)):
        logger.error("Invalid or missing media_urls parameter in request")
        return jsonify({"message": "Invalid or missing media_urls parameter"}), 400

    #if webhook_url and not id:
    #    logger.warning("id is missing when webhook_url is provided")
    #    return jsonify({"message": "It appears that the id is missing. Please review your API call and try again."}), 400
    if webhook_url:
        # Add the job to the queue for background processing
        combine_queue.put({
            'media_urls': media_urls,
            'webhook_url': webhook_url,
            'id': id,
            'job_id': job_id
        })
        logger.info(f"Job {job_id}: Added to queue for asynchronous processing")
        return jsonify(
            {
                "code": 202,
                "id": id,
                "job_id": job_id,
                "message": "processing"
            }
        ), 202
    else:
        try:
            # Process the conversion synchronously and return the URL
            uploaded_file_url = process_job(media_urls=media_urls, job_id=job_id, id=id, webhook_url=None)
            
            return jsonify({
                    "code": 200,
                    "response": uploaded_file_url,
                    "message": "success"
            }), 200

        except Exception as e:
            logger.error(f"Job {job_id}: Error during synchronous processing - {e}")
            return jsonify({
                "code": 500,
                "message": str(e)
            }), 500
