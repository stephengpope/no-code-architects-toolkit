# services/v1/code_execution.py

import subprocess
import uuid
import os
import logging

logger = logging.getLogger(__name__)

def execute_python_code(code):
    job_id = str(uuid.uuid4())
    code_filename = f'/tmp/{job_id}.py'
    with open(code_filename, 'w') as code_file:
        code_file.write(code)
    
    try:
        result = subprocess.check_output(
            ['python', code_filename],
            stderr=subprocess.STDOUT,
            timeout=5,
            text=True
        )
        logger.info(f"Job {job_id}: Python code executed successfully")
    except subprocess.CalledProcessError as e:
        result = e.output
        logger.error(f"Job {job_id}: Python execution error - {e.output}")
    except subprocess.TimeoutExpired:
        result = 'Execution timed out.'
        logger.error(f"Job {job_id}: Python execution timed out")
    finally:
        os.remove(code_filename)
    
    return result

def execute_javascript_code(code):
    job_id = str(uuid.uuid4())
    code_filename = f'/tmp/{job_id}.js'
    with open(code_filename, 'w') as code_file:
        code_file.write(code)
    
    try:
        result = subprocess.check_output(
            ['node', code_filename],
            stderr=subprocess.STDOUT,
            timeout=5,
            text=True
        )
        logger.info(f"Job {job_id}: JavaScript code executed successfully")
    except subprocess.CalledProcessError as e:
        result = e.output
        logger.error(f"Job {job_id}: JavaScript execution error - {e.output}")
    except subprocess.TimeoutExpired:
        result = 'Execution timed out.'
        logger.error(f"Job {job_id}: JavaScript execution timed out")
    finally:
        os.remove(code_filename)
    
    return result