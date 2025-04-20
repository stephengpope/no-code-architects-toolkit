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



from flask import Blueprint
from app_utils import *
import logging
from services.v1.media.silence import detect_silence
from services.authentication import authenticate

v1_media_silence_bp = Blueprint('v1_media_silence', __name__)
logger = logging.getLogger(__name__)

@v1_media_silence_bp.route('/v1/media/silence', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "media_url": {"type": "string", "format": "uri"},
        "start": {"type": "string"},
        "end": {"type": "string"},
        "noise": {"type": "string"},
        "duration": {"type": "number", "minimum": 0.1},
        "mono": {"type": "boolean"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["media_url", "duration"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def silence(job_id, data):
    """Detect silence in a media file and return the silence intervals."""
    media_url = data['media_url']
    start_time = data.get('start', None)  # None = start from beginning
    end_time = data.get('end', None)  # None = process until end
    noise_threshold = data.get('noise', '-30dB')
    min_duration = data['duration']  # Required parameter
    mono = data.get('mono', True)  # Default to True
    
    logger.info(f"Job {job_id}: Received silence detection request for {media_url}")
    
    try:
        silence_intervals = detect_silence(
            media_url=media_url,
            start_time=start_time,
            end_time=end_time,
            noise_threshold=noise_threshold,
            min_duration=min_duration,
            mono=mono,
            job_id=job_id
        )
        
        logger.info(f"Job {job_id}: Silence detection completed successfully")
        return silence_intervals, "/v1/media/silence", 200
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error during silence detection process - {str(e)}")
        return str(e), "/v1/media/silence", 500