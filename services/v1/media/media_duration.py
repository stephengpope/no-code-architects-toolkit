import subprocess
from services.file_management import download_file
import os

def get_media_duration_from_url(media_url):
    local_file = download_file(media_url)
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            local_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(result.stderr.strip())
        duration = float(result.stdout.strip())
        return round(duration, 2)
    finally:
        if os.path.exists(local_file):
            os.remove(local_file)
