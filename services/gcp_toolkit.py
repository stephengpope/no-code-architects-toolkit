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
import requests
from google.oauth2 import service_account
from google.cloud import storage
from google.cloud.run_v2 import JobsClient, RunJobRequest, ExecutionsClient
from google.protobuf.json_format import MessageToDict

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



def load_gcp_credentials(credentials=None):
    credentials_info = None
    if credentials:
        if isinstance(credentials, str):
            if credentials.startswith(('http://', 'https://')):
                try:
                    response = requests.get(credentials)
                    response.raise_for_status()
                    credentials_info = response.json()
                except Exception as e:
                    raise ValueError(f"Failed to fetch credentials from URL: {e}")
            else:
                try:
                    credentials_info = json.loads(credentials)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to parse credentials JSON string: {e}")
        else:
            credentials_info = credentials

    if not credentials_info:
        json_str = os.environ.get("GCP_SA_CREDENTIALS")
        if json_str:
            try:
                credentials_info = json.loads(json_str)
            except json.JSONDecodeError:
                raise ValueError("Failed to parse GCP_SA_CREDENTIALS from environment variable.")

    if not credentials_info:
        raise ValueError("GCP credentials must be provided either in the request payload or as the 'GCP_SA_CREDENTIALS' environment variable.")

    try:
        creds = service_account.Credentials.from_service_account_info(credentials_info)
    except Exception as e:
        raise ValueError(f"Failed to create credentials from provided info: {e}")
    return credentials_info, creds

def trigger_cloud_run_job(job_name, location="us-central1", credentials=None, overrides=None):
    credentials_info, creds = load_gcp_credentials(credentials)
    client = JobsClient(credentials=creds)

    project_id = credentials_info.get("project_id")
    if not project_id:
        raise ValueError("'project_id' not found in GCP credentials.")
        
    job_path = f"projects/{project_id}/locations/{location}/jobs/{job_name}"

    request = RunJobRequest(
        name=job_path,
        overrides=overrides,
    )

    operation = client.run_job(request=request)
    return MessageToDict(operation.metadata._pb)

def get_job_status(name, credentials=None):
    credentials_info, creds = load_gcp_credentials(credentials)
    client = ExecutionsClient(credentials=creds)

    execution = client.get_execution(name=name)
    execution_dict = MessageToDict(execution._pb)

    # Sort conditions by lastTransitionTime (newest first)
    if "conditions" in execution_dict:
        conditions = execution_dict["conditions"]
        if conditions:
            sorted_conditions = sorted(conditions, key=lambda x: x.get("lastTransitionTime", ""), reverse=True)
            execution_dict["conditions"] = sorted_conditions

    return execution_dict
