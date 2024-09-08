import os
import ffmpeg
from services.file_management import download_file, STORAGE_PATH
from services.gdrive_service import upload_to_gcs, GCP_BUCKET_NAME

def process_audio_mixing(video_url, audio_url, video_vol, audio_vol, output_length, job_id, webhook_url=None):
    video_path = download_file(video_url, STORAGE_PATH)
    audio_path = download_file(audio_url, STORAGE_PATH)
    output_path = os.path.join(STORAGE_PATH, f"{job_id}.mp4")

    # Apply volume filters and mix audio
    video = ffmpeg.input(video_path)
    audio = ffmpeg.input(audio_path)
    video_audio = video.audio.filter('volume', volume=video_vol / 100.0)
    input_audio = audio.filter('volume', volume=audio_vol / 100.0)
    mixed_audio = ffmpeg.filter([video_audio, input_audio], 'amix', duration='longest')

    if output_length == 'audio':
        output = ffmpeg.output(video.video, mixed_audio, output_path, shortest=None)
    else:
        output = ffmpeg.output(video.video, mixed_audio, output_path, shortest=None)

    ffmpeg.run(output)
    return output_path