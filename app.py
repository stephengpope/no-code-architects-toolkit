from flask import Flask, request
from queue import Queue
import threading
import uuid

def create_app():
    app = Flask(__name__)

    # Create a queue to hold tasks
    task_queue = Queue()

    # Function to process tasks from the queue
    def process_queue():
        while True:
            job_id, data, task_func = task_queue.get()
            task_func()
            task_queue.task_done()

    # Start the queue processing in a separate thread
    threading.Thread(target=process_queue, daemon=True).start()

    # Decorator to add tasks to the queue or bypass it
    def queue_task(bypass_queue=False):
        def decorator(f):
            def wrapper(*args, **kwargs):
                job_id = str(uuid.uuid4())
                data = request.json
                if bypass_queue or 'webhook_url':
                    return f(job_id=job_id, data=data, *args, **kwargs)
                else:
                    task_queue.put((job_id, data, lambda: f(job_id=job_id, data=data, *args, **kwargs)))
                    return {
                            "code": 202,
                            "id": data.get("id"),
                            "job_id": job_id,
                            "message": "processing"
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
    from routes.authentication import auth_bp
    from routes.caption_video import caption_bp 
    from routes.extract_keyframes import extract_keyframes_bp

    # Register blueprints
    app.register_blueprint(convert_bp)
    app.register_blueprint(transcribe_bp)
    app.register_blueprint(combine_bp)
    app.register_blueprint(audio_mixing_bp)
    app.register_blueprint(gdrive_upload_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(caption_bp)
    app.register_blueprint(extract_keyframes_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)