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
import requests
from urllib.parse import urlparse, parse_qs

def download_file(url, storage_path="/tmp/"):
    # Parse the URL to extract the file ID from the query parameters
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    # Use the 'id' parameter as the filename if it exists
    file_id = str(uuid.uuid4())
    
    #if not file_id:
    #    raise ValueError("Invalid URL: 'id' parameter not found in the URL")
    
    # Ensure the storage directory exists
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    
    # Use the file ID as the filename and save it in the specified storage path
    local_filename = os.path.join(storage_path, f"{file_id}.mp4")  # Assuming mp4; adjust extension if needed
    
    # Download the file
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    return local_filename


def delete_old_files():
    now = time.time()
    for filename in os.listdir(STORAGE_PATH):
        file_path = os.path.join(STORAGE_PATH, filename)
        if os.path.isfile(file_path) and os.stat(file_path).st_mtime < now - 3600:
            os.remove(file_path)
