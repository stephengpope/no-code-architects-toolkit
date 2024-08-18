import os
import uuid
import ffmpeg
from services.webhook import send_webhook
from services.file_management import download_file, STORAGE_PATH

def process_conversion(media_url, webhook_url):
    try:
        # Generate a unique job ID using UUID
        job_id = str(uuid.uuid4())
        output_filename = f"{job_id}.mp3"
        input_filename = download_file(media_url, os.path.join(STORAGE_PATH, f"{job_id}_input"))

        (
            ffmpeg
            .input(input_filename)
            .output(os.path.join(STORAGE_PATH, output_filename), acodec='libmp3lame', audio_bitrate='64k')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )

        os.remove(input_filename)  # Clean up the input file after conversion

        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/convert-media-to-mp3",
                "job_id": job_id,
                "response": output_filename,
                "code": 200,
                "message": "success"
            })

        return job_id  # Return the generated job ID
    except Exception as e:
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/convert-media-to-mp3",
                "job_id": None,
                "response": None,
                "code": 500,
                "message": str(e)
            })
        raise

def process_video_combination(media_urls, webhook_url):
    try:
        job_id = str(uuid.uuid4())
        output_filename = f"{job_id}_combined.mp4"
        input_files = []

        for i, url in enumerate(media_urls):
            input_filename = download_file(url, os.path.join(STORAGE_PATH, f"{job_id}_input_{i}"))
            input_files.append(input_filename)

        # Create a list of input files for ffmpeg
        inputs = [ffmpeg.input(f) for f in input_files]

        # Concatenate the input videos
        concat = ffmpeg.concat(*inputs, v=1, a=1).node

        # Output the result, re-encoding the video
        output = ffmpeg.output(concat[0], concat[1], os.path.join(STORAGE_PATH, output_filename),
            vcodec='libx264',  # Use H.264 codec
            acodec='aac',      # Use AAC for audio
            video_bitrate='3000k',  # Adjust as needed
            audio_bitrate='192k')   # Adjust as needed

        # Run the ffmpeg command
        ffmpeg.run(output, overwrite_output=True)

        # Clean up input files
        for f in input_files:
            os.remove(f)

        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/combine-videos",
                "job_id": job_id,
                "response": output_filename,
                "code": 200,
                "message": "success"
            })

        return job_id  # Return the generated job ID
    except Exception as e:
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/combine-videos",
                "job_id": None,
                "response": None,
                "code": 500,
                "message": str(e)
            })
        raise

def process_audio_mixing(video_url, audio_url, video_vol, audio_vol, output_length, webhook_url):
    try:
        job_id = str(uuid.uuid4())
        output_filename = f"{job_id}_mixed.mp4"
        video_input = os.path.join(STORAGE_PATH, f"{job_id}_video_input")
        audio_input = os.path.join(STORAGE_PATH, f"{job_id}_audio_input")

        # Download files
        download_file(video_url, video_input)
        download_file(audio_url, audio_input)

        # Prepare FFmpeg inputs
        video = ffmpeg.input(video_input)
        audio = ffmpeg.input(audio_input)

        # Apply volume filters
        video_audio = video.audio.filter('volume', volume=f"{video_vol/100}")
        input_audio = audio.filter('volume', volume=f"{audio_vol/100}")

        # Get video and audio durations
        video_info = ffmpeg.probe(video_input)
        audio_info = ffmpeg.probe(audio_input)
        video_duration = float(video_info['streams'][0]['duration'])
        audio_duration = float(audio_info['streams'][0]['duration'])

        # Determine output duration
        if output_length == 'video':
            output_duration = video_duration
        else:
            output_duration = audio_duration

        # Trim or pad audio
        if output_duration > audio_duration:
            input_audio = ffmpeg.filter([input_audio], 'apad', pad_dur=output_duration-audio_duration)
        else:
            input_audio = input_audio.filter('atrim', duration=output_duration)

        # Mix audio
        mixed_audio = ffmpeg.filter([video_audio, input_audio], 'amix', inputs=2)

        # Trim or pad video
        if output_duration > video_duration:
            video = ffmpeg.filter([video], 'tpad', stop_duration=output_duration-video_duration)
        else:
            video = video.trim(duration=output_duration)

        # Combine video and mixed audio
        output = ffmpeg.output(video, mixed_audio, os.path.join(STORAGE_PATH, output_filename),
            vcodec='libx264', acodec='aac', strict='experimental')

        # Run FFmpeg command
        ffmpeg.run(output, overwrite_output=True)

        # Clean up input files
        os.remove(video_input)
        os.remove(audio_input)

        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/audio-mixing",
                "job_id": job_id,
                "response": output_filename,
                "code": 200,
                "message": "success"
            })

        return job_id  # Return the generated job ID
    except Exception as e:
        if webhook_url:
            send_webhook(webhook_url, {
                "endpoint": "/audio-mixing",
                "job_id": None,
                "response": None,
                "code": 500,
                "message": str(e)
            })
        raise
