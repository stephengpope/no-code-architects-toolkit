import os
import logging
import requests
import json
import time
from urllib.parse import urlparse, unquote
import uuid

logger = logging.getLogger(__name__)

def get_filename_from_url(url):
    """Extract filename from URL."""
    path = urlparse(url).path
    filename = os.path.basename(unquote(path))
    
    # If filename cannot be determined, generate a UUID
    if not filename or filename == '':
        filename = f"{uuid.uuid4()}"
    
    return filename

def initiate_resumable_upload(filename, folder_id, access_token, mime_type='application/octet-stream'):
    """
    Initiates a resumable upload session with Google Drive and returns the upload URL.
    
    Args:
        filename (str): Name of the file to be created in Google Drive
        folder_id (str): Google Drive folder ID where the file will be stored
        access_token (str): OAuth bearer token for Google Drive API authentication
        mime_type (str, optional): MIME type of the file. Defaults to 'application/octet-stream'.
        
    Returns:
        str: URL for the resumable upload session
    """
    url = 'https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Upload-Content-Type': mime_type
    }
    metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    response = requests.post(url, headers=headers, data=json.dumps(metadata))
    response.raise_for_status()
    upload_url = response.headers['Location']
    return upload_url

def stream_upload_to_gdrive(file_url, folder_id, access_token, custom_filename=None):
    """
    Stream a file from a URL directly to Google Drive without saving to disk.
    
    Args:
        file_url (str): URL of the file to download
        folder_id (str): Google Drive folder ID to upload to
        access_token (str): OAuth bearer token for Google Drive API authentication
        custom_filename (str, optional): Custom filename for the uploaded file
        
    Returns:
        dict: Information about the uploaded file
    """
    try:
        # Determine filename (use custom if provided, otherwise extract from URL)
        if custom_filename:
            filename = custom_filename
        else:
            filename = get_filename_from_url(file_url)
        
        # Get the total size of the file
        head_response = requests.head(file_url, allow_redirects=True, timeout=30)
        head_response.raise_for_status()
        total_size = int(head_response.headers.get('Content-Length', 0))
        
        if total_size == 0:
            # Try a GET request to determine size if HEAD doesn't include Content-Length
            get_response = requests.get(file_url, stream=True, timeout=30)
            get_response.raise_for_status()
            total_size = int(get_response.headers.get('Content-Length', 0))
            if total_size == 0:
                raise ValueError("Content-Length header is missing or zero")
            get_response.close()
        
        logger.info(f"File size determined: {total_size} bytes")
        
        # Initiate upload session
        mime_type = 'application/octet-stream'  # Default mime type
        upload_url = initiate_resumable_upload(filename, folder_id, access_token, mime_type)
        logger.info(f"Resumable upload session initiated for {filename}")
        
        # Upload file in chunks by streaming from source
        bytes_uploaded = 0
        chunk_size = 5 * 1024 * 1024  # 5MB chunks
        max_retries = 5
        retry_delay = 5  # seconds
        
        with requests.get(file_url, stream=True) as r:
            r.raise_for_status()
            iterator = r.iter_content(chunk_size=chunk_size)
            
            for chunk in iterator:
                if chunk:
                    for attempt in range(max_retries):
                        start = bytes_uploaded
                        end = bytes_uploaded + len(chunk) - 1
                        content_range = f'bytes {start}-{end}/{total_size}'
                        headers = {
                            'Content-Length': str(len(chunk)),
                            'Content-Range': content_range,
                        }
                        
                        try:
                            upload_response = requests.put(
                                upload_url,
                                headers=headers,
                                data=chunk
                            )
                            
                            if upload_response.status_code in (200, 201):
                                # Upload complete
                                file_id = upload_response.json()['id']
                                file_link = f"https://drive.google.com/file/d/{file_id}/view"
                                
                                logger.info(f"Upload complete. File ID: {file_id}")
                                
                                # Webhook handling is done in app.py through the queue_task_wrapper
                                
                                return {
                                    'file_id': file_id,
                                    'file_url': file_link,
                                    'filename': filename,
                                    'size': total_size
                                }
                                
                            elif upload_response.status_code == 308:
                                # Resumable upload incomplete
                                bytes_uploaded = end + 1
                                break  # Break retry loop and continue with next chunk
                                
                            else:
                                # Handle unexpected status codes
                                logger.error(f"Unexpected status code: {upload_response.status_code}")
                                if attempt < max_retries - 1:
                                    logger.info(f"Retrying upload chunk after {retry_delay} seconds...")
                                    time.sleep(retry_delay)
                                    continue
                                else:
                                    logger.error(f"Max retries reached. Upload failed.")
                                    raise Exception(f"Upload failed with status code {upload_response.status_code}")
                                    
                        except requests.exceptions.RequestException as e:
                            logger.error(f"Network error during upload: {e}")
                            if attempt < max_retries - 1:
                                logger.info(f"Retrying upload chunk after {retry_delay} seconds...")
                                time.sleep(retry_delay)
                                continue
                            else:
                                logger.error(f"Max retries reached. Upload failed.")
                                raise Exception(f"Upload failed after {max_retries} retries: {str(e)}")
                    
                    # Log progress periodically
                    if total_size > 0:
                        progress_percentage = (bytes_uploaded / total_size) * 100
                        if progress_percentage % 10 < 1:  # Log roughly every 10%
                            logger.info(f"Upload progress: {progress_percentage:.1f}% ({bytes_uploaded}/{total_size} bytes)")
        
        raise Exception("Upload did not complete successfully")
            
    except Exception as e:
        logger.error(f"Error streaming file to Google Drive: {e}")
        
        # Error webhook handling is done in app.py through the queue_task_wrapper
                
        raise