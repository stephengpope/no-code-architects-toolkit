from flask import Blueprint
from app_utils import *
import logging
from services.v1.video.cut import process_video_cut
from services.authentication import authenticate
from services.cloud_storage import upload_file
import os

v1_video_cut_bp = Blueprint('v1_video_cut', __name__)
logger = logging.getLogger(__name__)

@v1_video_cut_bp.route('/v1/video/cut', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "video_url": {"type": "string", "format": "uri"},
        "cuts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start": {"type": "string", "pattern": "^([0-9]{2}):([0-9]{2}):([0-9]{2})$"},
                    "end": {"type": "string", "pattern": "^([0-9]{2}):([0-9]{2}):([0-9]{2})$"}
                },
                "required": ["start", "end"]
            },
            "minItems": 1
        },
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["video_url", "cuts"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def cut_video(job_id, data):
    video_url = data['video_url']
    cuts = data['cuts']
    webhook_url = data.get('webhook_url')
    id = data.get('id')

    logger.info(f"Job {job_id}: Received video cutting request for {video_url}")

    try:
        # Process video cutting
        output_files = process_video_cut(video_url, cuts, job_id)
        
        # Upload each cut segment to cloud storage
        file_urls = []
        for output_file in output_files:
            cloud_url = upload_file(output_file)
            file_urls.append({"file_url": cloud_url})
            os.remove(output_file)  # Clean up local file after upload
            
        logger.info(f"Job {job_id}: Video segments uploaded to cloud storage")

        return {"file_urls": file_urls}, "/v1/video/cut", 200
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error during video cutting process - {str(e)}")
        return str(e), "/v1/video/cut", 500 