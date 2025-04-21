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

def cut_media(video_url, cuts, job_id=None, video_codec='libx264', video_preset='medium', 
           video_crf=23, audio_codec='aac', audio_bitrate='128k'):
    """
    Cuts specified segments from a video file with customizable encoding settings.
    
    Args:
        video_url (str): URL of the video file to cut
        cuts (list): List of dictionaries with 'start' and 'end' timestamps
        job_id (str, optional): Unique job identifier
        video_codec (str, optional): Video codec to use for encoding (default: 'libx264')
        video_preset (str, optional): Encoding preset for speed/quality tradeoff (default: 'medium')
        video_crf (int, optional): Constant Rate Factor for quality (0-51, default: 23)
        audio_codec (str, optional): Audio codec to use for encoding (default: 'aac')
        audio_bitrate (str, optional): Audio bitrate (default: '128k')
        
    Returns:
        str: Path to the processed local file
    """
    logger.info(f"Starting video cut operation for {video_url}")
    input_filename = download_file(video_url, os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_input"))
    logger.info(f"Downloaded video to local file: {input_filename}")
    
    try:
        # Get the file extension
        _, ext = os.path.splitext(input_filename)
        
        # Create output filename
        output_filename = os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_output{ext}")
        
        # Using a single FFmpeg command with filter_complex to remove segments
        # This is much more efficient and reliable than concatenating segments
        
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
        
        # Validate and process cuts
        cuts_in_seconds = []
        for cut in cuts:
            start_seconds = time_to_seconds(cut['start'])
            end_seconds = time_to_seconds(cut['end'])
            
            # Validate cut times
            if start_seconds >= end_seconds:
                raise ValueError(f"Invalid cut: start time ({cut['start']}) must be before end time ({cut['end']})")
            
            if start_seconds < 0:
                logger.warning(f"Cut start time {cut['start']} is negative, using 0 instead")
                start_seconds = 0
                
            if end_seconds > file_duration:
                logger.warning(f"Cut end time {cut['end']} exceeds file duration, using file duration instead")
                end_seconds = file_duration
                
            # Only add valid cuts
            if start_seconds < end_seconds:
                cuts_in_seconds.append((start_seconds, end_seconds))
        
        # Sort cuts by start time and merge overlapping segments
        cuts_in_seconds.sort()
        merged_cuts = []
        
        if cuts_in_seconds:
            current_start, current_end = cuts_in_seconds[0]
            for start, end in cuts_in_seconds[1:]:
                if start <= current_end:  # Overlapping segments
                    current_end = max(current_end, end)
                else:  # Non-overlapping, add the previous merged segment
                    merged_cuts.append((current_start, current_end))
                    current_start, current_end = start, end
            # Add the last segment
            merged_cuts.append((current_start, current_end))
        
        logger.info(f"Merged cuts (segments to remove): {merged_cuts}")
        
        if not merged_cuts:
            logger.info("No valid cuts to apply, copying the original file")
            cmd = [
                'ffmpeg',
                '-i', input_filename,
                '-c', 'copy',
                output_filename
            ]
        else:
            # Build a select filter that excludes the segments we want to cut
            # Format: not(between(t,start1,end1)+between(t,start2,end2)+...)
            select_conditions = []
            for start, end in merged_cuts:
                select_conditions.append(f"between(t,{start},{end})")
            
            select_expr = "not(" + "+".join(select_conditions) + ")"
            logger.info(f"Using select expression: {select_expr}")
            
            # Create the single FFmpeg command with filter_complex and specified encoding settings
            cmd = [
                'ffmpeg',
                '-i', input_filename,
                '-filter_complex',
                f"[0:v]select='{select_expr}',setpts=N/FRAME_RATE/TB[v];[0:a]aselect='{select_expr}',asetpts=N/SR/TB[a]",
                '-map', '[v]',
                '-map', '[a]',
                '-c:v', video_codec,
                '-preset', video_preset,
                '-crf', str(video_crf),
                '-c:a', audio_codec,
                '-b:a', audio_bitrate,
                output_filename
            ]
        
        logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
        
        # Run the FFmpeg command
        subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
        
        # Return the path to the output file (route will handle upload)
        return output_filename, input_filename
        
    except Exception as e:
        logger.error(f"Video cut operation failed: {str(e)}")
        # Clean up all temporary files if they exist
        if 'input_filename' in locals() and os.path.exists(input_filename):
            os.remove(input_filename)
                    
        if 'output_filename' in locals() and os.path.exists(output_filename):
            os.remove(output_filename)
            
        raise