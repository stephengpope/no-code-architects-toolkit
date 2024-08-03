import os
import uuid
import threading
import time
from flask import Flask, request, jsonify, send_file
from werkzeug.exceptions import BadRequest
from functools import wraps
import ffmpeg

import whisper
import srt
from datetime import datetime, timedelta

app = Flask(__name__)

API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set")

STORAGE_PATH = os.environ.get('STORAGE_PATH', '/tmp/')

os.makedirs(STORAGE_PATH, exist_ok=True)

def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper

def delete_old_files():
    while True:
        now = time.time()
        for filename in os.listdir(STORAGE_PATH):
            file_path = os.path.join(STORAGE_PATH, filename)
            if os.path.isfile(file_path):
                if os.stat(file_path).st_mtime < now - 3600:
                    os.remove(file_path)
        time.sleep(3600)  # Run every hour

threading.Thread(target=delete_old_files, daemon=True).start()

def download_file(url, local_filename):
    import requests
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def send_webhook(webhook_url, data):
    import requests
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Webhook failed: {e}")

@app.route('/authenticate', methods=['POST'])
def authenticate_endpoint():
    api_key = request.headers.get('X-API-Key')
    if api_key == API_KEY:
        return jsonify([{"message": "Authorized"}]), 200
    else:
        return jsonify([{"message": "Unauthorized"}]), 401

@app.route('/convert-media-to-mp3', methods=['POST'])
@authenticate
def convert_media_to_mp3():
    data = request.json
    media_url = data.get('media_url')
    webhook_url = data.get('webhook_url')

    if not media_url:
        raise BadRequest("Missing media_url parameter")

    job_id = str(uuid.uuid4())
    output_filename = f"{job_id}.mp3"

    if webhook_url:
        threading.Thread(target=process_conversion, args=(media_url, output_filename, webhook_url, job_id)).start()
        return jsonify({"job_id": job_id, "filename": output_filename}), 202
    else:
        try:
            process_conversion(media_url, output_filename, webhook_url, job_id)
            return jsonify({"job_id": job_id, "filename": output_filename}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

def process_conversion(media_url, output_filename, webhook_url, job_id):
    try:
        input_filename = download_file(media_url, os.path.join(STORAGE_PATH, f"{job_id}_input"))
        
        (
            ffmpeg
            .input(input_filename)
            .output(os.path.join(STORAGE_PATH, output_filename), acodec='libmp3lame', audio_bitrate='64k')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )

        os.remove(input_filename)

        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/convert-media-to-mp3",
                "job_id": job_id,
                "response": output_filename,
                "code": 200,
                "message": "success"
            })
        
        return output_filename
    except Exception as e:
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/convert-media-to-mp3",
                "job_id": job_id,
                "response": None,
                "code": 500,
                "message": str(e)
            })
        raise

@app.route('/transcribe-media', methods=['POST'])
@authenticate
def transcribe_media():
    data = request.json
    media_url = data.get('media_url')
    output_type = data.get('output')
    webhook_url = data.get('webhook_url')

    if not media_url:
        raise BadRequest("Missing media_url parameter")
    if not output_type:
        raise BadRequest("Missing output parameter")
    if output_type not in ['transcript', 'srt']:
        raise BadRequest("Invalid output type. Must be 'transcript' or 'srt'")

    job_id = str(uuid.uuid4())

    if webhook_url:
        threading.Thread(target=process_transcription, args=(media_url, output_type, webhook_url, job_id)).start()
        return jsonify({"job_id": job_id}), 200
    
    try:
        result = process_transcription(media_url, output_type, webhook_url, job_id)
        return jsonify({"response": result}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

def process_transcription(media_url, output_type, webhook_url, job_id):
    try:
        input_filename = download_file(media_url, os.path.join(STORAGE_PATH, f"{job_id}_input"))
        
        model = whisper.load_model("base")
        result = model.transcribe(input_filename)

        os.remove(input_filename)

        if output_type == 'transcript':
            output = result['text']
        else:  # srt
            srt_subtitles = []
            for i, segment in enumerate(result['segments'], start=1):
                start = timedelta(seconds=segment['start'])
                end = timedelta(seconds=segment['end'])
                text = segment['text'].strip()
                srt_subtitles.append(srt.Subtitle(i, start, end, text))
            output = srt.compose(srt_subtitles)

        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/transcribe-media",
                "job_id": job_id,
                "response": output,
                "code": 200,
                "message": "success"
            })
        
        return output
    except Exception as e:
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/transcribe-media",
                "job_id": job_id,
                "code": 500,
                "message": str(e)
            })
        raise

@app.route('/get-file', methods=['POST'])
@authenticate
def get_file():
    data = request.json
    filename = data.get('filename')

    if not filename:
        raise BadRequest("Missing filename parameter")

    file_path = os.path.join(STORAGE_PATH, filename)
    if not os.path.exists(file_path):
        return jsonify({"message": "File not found"}), 404

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)