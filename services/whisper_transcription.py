import os
import uuid
import whisper
import srt
from datetime import timedelta
from services.webhook import send_webhook
from services.file_management import download_file, STORAGE_PATH

def process_transcription(media_url, output_type, webhook_url):
    try:
        # Generate a unique job ID using UUID
        job_id = str(uuid.uuid4())
        input_filename = download_file(media_url, os.path.join(STORAGE_PATH, f"{job_id}_input"))
        
        model = whisper.load_model("base")
        result = model.transcribe(input_filename)

        os.remove(input_filename)  # Clean up the input file after transcription

        if output_type == 'transcript':
            output = result['text']
        else:  # SRT format
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

        return job_id  # Return the generated job ID
    except Exception as e:
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/transcribe-media",
                "job_id": None,
                "response": None,
                "code": 500,
                "message": str(e)
            })
        raise
