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

import base64
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

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

@app.route('/combine-videos', methods=['POST'])
@authenticate
def combine_videos():
    data = request.json
    media_urls = data.get('media_urls')
    webhook_url = data.get('webhook_url')

    if not media_urls or not isinstance(media_urls, list):
        raise BadRequest("Missing or invalid media_urls parameter")

    job_id = str(uuid.uuid4())
    output_filename = f"{job_id}_combined.mp4"

    if webhook_url:
        threading.Thread(target=process_video_combination, args=(media_urls, output_filename, webhook_url, job_id)).start()
        return jsonify({"job_id": job_id, "filename": output_filename}), 202
    else:
        try:
            process_video_combination(media_urls, output_filename, webhook_url, job_id)
            return jsonify({"job_id": job_id, "filename": output_filename}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

def process_video_combination(media_urls, output_filename, webhook_url, job_id):
    try:
        input_files = []
        for i, url in enumerate(media_urls):
            input_filename = download_file(url, os.path.join(STORAGE_PATH, f"{job_id}_input_{i}"))
            input_files.append(input_filename)

        # Create a list of input files for ffmpeg
        inputs = [ffmpeg.input(f) for f in input_files]

        # Concatenate the input videos
        concat = ffmpeg.concat(*inputs)

        # Output the result, re-encoding the video
        output = ffmpeg.output(concat, os.path.join(STORAGE_PATH, output_filename),
                               vcodec='libx264',  # Use H.264 codec
                               acodec='aac',      # Use AAC for audio
                               video_bitrate='3000k',  # Adjust as needed
                               audio_bitrate='192k')   # Adjust as needed

        # Run the ffmpeg command
        ffmpeg.run(output, overwrite_output=True)

        # Clean up input files
        for f in input_files:
            os.remove(f)

        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/combine-videos",
                "job_id": job_id,
                "response": output_filename,
                "code": 200,
                "message": "success"
            })
        
        return output_filename
    except Exception as e:
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/combine-videos",
                "job_id": job_id,
                "response": None,
                "code": 500,
                "message": str(e)
            })
        raise

@app.route('/audio-mixing', methods=['POST'])
@authenticate
def audio_mixing():
    data = request.json
    video_url = data.get('video_url')
    audio_url = data.get('audio_url')
    video_vol = data.get('video_vol', 100)
    audio_vol = data.get('audio_vol', 100)
    output_length = data.get('output_length', 'video')
    webhook_url = data.get('webhook_url')

    # Input validation
    if not video_url or not audio_url:
        raise BadRequest("Missing video_url or audio_url parameter")
    
    if not 0 <= video_vol <= 100 or not 0 <= audio_vol <= 100:
        raise BadRequest("video_vol and audio_vol must be between 0 and 100")
    
    if output_length not in ['video', 'audio']:
        raise BadRequest("output_length must be either 'video' or 'audio'")

    job_id = str(uuid.uuid4())
    output_filename = f"{job_id}_mixed.mp4"

    if webhook_url:
        threading.Thread(target=process_audio_mixing, args=(video_url, audio_url, video_vol, audio_vol, output_length, output_filename, webhook_url, job_id)).start()
        return jsonify({"job_id": job_id, "filename": output_filename}), 202
    else:
        try:
            process_audio_mixing(video_url, audio_url, video_vol, audio_vol, output_length, output_filename, webhook_url, job_id)
            return jsonify({"job_id": job_id, "filename": output_filename}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

def process_audio_mixing(video_url, audio_url, video_vol, audio_vol, output_length, output_filename, webhook_url, job_id):
    try:
        video_input = os.path.join(STORAGE_PATH, f"{job_id}_video_input")
        audio_input = os.path.join(STORAGE_PATH, f"{job_id}_audio_input")
        
        # Download files
        download_file(video_url, video_input)
        download_file(audio_url, audio_input)

        # Prepare FFmpeg inputs
        video = ffmpeg.input(video_input)
        audio = ffmpeg.input(audio_input)

        # Apply volume filters
        video_audio = video.audio.filter('volume', volume=f"{video_vol/100}")
        input_audio = audio.filter('volume', volume=f"{audio_vol/100}")

        # Get video and audio durations
        video_info = ffmpeg.probe(video_input)
        audio_info = ffmpeg.probe(audio_input)
        video_duration = float(video_info['streams'][0]['duration'])
        audio_duration = float(audio_info['streams'][0]['duration'])

        # Determine output duration
        if output_length == 'video':
            output_duration = video_duration
        else:
            output_duration = audio_duration

        # Trim or pad audio
        if output_duration > audio_duration:
            input_audio = ffmpeg.filter([input_audio], 'apad', pad_dur=output_duration-audio_duration)
        else:
            input_audio = input_audio.filter('atrim', duration=output_duration)

        # Mix audio
        mixed_audio = ffmpeg.filter([video_audio, input_audio], 'amix', inputs=2)

        # Trim or pad video
        if output_duration > video_duration:
            video = ffmpeg.filter([video], 'tpad', stop_duration=output_duration-video_duration)
        else:
            video = video.trim(duration=output_duration)

        # Combine video and mixed audio
        output = ffmpeg.output(video, mixed_audio, os.path.join(STORAGE_PATH, output_filename),
                               vcodec='libx264', acodec='aac', strict='experimental')

        # Run FFmpeg command
        ffmpeg.run(output, overwrite_output=True)

        # Clean up input files
        os.remove(video_input)
        os.remove(audio_input)

        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/audio-mixing",
                "job_id": job_id,
                "response": output_filename,
                "code": 200,
                "message": "success"
            })
        
        return output_filename
    except Exception as e:
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/audio-mixing",
                "job_id": job_id,
                "response": None,
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

# Add these to the existing imports at the top of the file

# Add these new environment variables
GCP_SA_CREDENTIALS = os.environ.get('GCP_SA_CREDENTIALS', '')
GDRIVE_USER = os.environ.get('GDRIVE_USER', '')

#if not GCP_SA_CREDENTIALS or not GDRIVE_USER:
#    raise ValueError("GCP_SA_CREDENTIALS and GDRIVE_USER environment variables must be set")

# Add this function to set up the Google Drive service
def get_gdrive_service():
    credentials_json = json.loads(base64.b64decode(GCP_SA_CREDENTIALS))
    credentials = service_account.Credentials.from_service_account_info(
        credentials_json,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    delegated_credentials = credentials.with_subject(GDRIVE_USER)
    return build('drive', 'v3', credentials=delegated_credentials)

# Add this new endpoint
@app.route('/gdrive-upload', methods=['POST'])
@authenticate
def gdrive_upload():
    data = request.json
    file_url = data.get('file_url')
    filename = data.get('filename')
    folder_id = data.get('folder_id')
    webhook_url = data.get('webhook_url')

    if not file_url or not filename or not folder_id:
        raise BadRequest("Missing file_url, filename, or folder_id parameter")

    job_id = str(uuid.uuid4())
    unique_filename = f"{job_id}_{filename}"

    if webhook_url:
        threading.Thread(target=process_gdrive_upload, args=(file_url, unique_filename, filename, folder_id, webhook_url, job_id)).start()
        return jsonify({"job_id": job_id, "filename": filename}), 202
    else:
        try:
            file_id = process_gdrive_upload(file_url, unique_filename, filename, folder_id, webhook_url, job_id)
            return jsonify({"job_id": job_id, "filename": unique_filename, "file_id": file_id}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

def process_gdrive_upload(file_url, unique_filename, filename, folder_id, webhook_url, job_id):
    try:
        local_file_path = download_file(file_url, os.path.join(STORAGE_PATH, unique_filename))
        
        drive_service = get_gdrive_service()
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        media = MediaFileUpload(local_file_path, resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')

        os.remove(local_file_path)

        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/gdrive-upload",
                "job_id": job_id,
                "response": file_id,
                "code": 200,
                "message": "success"
            })
        
        return file_id
    except Exception as e:
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/gdrive-upload",
                "job_id": job_id,
                "response": None,
                "code": 500,
                "message": str(e)
            })
        raise

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)