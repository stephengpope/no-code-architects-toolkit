import logging
import os
import tempfile
from flask import Blueprint
from services.authentication import authenticate
from app_utils import validate_payload, queue_task_wrapper
from services.cloud_storage import upload_file
import json

v1_transform_chunk_bp = Blueprint('v1_transform_chunk', __name__)
logger = logging.getLogger(__name__)

def chunk_text(text, max_tokens=500, percent=0, direction="left"):
    """
    Chunk text with configurable overlap.
    
    Args:
        text (str): Input text to chunk
        max_tokens (int): Maximum number of tokens (words) per chunk
        percent (float): Percentage of overlap between chunks (0-100)
        direction (str): Direction of overlap - "left" or "both"
                        "left" - each chunk overlaps only with previous chunk
                        "both" - each chunk overlaps with both previous and next chunks
    
    Returns:
        list: List of text chunks
    """
    words = text.split()
    if not words:
        return []
        
    # Calculate overlap size in tokens
    overlap_size = int(max_tokens * (percent / 100))
    
    # Validate parameters
    if overlap_size >= max_tokens:
        raise ValueError("Overlap size cannot be greater than or equal to chunk size")
    
    # Calculate core chunk size (without overlaps)
    core_size = max_tokens - overlap_size
    
    # Precompute chunk boundaries
    if direction == "left":
        # Calculate positions for sequential overlap
        positions = []
        current_pos = 0
        
        while current_pos < len(words):
            positions.append({
                'start': current_pos,
                'end': min(current_pos + max_tokens, len(words))
            })
            current_pos += core_size
            
    else:  # "both"
        # Calculate positions for bidirectional overlap
        positions = []
        current_pos = 0
        
        while current_pos < len(words):
            if current_pos == 0:  # First chunk
                start_pos, end_pos = 0, min(max_tokens, len(words))
            elif current_pos + core_size >= len(words):  # Last chunk
                start_pos, end_pos = max(0, len(words) - max_tokens), len(words)
            else:  # Middle chunks
                start_pos = current_pos - overlap_size
                end_pos = min(start_pos + max_tokens, len(words))
            
            positions.append({
                'start': start_pos,
                'end': end_pos
            })
            current_pos += core_size
    
    # Generate chunks using precomputed positions
    chunks = [
        " ".join(words[pos['start']:pos['end']])
        for pos in positions
    ]
    
    return chunks

@v1_transform_chunk_bp.route('/v1/string/transform/chunks', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "max_tokens": {"type": "integer", "minimum": 1, "maximum": 10000},
        "percent": {"type": "number", "minimum": 0, "maximum": 100},
        "direction": {"type": "string", "enum": ["left", "both"]},
        "response_type": {"type": "string", "enum": ["direct", "cloud"]},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["text"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def transform_chunk(job_id, data):
    """
    API endpoint to chunk text with configurable overlap parameters.
    """
    logger.info(f"Job {job_id}: Received text chunking request")
    
    try:
        # Extract parameters with defaults
        text = data['text']
        max_tokens = data.get('max_tokens', 500)
        percent = data.get('percent', 10)
        direction = data.get('direction', 'left')
        response_type = data.get('response_type', 'direct')
        
        # Process the text
        chunks = chunk_text(
            text=text,
            max_tokens=max_tokens,
            percent=percent,
            direction=direction
        )
        
        if response_type == "direct":
            return {
                'chunks': chunks,
                'chunks_url': None,
                'count': len(chunks)
            }, '/v1/string/transform/chunks', 200
            
        else:  # response_type == "cloud"
            # Create temporary file with job_id as filename
            temp_path = os.path.join(tempfile.gettempdir(), f"{job_id}.json")
            with open(temp_path, 'w') as temp_file:
                json.dump(chunks, temp_file)
                
            # Upload to cloud storage
            cloud_url = upload_file(temp_path)
            
            # Clean up temporary file
            os.remove(temp_path)
            
            return {
                'chunks': None,
                'chunks_url': cloud_url,
                'count': len(chunks)
            }, '/v1/string/transform/chunks', 200
        
    except ValueError as e:
        logger.error(f"Job {job_id}: Validation error in chunking request: {str(e)}")
        return {"error": str(e)}, '/v1/string/transform/chunks', 400
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error processing chunking request: {str(e)}")
        return {"error": str(e)}, '/v1/string/transform/chunks', 500