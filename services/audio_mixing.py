import os
import ffmpeg
from services.file_management import download_file, STORAGE_PATH
from services.gdrive_service import upload_to_gdrive, upload_to_gcs, GCP_BUCKET_NAME

def process_audio_mixing(video_url, audio_url, video_vol, audio_vol, output_length, job_id, webhook_url=None):
    """Mix audio with video."""
    video_input = os.path.join(STORAGE_PATH, f"{job_id}_video_input")
    audio_input = os.path.join(STORAGE_PATH, f"{job_id}_audio_input")
    output_filename = f"{job_id}_mixed.mp4"
    output_path = os.path.join(STORAGE_PATH, output_filename)

    try:
        download_file(video_url, video_input)
        download_file(audio_url, audio_input)

        video = ffmpeg.input(video_input)
        audio = ffmpeg.input(audio_input)

        video_audio = video.audio.filter('volume', volume=f"{video_vol/100}")
        input_audio = audio.filter('volume', volume=f"{audio_vol/100}")

        video_info = ffmpeg.probe(video_input)
        audio_info = ffmpeg.probe(audio_input)
        video_duration = float(video_info['streams'][0]['duration'])
        audio_duration = float(audio_info['streams'][0]['duration'])

        if output_length == 'video':
            output_duration = video_duration
        else:
            output_duration = audio_duration

        if output_duration > audio_duration:
            input_audio = ffmpeg.filter([input_audio], 'apad', pad_dur=output_duration-audio_duration)
        else:
            input_audio = input_audio.filter('atrim', duration=output_duration)

        mixed_audio = ffmpeg.filter([video_audio, input_audio], 'amix', inputs=2)

        if output_duration > video_duration:
            video = ffmpeg.filter([video], 'tpad', stop_duration=output_duration-video_duration)
        else:
            video = video.trim(duration=output_duration)

        output = ffmpeg.output(video, mixed_audio, output_path,
            vcodec='libx264', acodec='aac', strict='experimental')

        ffmpeg.run(output, overwrite_output=True)

        # Remove the input files
        os.remove(video_input)
        os.remove(audio_input)
        print(f"Audio mixing successful: {output_path}")

        # Check if the output file exists locally before upload
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file {output_path} does not exist after mixing.")

        # Upload to Google Drive or GCP Storage
        if GCP_BUCKET_NAME:
            uploaded_file_url = upload_to_gcs(output_path, GCP_BUCKET_NAME, output_filename)
        else:
            uploaded_file_url = upload_to_gdrive(output_path, output_filename)

        # If upload fails, log the failure
        if not uploaded_file_url:
            raise FileNotFoundError(f"Failed to upload the output file {output_path}")

        # Trigger webhook if provided
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/audio-mixing",
                "job_id": job_id,
                "response": uploaded_file_url or output_path,
                "code": 200,
                "message": "success"
            })
        
        return uploaded_file_url or output_path
    except Exception as e:
        print(f"Audio mixing failed: {str(e)}")
        # Trigger failure webhook if provided
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/audio-mixing",
                "job_id": job_id,
                "response": None,
                "code": 500,
                "message": str(e)
            })
        raise