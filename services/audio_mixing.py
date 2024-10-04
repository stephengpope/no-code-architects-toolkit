import os
import subprocess
from services.file_management import download_file

STORAGE_PATH = "/tmp/"

def get_duration(file_path):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(result.stdout)

def process_audio_mixing(video_url, audio_url, video_vol, audio_vol, output_length, job_id, webhook_url=None):
    video_path = download_file(video_url, STORAGE_PATH)
    audio_path = download_file(audio_url, STORAGE_PATH)
    output_path = os.path.join(STORAGE_PATH, f"{job_id}.mp4")

    video_duration = get_duration(video_path)
    audio_duration = get_duration(audio_path)

    # Explicitly set output duration based on output_length
    output_duration = video_duration if output_length == 'video' else audio_duration

    # Prepare FFmpeg command
    cmd = ['ffmpeg', '-y']

    # Input video
    cmd.extend(['-i', video_path])

    # Input audio
    cmd.extend(['-i', audio_path])

    # Video settings
    if output_length == 'audio' and audio_duration > video_duration:
        cmd.extend(['-stream_loop', '-1'])  # Loop video only if output_length is 'audio' and audio is longer

    # Audio settings
    audio_filter = f'[1:a]volume={audio_vol/100}'
    if output_length == 'video':
        audio_filter += f',atrim=duration={video_duration}'
    audio_filter += '[a]'
    cmd.extend(['-filter_complex', audio_filter])

    # Output settings
    cmd.extend(['-map', '0:v'])  # Map video from first input
    cmd.extend(['-map', '[a]'])  # Map processed audio

    if output_length == 'audio' and audio_duration > video_duration:
        cmd.extend(['-c:v', 'libx264'])  # Re-encode video if looping
    else:
        cmd.extend(['-c:v', 'copy'])  # Copy video codec otherwise

    cmd.extend(['-c:a', 'aac'])  # Always encode audio to AAC
    
    # Explicitly set output duration
    cmd.extend(['-t', str(output_duration)])

    cmd.append(output_path)

    # Run FFmpeg command
    subprocess.run(cmd, check=True)

    # Clean up input files
    os.remove(video_path)
    os.remove(audio_path)

    return output_path