import os

API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set")

STORAGE_PATH = os.environ.get('STORAGE_PATH', '/tmp/')
os.makedirs(STORAGE_PATH, exist_ok=True)

GCP_SA_CREDENTIALS = os.environ.get('GCP_SA_CREDENTIALS', '')
GDRIVE_USER = os.environ.get('GDRIVE_USER', '')
GCP_BUCKET_NAME = os.environ.get('GCP_BUCKET_NAME', '')

# Add GPU acceleration flag
GPU_ENABLED = os.environ.get('GPU_ENABLED', 'false').lower() == 'true'
