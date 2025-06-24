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
from services.gcp_toolkit import trigger_cloud_run_job
from google.api_core.exceptions import GoogleAPIError
import os
import json
import logging
import requests

logger = logging.getLogger(__name__)
v1_gcp_job_run_bp = Blueprint('v1_gcp_job_run', __name__)

@v1_gcp_job_run_bp.route('/v1/gcp/job/run', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "job_name": {"type": "string"},
        "location": {"type": "string"},
        "credentials": {
            "oneOf": [
                {"type": "string"},
                {"type": "object"}
            ]
        },
        "overrides": {
            "type": "object",
            "properties": {
                "container_overrides": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "env": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "value": {"type": "string"}
                                    },
                                    "required": ["name", "value"]
                                }
                            },
                            "args": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                        },
                        "additionalProperties": True
                    }
                },
                "task_count": {
                    "type": "integer",
                    "minimum": 1
                },
                "timeout": {
                    "type": "string",
                    "pattern": "^[0-9]+s$"
                }
            }
        }
    },
    "required": ["job_name"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def gcp_job_run_endpoint(job_id, data):
    job_name = data.get('job_name')
    location = data.get('location', 'us-central1')
    credentials = data.get('credentials')
    overrides = data.get('overrides')
    
    logger.info(f"Job {job_id}: Starting Cloud Run job {job_name} in {location}")
    
    try:
        response = trigger_cloud_run_job(
            job_name=job_name,
            location=location,
            credentials=credentials,
            overrides=overrides
        )
        
        logger.info(f"Job {job_id}: Successfully started Cloud Run job")
        return response, "/v1/gcp/job/run", 200
        
    except GoogleAPIError as e:
        logger.error(f"Job {job_id}: Google API error starting Cloud Run job - {str(e)}")
        return str(e), "/v1/gcp/job/run", 400
    except Exception as e:
        logger.error(f"Job {job_id}: Error starting Cloud Run job - {str(e)}")
        return str(e), "/v1/gcp/job/run", 500 