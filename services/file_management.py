import os
import time
import requests
from config import STORAGE_PATH

def download_file(url, storage_path):
    local_filename = os.path.join(storage_path, url.split('/')[-1])
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return local_filename

def delete_old_files():
    while True:
        now = time.time()
        for filename in os.listdir(STORAGE_PATH):
            file_path = os.path.join(STORAGE_PATH, filename)
            if os.path.isfile(file_path) and os.stat(file_path).st_mtime < now - 3600:
                os.remove(file_path)
        time.sleep(3600)
