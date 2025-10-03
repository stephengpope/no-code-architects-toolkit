# Copyright (c) 2025 Stephen G. Pope
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.



import os
import json
import logging
from google.oauth2 import service_account
from google.cloud import storage
from google.cloud.run_v2 import JobsClient, RunJobRequest
from google.api_core.exceptions import GoogleAPIError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GCS environment variables
GCP_BUCKET_NAME = os.getenv('GCP_BUCKET_NAME')
STORAGE_PATH = "/tmp/"
gcs_client = None

def initialize_gcp_client():
    GCP_SA_CREDENTIALS = os.getenv('GCP_SA_CREDENTIALS')

    if not GCP_SA_CREDENTIALS:
        #logger.warning("GCP credentials not found. Skipping GCS client initialization.")
        return None  # Skip client initialization if credentials are missing

    # Define the required scopes for Google Cloud Storage
    GCS_SCOPES = ['https://www.googleapis.com/auth/devstorage.full_control']

    try:
        credentials_info = json.loads(GCP_SA_CREDENTIALS)
        gcs_credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=GCS_SCOPES
        )
        return storage.Client(credentials=gcs_credentials)
    except Exception as e:
        logger.error(f"Failed to initialize GCS client: {e}")
        return None

# Initialize the GCS client
gcs_client = initialize_gcp_client()

def upload_to_gcs(file_path, bucket_name=GCP_BUCKET_NAME):
    if not gcs_client:
        raise ValueError("GCS client is not initialized. Skipping file upload.")

    try:
        logger.info(f"Uploading file to Google Cloud Storage: {file_path}")
        bucket = gcs_client.bucket(bucket_name)
        blob = bucket.blob(os.path.basename(file_path))
        blob.upload_from_filename(file_path)
        logger.info(f"File uploaded successfully to GCS: {blob.public_url}")
        return blob.public_url
    except Exception as e:
        logger.error(f"Error uploading file to GCS: {e}")
        raise


def trigger_cloud_run_job(job_name, location="us-central1", overrides=None):
    # Retrieve service account credentials
    json_str = os.environ.get("GCP_SA_CREDENTIALS")
    if not json_str:
        raise ValueError("GCP_SA_CREDENTIALS environment variable not set.")
    
    credentials_info = json.loads(json_str)
    credentials = service_account.Credentials.from_service_account_info(credentials_info)

    # Initialize the JobsClient with the provided credentials
    client = JobsClient(credentials=credentials)

    # Construct the job path using project ID and location
    project_id = credentials_info.get("project_id")
    job_path = f"projects/{project_id}/locations/{location}/jobs/{job_name}"

    # Create the RunJobRequest with the specified overrides
    request = RunJobRequest(
        name=job_path,
        overrides=overrides  # Passing the overrides dictionary directly
    )

    try:
        # Trigger the job (non-blocking)
        operation = client.run_job(request=request)

        return {
            "operation_name": operation.operation.name,  # Return operation name to track job status
            "execution_name": operation.metadata.name,  # Execution name for tracking
            "job_submitted": True
        }
    except GoogleAPIError as e:
        # Handle any errors (e.g., authentication, bad request)
        return {
            "job_submitted": False,
            "error": str(e)
        }
