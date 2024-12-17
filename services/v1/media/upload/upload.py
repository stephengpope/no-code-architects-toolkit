# services/v1/media/upload/upload.py
import os
from google.cloud import storage
import requests

class GCPStorageProvider:
    """Google Cloud Storage-specific storage provider"""

    def __init__(self):
        self.bucket_name = os.getenv('GCP_BUCKET_NAME', 'default-bucket-name')
        self.storage_client = storage.Client()

    def upload_file(self, file_data: bytes, filename: str) -> str:
        bucket = self.storage_client.get_bucket(self.bucket_name)
        blob = bucket.blob(filename)

        # Upload the file data
        blob.upload_from_string(file_data)

        return blob.name

def download_file_from_url(url: str) -> bytes:
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    return response.content