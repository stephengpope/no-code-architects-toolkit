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
from app_utils import validate_payload, queue_task_wrapper
import logging
from services.v1.media.metadata import get_media_metadata
from services.authentication import authenticate

# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
v1_media_metadata_bp = Blueprint('v1_media_metadata', __name__)

@v1_media_metadata_bp.route('/v1/media/metadata', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "media_url": {"type": "string", "format": "uri"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["media_url"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=True)  # Set to execute immediately instead of queueing
def media_metadata(job_id, data):
    """
    Extract metadata from a media file, including video and audio properties.
    
    Expected input:
    {
        "media_url": "https://example.com/media.mp4",
        "webhook_url": "https://example.com/webhook" (optional),
        "id": "custom-id" (optional)
    }
    
    Returns metadata including filesize, duration, video/audio codec info, 
    resolution, frame rate, and bitrates.
    """
    media_url = data['media_url']
    logger.info(f"Job {job_id}: Received metadata request for {media_url}")
    
    try:
        # Extract metadata from the media file
        metadata = get_media_metadata(media_url, job_id)
        logger.info(f"Job {job_id}: Successfully extracted metadata")
        
        # Return the metadata directly
        return metadata, "/v1/media/metadata", 200
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Job {job_id}: Error extracting metadata - {error_message}")
        return error_message, "/v1/media/metadata", 500