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
import logging
from flask import Blueprint, request, jsonify
from services.authentication import authenticate
from services.cloud_storage import upload_file
from config import LOCAL_STORAGE_PATH

logger = logging.getLogger(__name__)
v1_files_upload_bp = Blueprint('v1_files_upload', __name__)


@v1_files_upload_bp.route('/v1/files/upload', methods=['POST'])
@authenticate
def files_upload(job_id=None):
    """Accept a multipart file upload, save to cloud storage, return the URL.

    The returned URL can then be passed as media_url/video_url to any
    processing endpoint.

    Request: multipart/form-data with a 'file' field.
    Response: {"url": "<cloud_storage_url>", "filename": "<original_name>"}
    """
    if 'file' not in request.files:
        return jsonify({"message": "No 'file' field in multipart request"}), 400

    uploaded = request.files['file']
    if not uploaded.filename:
        return jsonify({"message": "Empty filename"}), 400

    # Determine extension from the original filename
    _, ext = os.path.splitext(uploaded.filename)
    if not ext:
        ext = '.bin'

    # Save to a temp path
    file_id = str(uuid.uuid4())
    local_path = os.path.join(LOCAL_STORAGE_PATH, f"{file_id}{ext}")

    try:
        uploaded.save(local_path)
        logger.info(f"Saved uploaded file to {local_path} ({uploaded.filename})")

        # Upload to configured storage provider (S3, GCP, or local)
        cloud_url = upload_file(local_path)
        logger.info(f"Uploaded to storage: {cloud_url}")

        return jsonify({
            "url": cloud_url,
            "filename": uploaded.filename,
        }), 200

    except Exception as e:
        logger.error(f"File upload failed: {e}")
        return jsonify({"message": str(e)}), 500

    finally:
        # Clean up the temp file
        if os.path.exists(local_path):
            os.remove(local_path)
