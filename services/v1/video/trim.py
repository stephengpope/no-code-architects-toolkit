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
import json
import subprocess
import logging
import uuid
from services.file_management import download_file
from services.cloud_storage import upload_file
from config import LOCAL_STORAGE_PATH

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def time_to_seconds(time_str):
    """
    Convert a time string in format HH:MM:SS[.mmm] to seconds.
    
    Args:
        time_str (str): Time string
        
    Returns:
        float: Time in seconds
    """
    if not time_str:
        return None
        
    try:
        parts = time_str.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        elif len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + float(seconds)
        else:
            return float(time_str)
    except ValueError:
        raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM:SS[.mmm]")

def trim_video(video_url, start=None, end=None, job_id=None, video_codec='libx264', video_preset='medium', 
               video_crf=23, audio_codec='aac', audio_bitrate='128k'):
    """
    Trims a video by removing specified portions from the beginning and/or end with customizable encoding settings.
    
    Args:
        video_url (str): URL of the video file to trim
        start (str, optional): Timestamp to start the trimmed video (keep everything after this point)
        end (str, optional): Timestamp to end the trimmed video (keep everything before this point)
        job_id (str, optional): Unique job identifier
        video_codec (str, optional): Video codec to use for encoding (default: 'libx264')
        video_preset (str, optional): Encoding preset for speed/quality tradeoff (default: 'medium')
        video_crf (int, optional): Constant Rate Factor for quality (0-51, default: 23)
        audio_codec (str, optional): Audio codec to use for encoding (default: 'aac')
        audio_bitrate (str, optional): Audio bitrate (default: '128k')
        
    Returns:
        tuple: (output_filename, input_filename)
    """
    logger.info(f"Starting video trim operation for {video_url}")
    if not job_id:
        job_id = str(uuid.uuid4())
        
    input_filename = download_file(video_url, os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_input"))
    logger.info(f"Downloaded video to local file: {input_filename}")
    
    try:
        # Get the file extension
        _, ext = os.path.splitext(input_filename)
        
        # Create output filename
        output_filename = os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_output{ext}")
        
        # Get the duration of the input file
        probe_cmd = [
            'ffprobe', 
            '-v', 'error', 
            '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_filename
        ]
        duration_result = subprocess.run(probe_cmd, capture_output=True, text=True)
        
        try:
            file_duration = float(duration_result.stdout.strip())
            logger.info(f"File duration: {file_duration} seconds")
        except (ValueError, IndexError):
            logger.warning("Could not determine file duration, using a large value")
            file_duration = 86400  # 24 hours as a fallback
        
        # Convert start and end times to seconds
        start_seconds = time_to_seconds(start) if start else 0
        end_seconds = time_to_seconds(end) if end else file_duration
        
        # Validate times
        if start_seconds is not None and start_seconds < 0:
            logger.warning(f"Start time {start} is negative, using 0 instead")
            start_seconds = 0
            
        if end_seconds is not None and end_seconds > file_duration:
            logger.warning(f"End time {end} exceeds file duration, using file duration instead")
            end_seconds = file_duration
            
        if start_seconds is not None and end_seconds is not None and start_seconds >= end_seconds:
            raise ValueError(f"Invalid trim: start time ({start}) must be before end time ({end})")
        
        # Prepare FFmpeg command based on trim parameters
        cmd = ['ffmpeg', '-i', input_filename]
        
        filter_applied = False
        
        if start_seconds > 0 or end_seconds < file_duration:
            # We need to trim the video
            logger.info(f"Trimming video from {start_seconds}s to {end_seconds}s")
            
            if start_seconds > 0:
                cmd.extend(['-ss', str(start_seconds)])
                
            if end_seconds < file_duration:
                duration = end_seconds - (start_seconds or 0)
                cmd.extend(['-t', str(duration)])
                
            filter_applied = True
        
        # Add encoding parameters
        cmd.extend([
            '-c:v', video_codec,
            '-preset', video_preset,
            '-crf', str(video_crf),
            '-c:a', audio_codec,
            '-b:a', audio_bitrate,
            '-avoid_negative_ts', 'make_zero',
            output_filename
        ])
        
        if not filter_applied:
            logger.info("No trimming needed, copying with encoder settings")
        
        logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
        
        # Run the FFmpeg command
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode != 0:
            logger.error(f"Error during trim: {process.stderr}")
            raise Exception(f"FFmpeg error: {process.stderr}")
        
        # Return the path to the output file (route will handle upload)
        return output_filename, input_filename
        
    except Exception as e:
        logger.error(f"Video trim operation failed: {str(e)}")
        
        # Clean up all temporary files if they exist
        if 'input_filename' in locals() and os.path.exists(input_filename):
            os.remove(input_filename)
                
        if 'output_filename' in locals() and os.path.exists(output_filename):
            os.remove(output_filename)
            
        raise