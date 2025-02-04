import os
import boto3
import logging

logger = logging.getLogger(__name__)

def upload_to_s3(file_path, access_key, secret_key):
    # Get S3 endpoint from environment variables
    endpoint_url = os.getenv('S3_ENDPOINT_URL')
    
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    client = session.client('s3', endpoint_url=endpoint_url)

    try:
        with open(file_path, 'rb') as data:
            # Note: Here the bucket parameter is set to an empty string.
            client.upload_fileobj(data, "", os.path.basename(file_path), ExtraArgs={'ACL': 'public-read'})
        file_url = f"{endpoint_url}/{os.path.basename(file_path)}"
        return file_url
    except Exception as e:
        logger.error(f"Error uploading file to S3: {e}")
        raise
