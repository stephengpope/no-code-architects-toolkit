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
import logging
from flask import Blueprint, request
from services.authentication import authenticate
from app_utils import validate_payload, queue_task_wrapper
import subprocess
import tempfile
import json
import textwrap

v1_code_execute_bp = Blueprint('v1_code_execute', __name__)
logger = logging.getLogger(__name__)

@v1_code_execute_bp.route('/v1/code/execute/python', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "code": {"type": "string"},
        "timeout": {"type": "integer", "minimum": 1, "maximum": 300},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["code"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def execute_python(job_id, data):
    logger.info(f"Job {job_id}: Received Python code execution request")
    
    try:
        code = data['code']
        timeout = data.get('timeout', 30)
        
        # Indent user code
        indented_code = textwrap.indent(code, '    ')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            template = '''import sys
import json
from io import StringIO
import contextlib

@contextlib.contextmanager
def capture_output():
    stdout, stderr = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = stdout, stderr
        yield stdout, stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

def execute_code():
{}

with capture_output() as (stdout, stderr):
    try:
        result_value = execute_code()
    except Exception as e:
        print(f"Error: {{str(e)}}", file=sys.stderr)
        result_value = None

result = {{
    'stdout': stdout.getvalue(),
    'stderr': stderr.getvalue(),
    'return_value': result_value
}}
print(json.dumps(result))
'''
            
            final_code = template.format(indented_code)
            temp_file.write(final_code)
            temp_file.flush()
            
            # Log the generated code for debugging
            logger.debug(f"Generated code:\n{final_code}")
            
            try:
                result = subprocess.run(
                    ['python3', temp_file.name],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                try:
                    output = json.loads(result.stdout)
                    if result.returncode != 0 or output['stderr']:
                        return {
                            'error': output['stderr'] or 'Execution failed',
                            'stdout': output['stdout'],
                            'exit_code': result.returncode
                        }, '/v1/code/execute/python', 400
                    
                    return {
                        'result': output['return_value'],
                        'stdout': output['stdout'],
                        'stderr': output['stderr'],
                        'exit_code': result.returncode
                    }, '/v1/code/execute/python', 200
                    
                except json.JSONDecodeError:
                    return {
                        'error': 'Failed to parse execution result',
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'exit_code': result.returncode
                    }, '/v1/code/execute/python', 500
                    
            except subprocess.TimeoutExpired:
                return {"error": f"Execution timed out after {timeout} seconds"}, '/v1/code/execute/python', 408
            except subprocess.SubprocessError as e:
                return {"error": f"Execution failed: {str(e)}"}, '/v1/code/execute/python', 500
            
    except Exception as e:
        logger.error(f"Job {job_id}: Error executing Python code: {str(e)}")
        return {"error": str(e)}, '/v1/code/execute/python', 500
        
    finally:
        if 'temp_file' in locals():
            os.unlink(temp_file.name)