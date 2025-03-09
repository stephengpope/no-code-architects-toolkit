import os
import ffmpeg
import requests
from services.file_management import download_file

# Set the default local storage directory
STORAGE_PATH = "/tmp/"

def process_audio_concatenate(media_urls, job_id, webhook_url=None):
    """Combine multiple audio files into one."""
    input_streams = []
    input_files = []
    output_filename = f"{job_id}.mp3"
    output_path = os.path.join(STORAGE_PATH, output_filename)

    try:
        # Download all media files
        for i, media_item in enumerate(media_urls):
            url = media_item['audio_url']
            input_filename = download_file(url, os.path.join(STORAGE_PATH, f"{job_id}_input_{i}"))
            input_streams.append(ffmpeg.input(input_filename))
            input_files.append(input_filename)

        # Use the concat filter with re-encoding
        (
            ffmpeg
            .concat(*input_streams, v=0, a=1)
            .output(output_path, acodec='libmp3lame', ar='44100')
            .run(overwrite_output=True)
        )

        # Clean up input files
        for f in input_files:
            os.remove(f)

        print(f"Audio combination successful: {output_path}")

        # Check if the output file exists locally before upload
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file {output_path} does not exist after combination.")

        return output_path
    except Exception as e:
        print(f"Audio combination failed: {str(e)}")
        raise

