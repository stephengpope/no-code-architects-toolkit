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



from flask import Flask, request
from queue import Queue
from services.webhook import send_webhook
import threading
import uuid
import os
import time
from version import BUILD_NUMBER  # Import the BUILD_NUMBER
from app_utils import log_job_status  # Import the log_job_status function

MAX_QUEUE_LENGTH = int(os.environ.get('MAX_QUEUE_LENGTH', 0))

def create_app():
    app = Flask(__name__)

    # Create a queue to hold tasks
    task_queue = Queue()
    queue_id = id(task_queue)  # Generate a single queue_id for this worker

    # Function to process tasks from the queue
    def process_queue():
        while True:
            job_id, data, task_func, queue_start_time = task_queue.get()
            queue_time = time.time() - queue_start_time
            run_start_time = time.time()
            pid = os.getpid()  # Get the PID of the actual processing thread
            
            # Log job status as running
            log_job_status(job_id, {
                "job_status": "running",
                "job_id": job_id,
                "queue_id": queue_id,
                "process_id": pid,
                "response": None
            })
            
            response = task_func()
            run_time = time.time() - run_start_time
            total_time = time.time() - queue_start_time

            response_data = {
                "endpoint": response[1],
                "code": response[2],
                "id": data.get("id"),
                "job_id": job_id,
                "response": response[0] if response[2] == 200 else None,
                "message": "success" if response[2] == 200 else response[0],
                "pid": pid,
                "queue_id": queue_id,
                "run_time": round(run_time, 3),
                "queue_time": round(queue_time, 3),
                "total_time": round(total_time, 3),
                "queue_length": task_queue.qsize(),
                "build_number": BUILD_NUMBER  # Add build number to response
            }
            
            # Log job status as done
            log_job_status(job_id, {
                "job_status": "done",
                "job_id": job_id,
                "queue_id": queue_id,
                "process_id": pid,
                "response": response_data
            })

            # Only send webhook if webhook_url has an actual value (not an empty string)
            if data.get("webhook_url") and data.get("webhook_url") != "":
                send_webhook(data.get("webhook_url"), response_data)

            task_queue.task_done()

    # Start the queue processing in a separate thread
    threading.Thread(target=process_queue, daemon=True).start()

    # Decorator to add tasks to the queue or bypass it
    def queue_task(bypass_queue=False):
        def decorator(f):
            def wrapper(*args, **kwargs):
                job_id = str(uuid.uuid4())
                data = request.json if request.is_json else {}
                pid = os.getpid()  # Get PID for non-queued tasks
                start_time = time.time()
                
                if bypass_queue or 'webhook_url' not in data:
                    
                    # Log job status as running immediately (bypassing queue)
                    log_job_status(job_id, {
                        "job_status": "running",
                        "job_id": job_id,
                        "queue_id": queue_id,
                        "process_id": pid,
                        "response": None
                    })
                    
                    response = f(job_id=job_id, data=data, *args, **kwargs)
                    run_time = time.time() - start_time
                    
                    response_obj = {
                        "code": response[2],
                        "id": data.get("id"),
                        "job_id": job_id,
                        "response": response[0] if response[2] == 200 else None,
                        "message": "success" if response[2] == 200 else response[0],
                        "run_time": round(run_time, 3),
                        "queue_time": 0,
                        "total_time": round(run_time, 3),
                        "pid": pid,
                        "queue_id": queue_id,
                        "queue_length": task_queue.qsize(),
                        "build_number": BUILD_NUMBER  # Add build number to response
                    }
                    
                    # Log job status as done
                    log_job_status(job_id, {
                        "job_status": "done",
                        "job_id": job_id,
                        "queue_id": queue_id,
                        "process_id": pid,
                        "response": response_obj
                    })
                    
                    return response_obj, response[2]
                else:
                    if MAX_QUEUE_LENGTH > 0 and task_queue.qsize() >= MAX_QUEUE_LENGTH:
                        error_response = {
                            "code": 429,
                            "id": data.get("id"),
                            "job_id": job_id,
                            "message": f"MAX_QUEUE_LENGTH ({MAX_QUEUE_LENGTH}) reached",
                            "pid": pid,
                            "queue_id": queue_id,
                            "queue_length": task_queue.qsize(),
                            "build_number": BUILD_NUMBER  # Add build number to response
                        }
                        
                        # Log the queue overflow error
                        log_job_status(job_id, {
                            "job_status": "done",
                            "job_id": job_id,
                            "queue_id": queue_id,
                            "process_id": pid,
                            "response": error_response
                        })
                        
                        return error_response, 429
                    
                    # Log job status as queued
                    log_job_status(job_id, {
                        "job_status": "queued",
                        "job_id": job_id,
                        "queue_id": queue_id,
                        "process_id": pid,
                        "response": None
                    })
                    
                    task_queue.put((job_id, data, lambda: f(job_id=job_id, data=data, *args, **kwargs), start_time))
                    
                    return {
                        "code": 202,
                        "id": data.get("id"),
                        "job_id": job_id,
                        "message": "processing",
                        "pid": pid,
                        "queue_id": queue_id,
                        "max_queue_length": MAX_QUEUE_LENGTH if MAX_QUEUE_LENGTH > 0 else "unlimited",
                        "queue_length": task_queue.qsize(),
                        "build_number": BUILD_NUMBER  # Add build number to response
                    }, 202
            return wrapper
        return decorator

    app.queue_task = queue_task

    # Import blueprints
    from routes.media_to_mp3 import convert_bp
    from routes.transcribe_media import transcribe_bp
    from routes.combine_videos import combine_bp
    from routes.audio_mixing import audio_mixing_bp
    from routes.gdrive_upload import gdrive_upload_bp
    from routes.authenticate import auth_bp
    from routes.caption_video import caption_bp 
    from routes.extract_keyframes import extract_keyframes_bp
    from routes.image_to_video import image_to_video_bp
    

    # Register blueprints
    app.register_blueprint(convert_bp)
    app.register_blueprint(transcribe_bp)
    app.register_blueprint(combine_bp)
    app.register_blueprint(audio_mixing_bp)
    app.register_blueprint(gdrive_upload_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(caption_bp)
    app.register_blueprint(extract_keyframes_bp)
    app.register_blueprint(image_to_video_bp)
    
    

    # version 1.0
    from routes.v1.ffmpeg.ffmpeg_compose import v1_ffmpeg_compose_bp
    from routes.v1.media.media_transcribe import v1_media_transcribe_bp
    from routes.v1.media.feedback import v1_media_feedback_bp
    from routes.v1.media.convert.media_to_mp3 import v1_media_convert_mp3_bp
    from routes.v1.video.concatenate import v1_video_concatenate_bp
    from routes.v1.video.caption_video import v1_video_caption_bp
    from routes.v1.image.convert.image_to_video import v1_image_convert_video_bp
    from routes.v1.toolkit.test import v1_toolkit_test_bp
    from routes.v1.toolkit.authenticate import v1_toolkit_auth_bp
    from routes.v1.code.execute.execute_python import v1_code_execute_bp
    from routes.v1.s3.upload import v1_s3_upload_bp
    from routes.v1.video.thumbnail import v1_video_thumbnail_bp
    from routes.v1.media.download import v1_media_download_bp
    from routes.v1.media.convert.media_convert import v1_media_convert_bp
    from routes.v1.audio.concatenate import v1_audio_concatenate_bp
    from routes.v1.media.silence import v1_media_silence_bp
    from routes.v1.video.cut import v1_video_cut_bp
    from routes.v1.video.split import v1_video_split_bp
    from routes.v1.video.trim import v1_video_trim_bp
    from routes.v1.media.metadata import v1_media_metadata_bp
    from routes.v1.toolkit.job_status import v1_toolkit_job_status_bp
    from routes.v1.toolkit.jobs_status import v1_toolkit_jobs_status_bp

    app.register_blueprint(v1_ffmpeg_compose_bp)
    app.register_blueprint(v1_media_transcribe_bp)
    app.register_blueprint(v1_media_feedback_bp)
    
    # Register a special route for Next.js root asset paths
    from routes.v1.media.feedback import create_root_next_routes
    create_root_next_routes(app)
    
    app.register_blueprint(v1_media_convert_mp3_bp)
    app.register_blueprint(v1_video_concatenate_bp)
    app.register_blueprint(v1_video_caption_bp)
    app.register_blueprint(v1_image_convert_video_bp)
    app.register_blueprint(v1_toolkit_test_bp)
    app.register_blueprint(v1_toolkit_auth_bp)
    app.register_blueprint(v1_code_execute_bp)
    app.register_blueprint(v1_s3_upload_bp)
    app.register_blueprint(v1_video_thumbnail_bp)
    app.register_blueprint(v1_media_download_bp)
    app.register_blueprint(v1_media_convert_bp)
    app.register_blueprint(v1_audio_concatenate_bp)
    app.register_blueprint(v1_media_silence_bp)
    app.register_blueprint(v1_video_cut_bp)
    app.register_blueprint(v1_video_split_bp)
    app.register_blueprint(v1_video_trim_bp)
    app.register_blueprint(v1_media_metadata_bp)
    app.register_blueprint(v1_toolkit_job_status_bp)
    app.register_blueprint(v1_toolkit_jobs_status_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)