import os
import subprocess
import json
from services.file_management import download_file
from services.gcp_toolkit import upload_to_gcs

STORAGE_PATH = "/tmp/"

def process_keyframe_extraction(video_url, job_id):
    video_path = download_file(video_url, STORAGE_PATH)

    # Extract keyframes
    output_pattern = os.path.join(STORAGE_PATH, f"{job_id}_%03d.jpg")
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f"select='eq(pict_type,I)',scale=iw*sar:ih,setsar=1",
        '-vsync', 'vfr',
        output_pattern
    ]

    print(f"Images: {cmd}")

    subprocess.run(cmd, check=True)

    # Upload keyframes to GCS and get URLs
    image_urls = []
    for filename in sorted(os.listdir(STORAGE_PATH)):
        if filename.startswith(f"{job_id}_") and filename.endswith(".jpg"):
            file_path = os.path.join(STORAGE_PATH, filename)
            gcs_url = upload_to_gcs(file_path)
            image_urls.append(gcs_url)
            os.remove(file_path)  # Clean up the local file

    # Clean up input file
    os.remove(video_path)

    return image_urls