# config.py
import os
import json
from google.cloud import storage
import tempfile

# Retrieve the API key from environment variables
API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set")

# GCP environment variables
GCP_SA_CREDENTIALS = os.environ.get('GCP_SA_CREDENTIALS', '')
GCP_BUCKET_NAME = os.environ.get('GCP_BUCKET_NAME', '')

# S3 (DigitalOcean Spaces) environment variables
S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL', '')
S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY', '')
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY', '')


def validate_env_vars(provider):
    """ Validate the necessary environment variables for the selected storage provider """
    required_vars = {
        'GCP': ['GCP_BUCKET_NAME', 'GCP_SA_CREDENTIALS'],
        'S3': ['S3_ENDPOINT_URL', 'S3_ACCESS_KEY', 'S3_SECRET_KEY']
    }
    missing_vars = [var for var in required_vars[provider] if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing environment variables for {provider} storage: {', '.join(missing_vars)}")


class CloudStorageProvider:
    """ Abstract CloudStorageProvider class to define the upload_file method """
    def upload_file(self, file_path: str, file_name: str, bucket_name: str = None, content_type: str = None) -> str:
        raise NotImplementedError("upload_file must be implemented by subclasses")


class GCPStorageProvider(CloudStorageProvider):
    """ GCP-specific cloud storage provider """
    def __init__(self):
        self.default_bucket_name = os.getenv('GCP_BUCKET_NAME')
        self.storage_client = self._initialize_storage_client()

    def _initialize_storage_client(self):
        gcp_sa_credentials = os.getenv('GCP_SA_CREDENTIALS')
        if not gcp_sa_credentials:
            raise ValueError("GCP_SA_CREDENTIALS environment variable is not set")

        try:
            # Create a temporary JSON file from the GCP_SA_CREDENTIALS environment variable
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as temp_file:
                json.dump(json.loads(gcp_sa_credentials), temp_file)
                temp_file_path = temp_file.name

            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_file_path

            # Initialize the storage client
            return storage.Client()

        except Exception as e:
            import traceback
            print(f"Failed to initialize GCS client: {str(e)}")
            print(traceback.format_exc())
            raise

    def upload_file(self, file_path: str, file_name: str, bucket_name: str = None, content_type: str = None) -> str:
        if not bucket_name:
            bucket_name = self.default_bucket_name
        if not bucket_name:
            raise ValueError("Bucket name must be provided or set in environment variables")

        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        # Upload the file
        blob.upload_from_filename(file_path, content_type=content_type)

        # Return the public URL of the uploaded file
        return f"https://storage.googleapis.com/{bucket_name}/{file_name}"

class S3CompatibleProvider(CloudStorageProvider):
    """ S3-compatible storage provider """
    def __init__(self):
        self.default_bucket_name = os.getenv('S3_BUCKET_NAME')
        self.region = os.getenv('S3_REGION')
        self.endpoint_url = os.getenv('S3_ENDPOINT_URL')
        self.access_key = os.getenv('S3_ACCESS_KEY')
        self.secret_key = os.getenv('S3_SECRET_KEY')

    def upload_file(self, file_path: str, file_name: str, bucket_name: str = None, content_type: str = None) -> str:
        if not bucket_name:
            bucket_name = self.default_bucket_name
        if not bucket_name:
            raise ValueError("Bucket name must be provided or set in environment variables")

        from services.s3_toolkit import upload_to_s3

        # Upload the file using your S3 upload function
        return upload_to_s3(
            file_path=file_path,
            bucket_name=bucket_name,
            file_name=file_name,
            region=self.region,
            endpoint_url=self.endpoint_url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            content_type=content_type
        )


def get_storage_provider() -> CloudStorageProvider:
    """ Get the appropriate storage provider based on the available environment variables """
    if os.getenv('S3_BUCKET_NAME'):
        validate_env_vars('S3')
        return S3CompatibleProvider()
    else:
        validate_env_vars('GCP')
        return GCPStorageProvider()