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
import re
from services.file_management import download_file
from config import LOCAL_STORAGE_PATH

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def detect_silence(media_url, start_time=None, end_time=None, noise_threshold="-30dB", min_duration=0.5, mono=False, job_id=None):
    """
    Detect silence in media files using FFmpeg's silencedetect filter.
    
    Args:
        media_url (str): URL of the media file to analyze
        start_time (str, optional): Start time in format HH:MM:SS.mmm
        end_time (str, optional): End time in format HH:MM:SS.mmm
        noise_threshold (str, optional): Noise tolerance threshold, default "-30dB"
        min_duration (float, optional): Minimum silence duration to detect in seconds
        mono (bool, optional): Whether to convert stereo to mono before analysis
        job_id (str, optional): Unique job identifier
        
    Returns:
        list: List of dictionaries containing silence intervals with start, end, and duration
    """
    logger.info(f"Starting silence detection for media URL: {media_url}")
    input_filename = download_file(media_url, os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_input"))
    logger.info(f"Downloaded media to local file: {input_filename}")
    
    try:
        # For reliable silence detection with time constraints, we need a different approach
        # We'll use FFmpeg without any time constraints and process the results later
        cmd = ['ffmpeg', '-i', input_filename]
        
        # We won't use audio trim filters as they're causing issues with silence detection
        # Instead, we'll filter the results after the analysis is complete
        segment_filter = ""
        
        # Save the start and end times for post-processing
        start_seconds = 0
        end_seconds = float('inf')
        
        if start_time:
            try:
                # Parse the start time to seconds
                h, m, s = start_time.split(':')
                start_seconds = int(h) * 3600 + int(m) * 60 + float(s)
                logger.info(f"Will filter results starting from {start_seconds} seconds")
            except ValueError:
                logger.warning(f"Could not parse start time '{start_time}', using 0")
                
        if end_time:
            try:
                # Parse the end time to seconds
                h, m, s = end_time.split(':')
                end_seconds = int(h) * 3600 + int(m) * 60 + float(s)
                logger.info(f"Will filter results ending at {end_seconds} seconds")
            except ValueError:
                logger.warning(f"Could not parse end time '{end_time}', using infinity")
            
        # Add audio processing options
        cmd.extend(['-af'])
        
        # Build the filter string
        filter_string = ""
        
        # First add the segment filter if needed
        filter_string += segment_filter
        
        # Then add mono conversion if needed
        if mono:
            filter_string += "pan=mono|c0=0.5*c0+0.5*c1,"
            
        # Add the silencedetect filter
        filter_string += f"silencedetect=noise={noise_threshold}:d={min_duration}"
        cmd.append(filter_string)
        
        # Output to null, we only want the filter output
        cmd.extend(['-f', 'null', '-'])
        
        logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
        
        # Run the FFmpeg command and capture stderr for silence detection output
        result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
        
        # Parse the silence detection output
        silence_intervals = []
        
        # Regular expressions to match the silence detection output
        silence_start_pattern = r'silence_start: (\d+\.?\d*)'
        silence_end_pattern = r'silence_end: (\d+\.?\d*) \| silence_duration: (\d+\.?\d*)'
        
        # Find all silence start times
        silence_starts = re.findall(silence_start_pattern, result.stderr)
        
        # Find all silence end times and durations
        silence_ends_durations = re.findall(silence_end_pattern, result.stderr)
        
        # Combine the results into a list of silence intervals
        for i, (end, duration) in enumerate(silence_ends_durations):
            # For the first silence period, the start time might not be detected correctly
            # if the media starts with silence
            start = silence_starts[i] if i < len(silence_starts) else "0.0"
            
            # Convert to float 
            start_time_float = float(start) 
            end_time_float = float(end)
            duration_float = float(duration)
            
            # Filter the results based on the specified time range
            # Only include silence periods that overlap with our requested range
            
            # Skip if silence ends before our start time
            if end_time_float < start_seconds:
                logger.info(f"Skipping silence at {start_time_float}-{end_time_float} as it ends before requested start time {start_seconds}")
                continue
                
            # Skip if silence starts after our end time
            if start_time_float > end_seconds:
                logger.info(f"Skipping silence at {start_time_float}-{end_time_float} as it starts after requested end time {end_seconds}")
                continue
                
            # Format time as HH:MM:SS.mmm
            start_formatted = format_time(start_time_float)
            end_formatted = format_time(end_time_float)
            
            silence_intervals.append({
                "start": start_formatted,
                "end": end_formatted,
                "duration": round(duration_float, 2)
            })
        
        # Clean up the downloaded file
        os.remove(input_filename)
        logger.info(f"Removed local file: {input_filename}")
        
        return silence_intervals
        
    except Exception as e:
        logger.error(f"Silence detection failed: {str(e)}")
        # Make sure to clean up even on error
        if os.path.exists(input_filename):
            os.remove(input_filename)
        raise

def format_time(seconds):
    """
    Format time in seconds to HH:MM:SS.mmm format
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"