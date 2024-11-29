# code_execution.py

from flask import Blueprint, request, jsonify
from app_utils import queue_task_wrapper
from services.authentication import authenticate
from services.webhook import send_webhook
import subprocess
import uuid
import os
import logging

code_execution_bp = Blueprint('code_execution', __name__)
logger = logging.getLogger(__name__)

@code_execution_bp.route('/v1/run/python', methods=['POST'])
@authenticate
@queue_task_wrapper(bypass_queue=False)
def run_python_code(job_id, data):
    code = data.get('code')
    webhook_url = data.get('webhook_url')
    id = data.get('id', job_id)

    # Save code to a temporary file
    code_filename = f'/tmp/{job_id}.py'
    with open(code_filename, 'w') as code_file:
        code_file.write(code)

    try:
        # Execute the code securely
        result = subprocess.check_output(
            ['python', code_filename],
            stderr=subprocess.STDOUT,
            timeout=5,
            text=True
        )
        logger.info(f"Job {job_id}: Code executed successfully")
    except subprocess.CalledProcessError as e:
        result = e.output
        logger.error(f"Job {job_id}: Execution error - {e.output}")
    except subprocess.TimeoutExpired:
        result = 'Execution timed out.'
        logger.error(f"Job {job_id}: Execution timed out")

    # Clean up the code file
    os.remove(code_filename)

    response_data = {
        "id": id,
        "Response": result
    }

    if webhook_url:
        send_webhook(webhook_url, response_data)
        return jsonify({"id": id, "message": "processing"}), 202
    else:
        return jsonify(response_data), 200

@code_execution_bp.route('/v1/run/javascript', methods=['POST'])
@authenticate
@queue_task_wrapper(bypass_queue=False)
def run_javascript_code(job_id, data):
    code = data.get('code')
    webhook_url = data.get('webhook_url')
    id = data.get('id', job_id)

    # Save code to a temporary file
    code_filename = f'/tmp/{job_id}.js'
    with open(code_filename, 'w') as code_file:
        code_file.write(code)

    try:
        # Execute the code securely
        result = subprocess.check_output(
            ['node', code_filename],
            stderr=subprocess.STDOUT,
            timeout=5,
            text=True
        )
        logger.info(f"Job {job_id}: Code executed successfully")
    except subprocess.CalledProcessError as e:
        result = e.output
        logger.error(f"Job {job_id}: Execution error - {e.output}")
    except subprocess.TimeoutExpired:
        result = 'Execution timed out.'
        logger.error(f"Job {job_id}: Execution timed out")

    # Clean up the code file
    os.remove(code_filename)

    response_data = {
        "id": id,
        "Response": result
    }

    if webhook_url:
        send_webhook(webhook_url, response_data)
        return jsonify({"id": id, "message": "processing"}), 202
    else:
        return jsonify(response_data), 200