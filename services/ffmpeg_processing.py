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

        # Reprocess input files to ensure they are all in the same format
        reprocessed_files = reprocess_input_files(input_files)

        # Generate an absolute path concat list file for FFmpeg
        concat_file_path = os.path.join(STORAGE_PATH, f"{job_id}_concat_list.txt")
        with open(concat_file_path, 'w') as concat_file:
            for reprocessed_file in reprocessed_files:
                # Write absolute paths to the concat list
                concat_file.write(f"file '{os.path.abspath(reprocessed_file)}'\n")

        # Use the concat demuxer to concatenate the videos
        (
            ffmpeg
            .input(concat_file_path, format='concat', safe=0)
            .output(output_path, vcodec='libx264', acodec='aac', video_bitrate='3000k', audio_bitrate='192k')
            .run(overwrite_output=True)
        )

        # Clean up reprocessed files and input files
        for f in input_files:
            os.remove(f)
        for f in reprocessed_files:
            os.remove(f)
        os.remove(concat_file_path)  # Remove the concat list file after the operation

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

def reprocess_input_files(input_files):
    reprocessed_files = []
    for i, input_file in enumerate(input_files):
        reprocessed_file = os.path.join(STORAGE_PATH, f"reprocessed_{i}.mp4")
        ffmpeg.input(input_file).output(reprocessed_file, vcodec='libx264', acodec='aac').run(overwrite_output=True)
        reprocessed_files.append(reprocessed_file)
    return reprocessed_files