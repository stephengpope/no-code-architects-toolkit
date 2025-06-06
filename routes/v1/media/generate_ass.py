from flask import Blueprint, jsonify, request
from app_utils import validate_payload, queue_task_wrapper
import logging
from services.ass_toolkit import generate_ass_captions_v1
from services.authentication import authenticate
from services.cloud_storage import upload_file
import os
import requests

v1_media_generate_ass_bp = Blueprint('v1_media_generate_ass', __name__)
logger = logging.getLogger(__name__)

@v1_media_generate_ass_bp.route('/v1/media/generate/ass', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "media_url": {"type": "string", "format": "uri"},
        "canvas_width": {"type": "integer", "minimum": 1},
        "canvas_height": {"type": "integer", "minimum": 1},
        "settings": {
            "type": "object",
            "properties": {
                "line_color": {"type": "string"},
                "word_color": {"type": "string"},
                "outline_color": {"type": "string"},
                "all_caps": {"type": "boolean"},
                "max_words_per_line": {"type": "integer"},
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "position": {
                    "type": "string",
                    "enum": [
                        "bottom_left", "bottom_center", "bottom_right",
                        "middle_left", "middle_center", "middle_right",
                        "top_left", "top_center", "top_right"
                    ]
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
                    "enum": ["classic", "karaoke", "highlight", "underline", "word_by_word"]
                },
                "outline_width": {"type": "integer"},
                "spacing": {"type": "integer"},
                "angle": {"type": "integer"},
                "shadow_offset": {"type": "integer"}
            },
            "additionalProperties": False
        },
        "replace": {
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
        "exclude_time_ranges": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start": { "type": "string" },
                    "end": { "type": "string" }
                },
                "required": ["start", "end"],
                "additionalProperties": False
            }
        },
        "language": {"type": "string"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "additionalProperties": False,
    "required": ["media_url"],
    "oneOf": [
        { "required": ["canvas_width", "canvas_height"] },
        { "not": { "anyOf": [ { "required": ["canvas_width"] }, { "required": ["canvas_height"] } ] } }
    ]

})

@queue_task_wrapper(bypass_queue=False)
def generate_ass_v1(job_id, data):
    media_url = data['media_url']
    settings = data.get('settings', {})
    replace = data.get('replace', [])
    exclude_time_ranges = data.get('exclude_time_ranges', [])
    webhook_url = data.get('webhook_url')
    id = data.get('id')
    language = data.get('language', 'auto')
    canvas_width = data.get('canvas_width')
    canvas_height = data.get('canvas_height')

    logger.info(f"Job {job_id}: Received ASS generation request for {media_url}")
    logger.info(f"Job {job_id}: Settings received: {settings}")
    logger.info(f"Job {job_id}: Replace rules received: {replace}")
    logger.info(f"Job {job_id}: Exclude time ranges received: {exclude_time_ranges}")

    try:
        output = generate_ass_captions_v1(
            media_url,
            captions=None,
            settings=settings,
            replace=replace,
            exclude_time_ranges=exclude_time_ranges,
            job_id=job_id,
            language=language,
            PlayResX=canvas_width,
            PlayResY=canvas_height
        )
        if isinstance(output, dict) and 'error' in output:
            if 'available_fonts' in output:
                return {"error": output['error'], "available_fonts": output['available_fonts']}, "/v1/media/generate/ass", 400
            else:
                return {"error": output['error']}, "/v1/media/generate/ass", 400

        ass_path = output
        logger.info(f"Job {job_id}: ASS file generated at {ass_path}")

        cloud_url = upload_file(ass_path)
        logger.info(f"Job {job_id}: ASS file uploaded to cloud storage: {cloud_url}")

        os.remove(ass_path)
        logger.info(f"Job {job_id}: Cleaned up local ASS file")

        return cloud_url, "/v1/media/generate/ass", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during ASS generation process - {str(e)}", exc_info=True)
        return {"error": str(e)}, "/v1/media/generate/ass", 500
