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
import uuid
import shutil
import logging
import requests
from urllib.parse import urlparse, parse_qs
import mimetypes

logger = logging.getLogger(__name__)

# Directories allowed for file:// URI access
ALLOWED_LOCAL_DIRS = ['/data/input', os.environ.get('LOCAL_STORAGE_PATH', '/tmp')]

def get_extension_from_url(url):
    """Extract file extension from URL, local path, or content type.

    Args:
        url (str): The URL or file:// URI to extract the extension from

    Returns:
        str: The file extension including the dot (e.g., '.jpg')

    Raises:
        ValueError: If no valid extension can be determined from the URL or content type
    """
    parsed_url = urlparse(url)

    # For file:// URIs, get extension directly from the path
    if parsed_url.scheme == 'file':
        path = parsed_url.path
        ext = os.path.splitext(path)[1].lower()
        if ext:
            return ext
        raise ValueError(f"Could not determine file extension from local path: {path}")

    # First try to get extension from URL path
    path = parsed_url.path
    if path:
        ext = os.path.splitext(path)[1].lower()
        if ext:
            return ext

    # If no extension in URL, try to determine from content type
    try:
        response = requests.head(url, allow_redirects=True)
        content_type = response.headers.get('content-type', '').split(';')[0]
        ext = mimetypes.guess_extension(content_type)
        if ext:
            return ext.lower()
    except:
        pass

    # If we can't determine the extension, raise an error
    raise ValueError(f"Could not determine file extension from URL: {url}")

def download_file(url, storage_path="/tmp/"):
    """Download a file from URL to local storage, or copy from local path for file:// URIs."""
    # Create storage directory if it doesn't exist
    os.makedirs(storage_path, exist_ok=True)

    parsed = urlparse(url)

    # Handle file:// URIs (local files from volume mount)
    if parsed.scheme == 'file':
        local_source = os.path.realpath(parsed.path)

        # Security: restrict to allowed directories
        if not any(local_source.startswith(os.path.realpath(d)) for d in ALLOWED_LOCAL_DIRS):
            raise ValueError(f"Access denied: file:// URIs must reference files in {ALLOWED_LOCAL_DIRS}")

        if not os.path.exists(local_source):
            raise FileNotFoundError(f"Local file not found: {local_source}")

        _, ext = os.path.splitext(local_source)
        if not ext:
            raise ValueError(f"Could not determine file extension from local path: {local_source}")

        file_id = str(uuid.uuid4())
        local_filename = os.path.join(storage_path, f"{file_id}{ext.lower()}")

        # Copy file (not symlink) so cleanup logic can safely delete the copy
        shutil.copy2(local_source, local_filename)
        logger.info(f"Copied local file {local_source} to {local_filename}")
        return local_filename

    # Existing HTTP/HTTPS download logic
    file_id = str(uuid.uuid4())
    extension = get_extension_from_url(url)
    local_filename = os.path.join(storage_path, f"{file_id}{extension}")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return local_filename
    except Exception as e:
        if os.path.exists(local_filename):
            os.remove(local_filename)
        raise e
