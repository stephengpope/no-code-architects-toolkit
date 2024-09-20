import os
import ffmpeg
from services.file_management import download_file

# Set the default local storage directory
STORAGE_PATH = "/tmp/"

def process_audio_mixing(video_url, audio_url, video_vol, audio_vol, output_length, job_id, webhook_url=None):
    video_path = download_file(video_url, STORAGE_PATH)
    audio_path = download_file(audio_url, STORAGE_PATH)
    output_path = os.path.join(STORAGE_PATH, f"{job_id}.mp4")

    # Get video and audio information
    video_info = ffmpeg.probe(video_path)
    audio_info = ffmpeg.probe(audio_path)
    video_duration = float(video_info['streams'][0]['duration'])
    audio_duration = float(audio_info['streams'][0]['duration'])

    # Check if video has audio
    video_has_audio = any(stream['codec_type'] == 'audio' for stream in video_info['streams'])

    # Prepare FFmpeg inputs
    video = ffmpeg.input(video_path)
    audio = ffmpeg.input(audio_path)

    # Apply volume filter to input audio
    input_audio = audio.filter('volume', volume=f"{audio_vol/100}")

    # Determine output duration
    output_duration = video_duration if output_length == 'video' else audio_duration

    # Trim or pad audio
    if output_duration > audio_duration:
        input_audio = ffmpeg.filter([input_audio], 'apad', pad_dur=output_duration-audio_duration)
    else:
        input_audio = input_audio.filter('atrim', duration=output_duration)

    # Handle audio mixing based on whether video has audio
    if video_has_audio:
        video_audio = video.audio.filter('volume', volume=f"{video_vol/100}")
        mixed_audio = ffmpeg.filter([video_audio, input_audio], 'amix', inputs=2)
    else:
        mixed_audio = input_audio

    # Trim video if necessary
    if output_duration < video_duration:
        video = video.trim(duration=output_duration)

    # Set up output
    output = ffmpeg.output(
        video.video,  # Copy video stream
        mixed_audio,
        output_path,
        vcodec='copy',  # Copy video codec
        acodec='aac',   # Re-encode audio to AAC
        strict='experimental'
    )

    # If padding is needed, we can't use stream copy
    if output_duration > video_duration:
        output = ffmpeg.output(
            ffmpeg.filter([video], 'tpad', stop_duration=output_duration-video_duration),
            mixed_audio,
            output_path,
            acodec='aac',
            strict='experimental'
        )

    # Run FFmpeg command
    ffmpeg.run(output, overwrite_output=True)

    # Clean up input files
    os.remove(video_path)
    os.remove(audio_path)

    return output_path