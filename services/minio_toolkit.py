import os
import boto3
import logging
from botocore.config import Config
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def parse_minio_url(minio_url):
    """Parse MinIO URL to extract endpoint URL.
    
    Args:
        minio_url (str): MinIO endpoint URL (e.g., http://minio:9000)
        
    Returns:
        str: endpoint_url
        
    Raises:
        ValueError: If the URL is malformed
    """
    logger.debug(f"Parsing MinIO URL: {minio_url}")
    
    try:
        parsed_url = urlparse(minio_url)
        logger.debug(f"Parsed URL components - scheme: {parsed_url.scheme}, netloc: {parsed_url.netloc}")
        
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid MinIO URL format: missing scheme or host")
            
        # Construct endpoint URL
        endpoint_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        logger.debug(f"Constructed endpoint URL: {endpoint_url}")
        
        return endpoint_url
        
    except Exception as e:
        logger.error(f"Failed to parse MinIO URL: {str(e)}")
        raise ValueError(f"Failed to parse MinIO URL: {str(e)}") from e

def upload_to_minio(file_path, minio_url, access_key, secret_key, bucket_name, region):
    """Upload a file to MinIO storage.
    
    Args:
        file_path (str): Path to the file to upload
        minio_url (str): MinIO endpoint URL (e.g., http://minio:9000)
        access_key (str): MinIO access key
        secret_key (str): MinIO secret key
    
    Returns:
        str: Public URL of the uploaded file
    """
    # Get the endpoint URL
    endpoint_url = parse_minio_url(minio_url)
    
    if not bucket_name:
        raise ValueError("MINIO_BUCKET_NAME environment variable must be set")
    
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    
       
    client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(
            signature_version="s3v4",
            s3={'addressing_style': 'path'},
            region_name=region  # Add default region
        )
    )


    try:
        # Upload the file to the specified bucket
        with open(file_path, 'rb') as data:
            object_name = os.path.basename(file_path)
            client.upload_fileobj(data, bucket_name, object_name)

        # Construct the file URL
        file_url = f"{endpoint_url}/{bucket_name}/{object_name}"
        return file_url
    except Exception as e:
        logger.error(f"Error uploading file to MinIO: {e}")
        raise