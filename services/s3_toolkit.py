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

# START ---- Добавил я для определения signature_version
from botocore.client import Config
# END ---- Добавил я для определения signature_version

logger = logging.getLogger(__name__)

def upload_to_s3(file_path, s3_url, access_key, secret_key, bucket_name, region):
    # Parse the S3 URL into bucket, region, and endpoint
    #bucket_name, region, endpoint_url = parse_s3_url(s3_url)

    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )
    
    # START ---- Добавил я для определения signature_version

    client = session.client(
        's3',
        endpoint_url=s3_url,
        config=Config(signature_version='s3')   # 🔑 фикс
    )

    # client = session.client('s3', endpoint_url=s3_url) # - я закоментил
    
    # END ---- Добавил я для определения signature_version

    try:
        # Upload the file to the specified S3 bucket
        with open(file_path, 'rb') as data:
            client.upload_fileobj(data, bucket_name, os.path.basename(file_path), ExtraArgs={'ACL': 'public-read'})

        # URL encode the filename for the URL
        encoded_filename = quote(os.path.basename(file_path))
        file_url = f"{s3_url}/{bucket_name}/{encoded_filename}"
        return file_url
    except Exception as e:
        logger.error(f"Error uploading file to S3: {e}")
        raise



# START ---- Добавил я list_objects_v2 - для получения списка файлов из бакета
# ⚡️ Новый метод для листинга
def list_files(s3_url, access_key, secret_key, bucket_name, region, prefix=""):
    """
    Возвращает список всех файлов в бакете (можно ограничить prefix).
    """
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )
    client = session.client(
        's3',
        endpoint_url=s3_url,
        config=Config(signature_version='s3')
    )
    try:
        response = client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        files = []
        if "Contents" in response:
            for obj in response["Contents"]:
                files.append(obj["Key"])
        return files
    except Exception as e:
        logger.error(f"Error listing files in S3: {e}")
        raise

# END ---- Добавил я list_objects_v2 - для получения списка файлов из бакета
