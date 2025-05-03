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
from services.v1.s3.upload_file import stream_file_to_s3
import os
import json
import logging

logger = logging.getLogger(__name__)
v1_s3_upload_file_bp = Blueprint('v1_s3_upload_file', __name__)

@v1_s3_upload_file_bp.route('/v1/s3/upload/file', methods=['POST'])
@authenticate
@queue_task_wrapper(bypass_queue=False)
def s3_upload_file_endpoint(job_id, data):
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return "No file provided", "/v1/s3/upload/file", 400
            
        file = request.files['file']
        if file.filename == '':
            return "No selected file", "/v1/s3/upload/file", 400
            
        # Get optional parameters from form data
        filename = request.form.get('filename')  # Optional custom filename
        make_public = request.form.get('public', 'false').lower() == 'true'  # Default to private
        
        logger.info(f"Job {job_id}: Starting S3 file upload for {file.filename}")
        
        # Call the service function to handle the upload
        result = stream_file_to_s3(file, filename, make_public)
        
        logger.info(f"Job {job_id}: Successfully uploaded file to S3")
        
        return result, "/v1/s3/upload/file", 200
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error uploading file to S3 - {str(e)}")
        return str(e), "/v1/s3/upload/file", 500
