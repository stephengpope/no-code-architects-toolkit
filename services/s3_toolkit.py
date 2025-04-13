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
import boto3
import logging
from urllib.parse import urlparse, quote

logger = logging.getLogger(__name__)

def upload_to_s3(file_path, s3_url, access_key, secret_key, bucket_name, region):
    from botocore.config import Config
    
    # Create S3 client with proper configuration
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )
    
    # Configure with signature version 4 and payload signing
    s3_config = Config(
        signature_version='s3v4',
        s3={'payload_signing_enabled': True}
    )
    
    client = session.client('s3', endpoint_url=s3_url, config=s3_config)

    try:
        # Upload the file using put_object instead of upload_fileobj
        with open(file_path, 'rb') as data:
            file_content = data.read()
            client.put_object(
                Bucket=bucket_name,
                Key=os.path.basename(file_path),
                Body=file_content,
                ACL='public-read'
            )

        # URL encode the filename for the URL
        encoded_filename = quote(os.path.basename(file_path))
        file_url = f"{s3_url}/{bucket_name}/{encoded_filename}"
        return file_url
    except Exception as e:
        logger.error(f"Error uploading file to S3: {e}")
        raise
