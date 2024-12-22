import logging
import os
import tempfile
from flask import Blueprint
from services.authentication import authenticate
from app_utils import validate_payload, queue_task_wrapper
from services.cloud_storage import upload_file
import json

v1_data_to_json_bp = Blueprint('v1_data_to_json', __name__)
logger = logging.getLogger(__name__)

@v1_data_to_json_bp.route('/v1/data/transform/json', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "data": {"type": ["object", "array", "string", "number", "boolean"]},
        "response_type": {"type": "string", "enum": ["direct", "cloud"]},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["data"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def transform_json(job_id, data):
    logger.info(f"Job {job_id}: Received JSON transformation request")
    
    try:
        input_data = data['data']
        response_type = data.get('response_type', 'direct')
        
        try:
            if isinstance(input_data, (dict, list, str, int, float, bool)):
                json_string = json.dumps(input_data)
                
                if response_type == "direct":
                    return {
                        'json': json_string,
                        'json_url': None,
                        'message': 'success'
                    }, '/v1/data/transform/json', 200
                    
                else:  # response_type == "cloud"
                    # Create file with job_id as filename
                    temp_path = os.path.join(tempfile.gettempdir(), f"{job_id}.json")
                    with open(temp_path, 'w') as temp_file:
                        temp_file.write(json_string)
                        
                    # Upload to cloud storage
                    cloud_url = upload_file(temp_path)
                    
                    # Clean up temporary file
                    os.remove(temp_path)
                        
                    return {
                        'json': None,
                        'json_url': cloud_url,
                        'message': 'success'
                    }, '/v1/data/transform/json', 200
                        
            else:
                return {
                    'error': f'Unsupported data type: {type(input_data).__name__}',
                }, '/v1/data/transform/json', 400
                
        except json.JSONDecodeError as e:
            return {
                'error': f'Invalid JSON structure: {str(e)}',
            }, '/v1/data/transform/json', 400
            
    except Exception as e:
        logger.error(f"Job {job_id}: Error transforming data to JSON: {str(e)}")
        return {
            'error': f'Internal server error: {str(e)}'
        }, '/v1/data/transform/json', 500