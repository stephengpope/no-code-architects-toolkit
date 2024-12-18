import os
import requests
import tempfile
import logging
import base64
from config import get_storage_provider

logger = logging.getLogger(__name__)

def upload_file_service(file_url=None, file_binary=None, file_name=None, bucket_name=None, content_type=None):
    """
    Handles the uploading of a file to the specified cloud storage provider.

    Parameters:
        file_url (str): URL of the file to upload.
        file_binary (str): Base64-encoded binary data of the file.
        file_name (str): Desired name for the uploaded file.
        bucket_name (str): Name of the target bucket.
        content_type (str): MIME type of the file.

    Returns:
        str: URL of the uploaded file in cloud storage.
    """
    # Determine the source type
    if file_url:
        # Download the file from the URL
        response = requests.get(file_url)
        response.raise_for_status()
        file_content = response.content
        if not file_name:
            file_name = os.path.basename(file_url)
    elif file_binary:
        # Decode the base64 file binary
        file_content = base64.b64decode(file_binary)
        if not file_name:
            file_name = 'uploaded_file'
    else:
        raise ValueError("Either file_url or file_binary must be provided.")

    # Save the file temporarily
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, file_name)

    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_content)

    # Get the storage provider from config.py
    storage_provider = get_storage_provider()

    # Upload the file using the storage provider
    uploaded_file_url = storage_provider.upload_file(
        file_path=temp_file_path,
        file_name=file_name,
        bucket_name=bucket_name,
        content_type=content_type
    )

    # Remove the temporary file
    os.remove(temp_file_path)

    return uploaded_file_url