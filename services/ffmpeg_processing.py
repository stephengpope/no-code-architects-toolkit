import os
import ffmpeg
import requests
from services.file_management import download_file, STORAGE_PATH
from services.gdrive_service import upload_to_gdrive, upload_to_gcs, GCP_BUCKET_NAME, gcs_client  # Import gcs_client

def process_conversion(media_url, job_id, webhook_url=None):
    """Convert media to MP3 format."""
    input_filename = download_file(media_url, os.path.join(STORAGE_PATH, f"{job_id}_input"))
    output_filename = f"{job_id}.mp3"
    output_path = os.path.join(STORAGE_PATH, output_filename)

    try:
        # Convert media file to MP3
        (
            ffmpeg
            .input(input_filename)
            .output(output_path, acodec='libmp3lame', audio_bitrate='64k')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        os.remove(input_filename)
        print(f"Conversion successful: {output_path}")
        
        # Ensure the output file exists locally before attempting upload
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file {output_path} does not exist after conversion.")

        # Upload to the correct storage based on STORAGE_PATH
        uploaded_file_url = None
        if STORAGE_PATH.lower() == 'drive':
            uploaded_file_url = upload_to_gdrive(output_path, output_filename)
        elif STORAGE_PATH.lower() == 'gcp':
            uploaded_file_url = upload_to_gcs(output_path, GCP_BUCKET_NAME, output_filename)
        else:
            raise Exception(f"Invalid STORAGE_PATH: {STORAGE_PATH}")

        # If the upload was successful, delete the local file and return
        if uploaded_file_url:
            print(f"File successfully uploaded to {uploaded_file_url}")
            os.remove(output_path)  # Remove the local file after uploading
            
            # Trigger webhook if provided and exit the function
            if webhook_url:
                send_webhook(webhook_url, {
                    "endpoint": "/convert-media-to-mp3",
                    "job_id": job_id,
                    "response": uploaded_file_url,
                    "code": 200,
                    "message": "success"
                })
            return uploaded_file_url

    except Exception as e:
        print(f"Conversion failed: {str(e)}")
        # Trigger failure webhook if provided
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/convert-media-to-mp3",
                "job_id": job_id,
                "response": None,
                "code": 500,
                "message": str(e)
            })
        raise

    """Convert media to MP3 format."""
    input_filename = download_file(media_url, os.path.join(STORAGE_PATH, f"{job_id}_input"))
    output_filename = f"{job_id}.mp3"
    output_path = os.path.join(STORAGE_PATH, output_filename)

    try:
        # Convert media file to MP3
        (
            ffmpeg
            .input(input_filename)
            .output(output_path, acodec='libmp3lame', audio_bitrate='64k')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        os.remove(input_filename)
        print(f"Conversion successful: {output_path}")
        
        # Ensure the output file exists locally before attempting upload
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file {output_path} does not exist after conversion.")

        # Upload to the correct storage based on STORAGE_PATH
        uploaded_file_url = None
        if STORAGE_PATH.lower() == 'drive':
            uploaded_file_url = upload_to_gdrive(output_path, output_filename)
        elif STORAGE_PATH.lower() == 'gcp':
            uploaded_file_url = upload_to_gcs(output_path, GCP_BUCKET_NAME, output_filename)
        else:
            raise Exception(f"Invalid STORAGE_PATH: {STORAGE_PATH}")

        # If the upload was successful, delete the local file and return
        if uploaded_file_url:
            print(f"File successfully uploaded to {uploaded_file_url}")
            os.remove(output_path)  # Remove the local file after uploading
            
            # Trigger webhook if provided and exit the function
            if webhook_url:
                send_webhook(webhook_url, {
                    "endpoint": "/convert-media-to-mp3",
                    "job_id": job_id,
                    "response": uploaded_file_url,
                    "code": 200,
                    "message": "success"
                })
            return uploaded_file_url

    except Exception as e:
        print(f"Conversion failed: {str(e)}")
        # Trigger failure webhook if provided
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/convert-media-to-mp3",
                "job_id": job_id,
                "response": None,
                "code": 500,
                "message": str(e)
            })

def process_video_combination(media_urls, job_id, webhook_url=None):
    """Combine multiple videos into one."""
    input_files = []
    output_filename = f"{job_id}_combined.mp4"
    output_path = os.path.join(STORAGE_PATH, output_filename)

    try:
        # Download all media files
        for i, url in enumerate(media_urls):
            input_filename = download_file(url, os.path.join(STORAGE_PATH, f"{job_id}_input_{i}"))
            input_files.append(input_filename)

        # Combine the videos
        inputs = [ffmpeg.input(f) for f in input_files]
        concat = ffmpeg.concat(*inputs)
        output = ffmpeg.output(concat, output_path,
            vcodec='libx264', acodec='aac',
            video_bitrate='3000k', audio_bitrate='192k')

        ffmpeg.run(output, overwrite_output=True)
        
        # Remove input files after combination
        for f in input_files:
            os.remove(f)
        print(f"Video combination successful: {output_path}")
        
        # Check if the output file exists locally before upload
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file {output_path} does not exist after combination.")

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
                "endpoint": "/combine-videos",
                "job_id": job_id,
                "response": uploaded_file_url or output_path,
                "code": 200,
                "message": "success"
            })
        
        return uploaded_file_url or output_path
    except Exception as e:
        print(f"Video combination failed: {str(e)}")
        # Trigger failure webhook if provided
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/combine-videos",
                "job_id": job_id,
                "response": None,
                "code": 500,
                "message": str(e)
            })
        raise

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
