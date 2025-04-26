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
import json
import logging
from flask import Blueprint, request
from config import LOCAL_STORAGE_PATH
from services.authentication import authenticate
from app_utils import queue_task_wrapper

v1_job_status_bp = Blueprint('v1_job_status', __name__)
logger = logging.getLogger(__name__)

@v1_job_status_bp.route('/v1/job/<status_id>/status', methods=['GET'])
@authenticate
@queue_task_wrapper(bypass_queue=True)
def get_job_status(job_id, data, status_id=None):
    """
    Get the status of a job by its ID
    
    Args:
        job_id (str): Job ID assigned by queue_task_wrapper (unused)
        data (dict): Request data (unused)
        status_id (str): The job ID to look up from URL path
        
    Returns:
        Tuple of (job_status_data, endpoint_string, status_code)
    """
    logger.info(f"Retrieving status for job {status_id}")
    endpoint = f"/v1/job/{status_id}/status"
    
    try:
        # Construct the path to the job status file
        job_file_path = os.path.join(LOCAL_STORAGE_PATH, 'jobs', f"{status_id}.json")
        
        # Check if the job file exists
        if not os.path.exists(job_file_path):
            return {"error": "Job not found", "job_id": status_id}, endpoint, 404
        
        # Read the job status file
        with open(job_file_path, 'r') as file:
            job_status = json.load(file)
        
        # Return the job status file content directly
        return job_status, endpoint, 200
        
    except Exception as e:
        logger.error(f"Error retrieving status for job {status_id}: {str(e)}")
        return {"error": f"Failed to retrieve job status: {str(e)}"}, endpoint, 500 