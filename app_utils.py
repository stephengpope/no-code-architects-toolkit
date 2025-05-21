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

def discover_and_register_blueprints(app, base_dir='routes'):
    """
    Dynamically discovers and registers all Flask blueprints in the routes directory.
    Recursively searches all subdirectories for Python modules containing Blueprint instances.
    
    Args:
        app (Flask): The Flask application instance
        base_dir (str): Base directory to start searching for blueprints (default: 'routes')
    """
    import importlib
    import pkgutil
    import inspect
    import sys
    import os
    from flask import Blueprint
    import logging
    import glob

    logger = logging.getLogger(__name__)
    logger.info(f"Discovering blueprints in {base_dir}")
    
    # Add the current working directory to sys.path if it's not already there
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
    
    # Get the absolute path to the base directory
    if not os.path.isabs(base_dir):
        base_dir = os.path.join(cwd, base_dir)
    
    registered_blueprints = set()
    
    # Find all Python files in the routes directory, including subdirectories
    python_files = glob.glob(os.path.join(base_dir, '**', '*.py'), recursive=True)
    logger.info(f"Found {len(python_files)} Python files in {base_dir}")
    
    for file_path in python_files:
        try:
            # Convert file path to import path
            rel_path = os.path.relpath(file_path, cwd)
            # Remove .py extension
            module_path = os.path.splitext(rel_path)[0]
            # Convert path separators to dots for import
            module_path = module_path.replace(os.path.sep, '.')
            
            # Skip __init__.py files
            if module_path.endswith('__init__'):
                continue
                
            #logger.info(f"Attempting to import module: {module_path}")
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Find all Blueprint instances in the module
            for name, obj in inspect.getmembers(module):
                if isinstance(obj, Blueprint) and obj not in registered_blueprints:
                    pid = os.getpid()
                    logger.info(f"PID {pid} Registering: {module_path}")
                    app.register_blueprint(obj)
                    registered_blueprints.add(obj)
            
        except Exception as e:
            logger.error(f"Error importing module {module_path}: {str(e)}")
    
    logger.info(f"PID {pid} Registered {len(registered_blueprints)} blueprints")
    return registered_blueprints