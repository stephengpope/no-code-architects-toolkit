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

from flask import Blueprint, request, jsonify
from services.authentication import authenticate
from app_utils import validate_payload, queue_task_wrapper
from services.v1.gcp.upload import stream_upload_to_gcs
import os
import json
import logging

logger = logging.getLogger(__name__)
v1_gcp_upload_bp = Blueprint('v1_gcp_upload', __name__)

@v1_gcp_upload_bp.route('/v1/gcp/upload', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "filename": {"type": "string"},
        "file_url": {"type": "string", "format": "uri"},
        "public": {"type": "boolean"},
        "download_headers": {"type": "object"}
    },
    "required": ["file_url"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def gcp_upload_endpoint(job_id, data):
    try:
        filename = data.get('filename')  # Optional, will default to original filename if not provided
        make_public = data.get('public', False)  # Default to private
        download_headers = data.get('download_headers')  # Optional headers for authentication
        
        # Handle file upload from URL
        file_url = data.get('file_url')
        logger.info(f"Job {job_id}: Starting GCS streaming upload from {file_url}")
        result = stream_upload_to_gcs(file_url, filename, make_public, download_headers)
        
        logger.info(f"Job {job_id}: Successfully uploaded to GCS")
        return result, "/v1/gcp/upload", 200
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error uploading to GCS - {str(e)}")
        return str(e), "/v1/gcp/upload", 500