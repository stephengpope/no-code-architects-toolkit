import os
import logging
from abc import ABC, abstractmethod
from services.gcp_toolkit import upload_to_gcs
from services.s3_toolkit import upload_to_s3
from config import validate_env_vars

logger = logging.getLogger(__name__)

class CloudStorageProvider(ABC):
    @abstractmethod
    def upload_file(self, file_path: str) -> str:
        pass

class GCPStorageProvider(CloudStorageProvider):
    def __init__(self):
        self.bucket_name = os.getenv('GCP_BUCKET_NAME')

    def upload_file(self, file_path: str) -> str:
        return upload_to_gcs(file_path, self.bucket_name)

class S3CompatibleProvider(CloudStorageProvider):
    def __init__(self):
        self.endpoint_url = os.getenv('S3_ENDPOINT_URL')
        self.access_key = os.getenv('S3_ACCESS_KEY')
        self.secret_key = os.getenv('S3_SECRET_KEY')

    def upload_file(self, file_path: str) -> str:
        return upload_to_s3(file_path, self.endpoint_url, self.access_key, self.secret_key)

def get_storage_provider() -> CloudStorageProvider:
    try:
        validate_env_vars('GCP')
        return GCPStorageProvider()
    except ValueError:
        validate_env_vars('S3')
        return S3CompatibleProvider()

def upload_file(file_path: str) -> str:
    provider = get_storage_provider()
    try:
        logger.info(f"Uploading file to cloud storage: {file_path}")
        url = provider.upload_file(file_path)
        logger.info(f"File uploaded successfully: {url}")
        return url
    except Exception as e:
        logger.error(f"Error uploading file to cloud storage: {e}")
        raise
    