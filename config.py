import os

API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set")

GCP_SA_CREDENTIALS = os.environ.get('GCP_SA_CREDENTIALS', '')
GDRIVE_USER = os.environ.get('GDRIVE_USER', '')
GCP_BUCKET_NAME = os.environ.get('GCP_BUCKET_NAME', '')
