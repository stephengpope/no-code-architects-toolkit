import preload

from flask import Blueprint, request, jsonify
from flask import current_app
from app_utils import *
import uuid
import logging
from services.authentication import authenticate
from services.gcp_toolkit import upload_to_gcs
from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio
from scipy.io import wavfile
import torch
import os

tts_bp = Blueprint('text_to_speech', __name__)
logger = logging.getLogger(__name__)

# Initialize Tortoise TTS model
tts = TextToSpeech()

@tts_bp.route('/text-to-speech', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "preset": {"type": "string"},
        "voice": {"type": "string"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["text", "preset", "voice"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def text_to_speech(job_id, data):
    text = data.get('text')
    preset = data.get('preset')
    voice = data.get('voice')
    
    logger.info(f"Job {job_id}: Received text-to-speech request for voice: {voice}")

    try:
        # Generate speech
        gen_audio = tts.tts_with_preset(text, voice, preset=preset)
        
        # Save the audio file
        output_filename = f"/tmp/{job_id}.wav"
        wavfile.write(output_filename, 24000, (gen_audio.cpu().numpy() * 32767).astype('int16'))
        
        # Upload to GCS
        gcs_url = upload_to_gcs(output_filename)
        
        # Clean up the temporary file
        os.remove(output_filename)

        return gcs_url, "/text-to-speech", 200
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error in text-to-speech - {str(e)}")
        return str(e), "/text-to-speech", 500