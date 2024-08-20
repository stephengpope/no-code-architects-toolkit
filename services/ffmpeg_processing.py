import os
import ffmpeg
from services.file_management import download_file, STORAGE_PATH

def process_conversion(media_url, job_id):
    """Convert media to MP3 format."""
    input_filename = download_file(media_url, os.path.join(STORAGE_PATH, f"{job_id}_input"))
    output_filename = f"{job_id}.mp3"

    try:
        (
            ffmpeg
            .input(input_filename)
            .output(os.path.join(STORAGE_PATH, output_filename), acodec='libmp3lame', audio_bitrate='64k')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        os.remove(input_filename)
        print(f"Conversion successful: {output_filename}")
        return output_filename
    except ffmpeg.Error as e:
        print(f"Conversion failed: {str(e)}")
        raise

def process_video_combination(media_urls, job_id):
    """Combine multiple videos into one."""
    input_files = []
    for i, url in enumerate(media_urls):
        input_filename = download_file(url, os.path.join(STORAGE_PATH, f"{job_id}_input_{i}"))
        input_files.append(input_filename)

    output_filename = f"{job_id}_combined.mp4"

    try:
        inputs = [ffmpeg.input(f) for f in input_files]
        concat = ffmpeg.concat(*inputs)
        output = ffmpeg.output(concat, os.path.join(STORAGE_PATH, output_filename),
            vcodec='libx264', acodec='aac',
            video_bitrate='3000k', audio_bitrate='192k')

        ffmpeg.run(output, overwrite_output=True)
        for f in input_files:
            os.remove(f)
        print(f"Video combination successful: {output_filename}")
        return output_filename
    except ffmpeg.Error as e:
        print(f"Video combination failed: {str(e)}")
        raise

def process_audio_mixing(video_url, audio_url, video_vol, audio_vol, output_length, job_id):
    """Mix audio with video."""
    video_input = os.path.join(STORAGE_PATH, f"{job_id}_video_input")
    audio_input = os.path.join(STORAGE_PATH, f"{job_id}_audio_input")

    download_file(video_url, video_input)
    download_file(audio_url, audio_input)

    output_filename = f"{job_id}_mixed.mp4"

    try:
        video = ffmpeg.input(video_input)
        audio = ffmpeg.input(audio_input)

        video_audio = video.audio.filter('volume', volume=f"{video_vol/100}")
        input_audio = audio.filter('volume', volume=f"{audio_vol/100}")

        video_info = ffmpeg.probe(video_input)
        audio_info = ffmpeg.probe(audio_input)
        video_duration = float(video_info['streams'][0]['duration'])
        audio_duration = float(audio_info['streams'][0]['duration'])

        if output_length == 'video':
            output_duration = video_duration
        else:
            output_duration = audio_duration

        if output_duration > audio_duration:
            input_audio = ffmpeg.filter([input_audio], 'apad', pad_dur=output_duration-audio_duration)
        else:
            input_audio = input_audio.filter('atrim', duration=output_duration)

        mixed_audio = ffmpeg.filter([video_audio, input_audio], 'amix', inputs=2)

        if output_duration > video_duration:
            video = ffmpeg.filter([video], 'tpad', stop_duration=output_duration-video_duration)
        else:
            video = video.trim(duration=output_duration)

        output = ffmpeg.output(video, mixed_audio, os.path.join(STORAGE_PATH, output_filename),
            vcodec='libx264', acodec='aac', strict='experimental')

        ffmpeg.run(output, overwrite_output=True)

        os.remove(video_input)
        os.remove(audio_input)
        print(f"Audio mixing successful: {output_filename}")
        return output_filename
    except ffmpeg.Error as e:
        print(f"Audio mixing failed: {str(e)}")
        raise
