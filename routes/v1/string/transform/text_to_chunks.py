import logging
import os
import tempfile
from flask import Blueprint
from services.authentication import authenticate
from app_utils import validate_payload, queue_task_wrapper
from services.cloud_storage import upload_file
import json
import re

v1_transform_chunk_bp = Blueprint('v1_transform_chunk', __name__)
logger = logging.getLogger(__name__)

def sequential_chunk(text, max_tokens, overlap, overlap_type, direction):
    """Sequential chunking with configurable overlap"""
    words = text.split()
    if not words:
        raise ValueError("Input text is empty or contains only whitespace")
        
    # Calculate overlap size in tokens
    if overlap_type == "percent":
        if not 0 <= overlap <= 100:
            raise ValueError("Percentage overlap must be between 0 and 100")
        overlap_size = int(max_tokens * (overlap / 100))
    else:  # "token"
        if not 0 <= overlap < max_tokens:
            raise ValueError("Token overlap must be less than max_tokens")
        overlap_size = int(overlap)
    
    if overlap_size >= max_tokens:
        raise ValueError("Overlap size cannot be greater than or equal to chunk size")
    
    core_size = max_tokens - overlap_size
    positions = []
    current_pos = 0
    
    if direction == "left":
        while current_pos < len(words):
            positions.append({
                'start': current_pos,
                'end': min(current_pos + max_tokens, len(words))
            })
            current_pos += core_size
    else:  # "both"
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
    
    return [" ".join(words[pos['start']:pos['end']]) for pos in positions]

def recursive_chunk(text, max_tokens, overlap, overlap_type):
    """Recursive chunking based on document structure"""
    
    def calculate_overlap_size(section_size):
        if overlap_type == "percent":
            return int(min(section_size, max_tokens) * (overlap / 100))
        return min(int(overlap), min(section_size, max_tokens))
    
    def split_section(section):
        words = section.split()
        section_size = len(words)
        
        # If section fits in one chunk, return it
        if section_size <= max_tokens:
            return [section]
            
        # Calculate overlap for this section
        overlap_size = calculate_overlap_size(section_size)
        core_size = max_tokens - overlap_size
        
        # Split into chunks with overlap
        chunks = []
        current_pos = 0
        
        while current_pos < section_size:
            end_pos = min(current_pos + max_tokens, section_size)
            chunks.append(" ".join(words[current_pos:end_pos]))
            current_pos += core_size
            
        return chunks
    
    # First split by double newlines to get major sections
    sections = [s.strip() for s in re.split(r'\n\s*\n', text) if s.strip()]
    if not sections:
        raise ValueError("Input text is empty or contains only whitespace")
    
    # Process each section recursively
    chunks = []
    for section in sections:
        # Only split sections that exceed max_tokens
        if len(section.split()) > max_tokens:
            chunks.extend(split_section(section))
        else:
            chunks.append(section)
    
    return chunks

def chunk_text(text, max_tokens=500, overlap=0, overlap_type="token", direction="both", strategy="sequential"):
    """
    Chunk text with configurable strategy and overlap.
    
    Args:
        text (str): Input text to chunk
        max_tokens (int): Maximum number of tokens (words) per chunk
        overlap (float or int): Amount of overlap between chunks
        overlap_type (str): Type of overlap - "percent" or "token"
        direction (str): Direction of overlap for sequential strategy - "left" or "both"
        strategy (str): Chunking strategy - "sequential" or "recursive"
    
    Returns:
        list: List of text chunks
    """
    if strategy == "sequential":
        return sequential_chunk(text, max_tokens, overlap, overlap_type, direction)
    else:  # "recursive"
        return recursive_chunk(text, max_tokens, overlap, overlap_type)

@v1_transform_chunk_bp.route('/v1/string/transform/chunks', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "max_tokens": {"type": "integer", "minimum": 1, "maximum": 10000},
        "overlap": {"type": "number", "minimum": 0},
        "overlap_type": {"type": "string", "enum": ["percent", "token"]},
        "direction": {"type": "string", "enum": ["left", "both"]},
        "strategy": {"type": "string", "enum": ["sequential", "recursive"]},
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
    API endpoint to chunk text with configurable parameters.
    """
    logger.info(f"Job {job_id}: Received text chunking request")
    
    try:
        # Extract parameters with defaults
        text = data['text']
        max_tokens = data.get('max_tokens', 500)
        overlap = data.get('overlap', 0)
        overlap_type = data.get('overlap_type', 'token')
        direction = data.get('direction', 'both')
        strategy = data.get('strategy', 'sequential')
        response_type = data.get('response_type', 'direct')
        
        # Process the text
        chunks = chunk_text(
            text=text,
            max_tokens=max_tokens,
            overlap=overlap,
            overlap_type=overlap_type,
            direction=direction,
            strategy=strategy
        )
        
        if response_type == "direct":
            return {
                'chunks': chunks,
                'chunks_url': None,
                'count': len(chunks)
            }, '/v1/string/transform/chunks', 200
            
        else:  # response_type == "cloud"
            temp_path = os.path.join(tempfile.gettempdir(), f"{job_id}.json")
            with open(temp_path, 'w') as temp_file:
                json.dump(chunks, temp_file)
                
            cloud_url = upload_file(temp_path)
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