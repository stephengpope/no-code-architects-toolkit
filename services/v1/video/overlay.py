import os
import subprocess
import json
from services.file_management import download_file
from config import LOCAL_STORAGE_PATH

def process_video_overlay(video_url, overlay_video_url, start_time, job_id, webhook_url=None):
    """
    Overlay one video on top of another at the specified start time.
    
    Args:
        video_url (str): URL of the base video
        overlay_video_url (str): URL of the video to overlay
        start_time (float): Time in seconds to start the overlay
        job_id (str): Unique job identifier
        webhook_url (str, optional): URL to send job completion notification
        
    Returns:
        str: Path to the output file
    """
    try:
        # Download both videos
        base_video_path = download_file(video_url, os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_base"))
        overlay_video_path = download_file(overlay_video_url, os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_overlay"))
        
        # Output file path
        output_filename = f"{job_id}_output.mp4"
        output_path = os.path.join(LOCAL_STORAGE_PATH, output_filename)
        
        # Get overlay video duration using ffprobe
        probe_cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            overlay_video_path
        ]
        
        probe_result = subprocess.run(
            probe_cmd,
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )
        
        # Parse the JSON output to get duration
        probe_data = json.loads(probe_result.stdout)
        overlay_duration = float(probe_data['format']['duration'])
        
        # Calculate end time
        end_time = start_time + overlay_duration
        
        # Construct and run the ffmpeg command using subprocess
        # Show the overlay starting at start_time and ending when the overlay video completes
        filter_complex = f"[0:v][1:v]overlay=0:0:enable='between(t,{start_time},{end_time})'"
        
        cmd = [
            'ffmpeg',
            '-i', base_video_path,
            '-i', overlay_video_path,
            '-filter_complex', filter_complex,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-map', '0:a',   # Use audio from the first input
            '-y',            # Overwrite output file if it exists
            output_path
        ]
        
        # Run the ffmpeg command
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        
        # Clean up input files
        os.remove(base_video_path)
        os.remove(overlay_video_path)
        
        print(f"Video overlay successful: {output_path}")
        
        # Check if the output file exists locally before upload
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file {output_path} does not exist after overlay.")
        
        return output_path
        
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg command failed: {e.stderr}")
        raise Exception(f"FFmpeg command failed: {e.stderr}")
    except Exception as e:
        print(f"Video overlay failed: {str(e)}")
        raise