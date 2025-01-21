import logging
import os
from urllib.parse import urlparse

import boto3

logger = logging.getLogger(__name__)

def parse_s3_url(s3_url):
    """Parse S3 URL to extract bucket name, region, and endpoint URL."""
    parsed_url = urlparse(s3_url)
    
    # Extract bucket name from the host
    bucket_name = parsed_url.hostname.split('.')[0]
    
    # Extract region from the host
    region = parsed_url.hostname.split('.')[1]
    
    # Use environment variable or default to DigitalOcean Spaces
    endpoint_url = os.environ.get("S3_ENDPOINT_URL")
    
    return bucket_name, region, endpoint_url

def upload_to_s3(file_path, s3_url, access_key, secret_key):
    # Parse the S3 URL into bucket, region, and endpoint
    bucket_name, region, endpoint_url = parse_s3_url(s3_url)
    
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )
    
    client = session.client('s3', endpoint_url=endpoint_url)

    try:
        # Upload the file to the specified S3 bucket
        client.upload_file(file_path, bucket_name, os.path.basename(file_path))
    except Exception as e:
        logger.error(f"Error uploading file to S3: {e}")
        raise
