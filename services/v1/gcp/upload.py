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
import logging
import requests
import json
from google.cloud import storage
from google.oauth2 import service_account
from urllib.parse import urlparse, unquote
import uuid

logger = logging.getLogger(__name__)

def get_gcs_client():
    """Create and return a Google Cloud Storage client using service account credentials."""
    credentials_json = os.environ.get('GCP_SA_CREDENTIALS')
    if not credentials_json:
        raise ValueError("GCP_SA_CREDENTIALS environment variable is not set")
    
    try:
        # Parse the JSON credentials
        credentials_info = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/devstorage.full_control']
        )
        return storage.Client(credentials=credentials)
    except json.JSONDecodeError:
        raise ValueError("GCP_SA_CREDENTIALS is not valid JSON")
    except Exception as e:
        raise ValueError(f"Failed to create GCS client: {str(e)}")

def get_filename_from_url(url):
    """Extract filename from URL."""
    path = urlparse(url).path
    filename = os.path.basename(unquote(path))
    
    # If filename cannot be determined, generate a UUID
    if not filename or filename == '':
        filename = f"{uuid.uuid4()}"
    
    return filename

def stream_upload_to_gcs(file_url, custom_filename=None, make_public=False, download_headers=None):
    try:
        # Get GCS configuration
        bucket_name = os.environ.get('GCP_BUCKET_NAME')
        if not bucket_name:
            raise ValueError("GCP_BUCKET_NAME environment variable is not set")

        # Get GCS client
        client = get_gcs_client()
        bucket = client.bucket(bucket_name)

        # Determine filename (use custom if provided, otherwise extract from URL)
        if custom_filename:
            filename = custom_filename
        else:
            filename = get_filename_from_url(file_url)

        # Create a new blob
        blob = bucket.blob(filename)

        # Stream the file from URL
        response = requests.get(file_url, stream=True, headers=download_headers)
        response.raise_for_status()

        # Get content type from response headers
        content_type = response.headers.get('content-type', 'application/octet-stream')

        # Create a streaming upload
        blob.upload_from_file(
            response.raw,
            content_type=content_type
        )

        # Return the public URL
        return {
            'file_url': blob.public_url,
            'filename': filename,
            'bucket': bucket_name,
            'public': True,  # Always return public URL like gcp_toolkit
            'content_type': content_type
        }

    except Exception as e:
        logger.error(f"Error streaming file to GCS: {e}")
        raise 