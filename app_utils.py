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



from flask import request, jsonify, current_app
from functools import wraps
import jsonschema
import os
import json
import time
from config import LOCAL_STORAGE_PATH

def validate_payload(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.json:
                return jsonify({"message": "Missing JSON in request"}), 400
            try:
                jsonschema.validate(instance=request.json, schema=schema)
            except jsonschema.exceptions.ValidationError as validation_error:
                return jsonify({"message": f"Invalid payload: {validation_error.message}"}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_job_status(job_id, data):
    """
    Log job status to a file in the STORAGE_PATH/jobs folder
    
    Args:
        job_id (str): The unique job ID
        data (dict): Data to write to the log file
    """
    jobs_dir = os.path.join(LOCAL_STORAGE_PATH, 'jobs')
    
    # Create jobs directory if it doesn't exist
    if not os.path.exists(jobs_dir):
        os.makedirs(jobs_dir, exist_ok=True)
    
    # Create or update the job log file
    job_file = os.path.join(jobs_dir, f"{job_id}.json")
    
    # Write data directly to file
    with open(job_file, 'w') as f:
        json.dump(data, f, indent=2)

def queue_task_wrapper(bypass_queue=False):
    def decorator(f):
        def wrapper(*args, **kwargs):
            return current_app.queue_task(bypass_queue=bypass_queue)(f)(*args, **kwargs)
        return wrapper
    return decorator