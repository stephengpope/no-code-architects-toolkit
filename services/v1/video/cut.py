import os
import ffmpeg
import logging
from services.file_management import download_file
from config import LOCAL_STORAGE_PATH
from datetime import datetime

logger = logging.getLogger(__name__)

def calculate_duration(start_time, end_time):
    """
    Calculate duration in seconds between two timestamps in HH:MM:SS format.
    
    Args:
        start_time (str): Start time in HH:MM:SS format
        end_time (str): End time in HH:MM:SS format
        
    Returns:
        float: Duration in seconds
    """
    start = datetime.strptime(start_time, "%H:%M:%S")
    end = datetime.strptime(end_time, "%H:%M:%S")
    duration = (end - start).total_seconds()
    return duration

def process_video_cut(video_url, cuts, job_id):
    """
    Cut a video into multiple segments based on the provided timestamps.
    
    Args:
        video_url (str): URL of the video to cut
        cuts (list): List of dictionaries containing start and end timestamps
        job_id (str): Unique identifier for the job
        
    Returns:
        list: List of paths to the cut video segments
    """
    # Download the video from the provided URL
    video_path = download_file(video_url, os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_input"))
    
    output_files = []
    
    try:
        # Process each cut segment
        for i, cut in enumerate(cuts):
            start_time = cut['start']
            end_time = cut['end']
            
            # Calculate duration from start and end times
            duration = calculate_duration(start_time, end_time)
            
            # Set output path for this segment
            output_path = os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_segment_{i}.mp4")
            
            # Cut the video segment using ffmpeg
            (
                ffmpeg
                .input(video_path, ss=start_time)  # Start time
                .output(output_path, t=duration)  # Duration in seconds
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            # Verify the output file exists
            if not os.path.exists(output_path):
                raise FileNotFoundError(f"Output file {output_path} was not created")
                
            output_files.append(output_path)
        
        # Clean up the downloaded input video file
        os.remove(video_path)
        
        return output_files
        
    except Exception as e:
        logger.error(f"Video cutting failed: {str(e)}")
        # Clean up any downloaded files on error
        if os.path.exists(video_path):
            os.remove(video_path)
        # Clean up any created output files
        for output_file in output_files:
            if os.path.exists(output_file):
                os.remove(output_file)
        raise 