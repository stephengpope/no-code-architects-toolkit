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
from services.gcp_toolkit import get_job_status
from google.api_core.exceptions import GoogleAPIError
import logging

logger = logging.getLogger(__name__)

# Create blueprint
v1_gcp_job_status_bp = Blueprint('v1_gcp_job_status', __name__)

@v1_gcp_job_status_bp.route('/v1/gcp/job/status', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "credentials": {
            "oneOf": [
                {"type": "string"},
                {"type": "object"}
            ]
        }
    },
    "required": ["name"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def gcp_job_status_endpoint(job_id, data):
    name = data.get('name')
    credentials = data.get('credentials')
    
    logger.info(f"Job {job_id}: Getting job status for {name}")
    
    try:
        # Get job status
        status = get_job_status(
            name=name,
            credentials=credentials
        )
        
        logger.info(f"Job {job_id}: Successfully retrieved job status")
        return status, "/v1/gcp/job/status", 200
        
    except GoogleAPIError as e:
        logger.error(f"Job {job_id}: Google API error getting job status - {str(e)}")
        return str(e), "/v1/gcp/job/status", 400
    except Exception as e:
        logger.error(f"Job {job_id}: Error getting job status - {str(e)}")
        return str(e), "/v1/gcp/job/status", 500 