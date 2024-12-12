from flask import Blueprint, jsonify
from app_utils import validate_payload, queue_task_wrapper
import logging
from services.v1.caption_video import process_captioning_v1
from services.authentication import authenticate
from services.cloud_storage import upload_file
import os
import requests  # Ensure requests is imported for webhook handling

v1_caption_bp = Blueprint('v1_caption', __name__)
logger = logging.getLogger(__name__)

@v1_caption_bp.route('/v1/caption-video', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "video_url": {"type": "string", "format": "uri"},
        "captions": {"type": "string"},  # Renamed from "caption"
        "settings": {
            "type": "object",
            "properties": {
                "line_color": {"type": "string"},
                "word_color": {"type": "string"},
                "outline_color": {"type": "string"},
                "box_color": {"type": "string"},
                "all_caps": {"type": "boolean"},
                "max_words_per_line": {"type": "integer"},
                "x": {"type": "integer"},            # Added
                "y": {"type": "integer"},            # Added
                "position": {
                    "type": "string",
                    "enum": ["bottom_left", "bottom_center", "bottom_right","middle_left", "middle_center", "middle_right","top_left", "top_center", "top_right"]
                },
                "alignment": {
                    "type": "string",
                    "enum": ["left", "center", "right"]
                },
                "font_family": {"type": "string"},
                "font_size": {"type": "integer"},
                "bold": {"type": "boolean"},
                "italic": {"type": "boolean"},
                "underline": {"type": "boolean"},
                "strikeout": {"type": "boolean"},
                "style": {
                    "type": "string",
                    "enum": ["classic", "karaoke", "highlight","underline", "word_by_word"]
                    },
                "border_style": {"type": "string"},
                "outline_width": {"type": "integer"},
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "spacing": {"type": "integer"},
                "angle": {"type": "integer"},
                "shadow_offset": {"type": "integer"}
            },
            "additionalProperties": False
        },
        "replace": {  # Moved to main payload
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "find": {"type": "string"},
                    "replace": {"type": "string"}
                },
                "required": ["find", "replace"]
            }
        },
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"},
        "language": {"type": "string"}  # Optional: Specify language if needed
    },
    "required": ["video_url"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def caption_video_v1(job_id, data):
    video_url = data['video_url']
    captions = data.get('captions')  # Renamed from "caption"
    settings = data.get('settings', {})  # Renamed from "options" and default to dict
    replace = data.get('replace', [])  # Moved to main payload
    webhook_url = data.get('webhook_url')
    id = data.get('id')
    language = data.get('language', 'auto')  # Default to 'auto' if not provided

    logger.info(f"Job {job_id}: Received v1 captioning request for {video_url}")
    logger.info(f"Job {job_id}: Settings received: {settings}")
    logger.info(f"Job {job_id}: Replace rules received: {replace}")

    try:
        # Combine 'position' and 'alignment' into a single 'position' string
        vertical_position = settings.get('position', 'middle')
        horizontal_alignment = settings.get('alignment', 'center')
        combined_position = f"{vertical_position}_{horizontal_alignment}"

        # Update settings with the combined position
        settings['position'] = combined_position

        # Remove the separate 'alignment' key to prevent confusion
        if 'alignment' in settings:
            del settings['alignment']

        logger.info(f"Job {job_id}: Combined position set to '{combined_position}'")

        # Process video with the enhanced v1 service
        output = process_captioning_v1(video_url, captions, settings, replace, job_id, language)
        
        if isinstance(output, dict) and 'error' in output:
            # Processing error occurred (e.g., unavailable font)
            return {"error": output['error'], "available_fonts": output.get('available_fonts', [])}, "/v1/caption-video", 400  # Return error response with HTTP 400

        # If processing was successful, output is the file path
        output_path = output
        logger.info(f"Job {job_id}: Captioning process completed successfully")

        # Upload the captioned video
        cloud_url = upload_file(output_path)
        logger.info(f"Job {job_id}: Captioned video uploaded to cloud storage: {cloud_url}")

        # Clean up the output file after upload
        os.remove(output_path)
        logger.info(f"Job {job_id}: Cleaned up local output file")

        # Optionally, send a webhook notification
        if webhook_url:
            payload = {
                "job_id": job_id,
                "status": "completed",
                "output_url": cloud_url
            }
            try:
                response = requests.post(webhook_url, json=payload)
                if response.status_code == 200:
                    logger.info(f"Job {job_id}: Webhook notification sent successfully")
                else:
                    logger.warning(f"Job {job_id}: Webhook notification failed with status code {response.status_code}")
            except Exception as e:
                logger.error(f"Job {job_id}: Failed to send webhook notification - {str(e)}")

        # Return a tuple with content, endpoint, and status code
        return {"output_url": cloud_url}, "/v1/caption-video", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during captioning process - {str(e)}", exc_info=True)
        return {"error": str(e)}, "/v1/caption-video", 500
