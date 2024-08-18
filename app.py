from flask import Flask
from routes.convert import convert_bp
from routes.transcribe import transcribe_bp
from routes.combine import combine_bp
from routes.audio_mixing import audio_mixing_bp
from routes.gdrive_upload import gdrive_upload_bp
from routes.authentication import auth_bp
from routes.job_status import job_status_bp
from routes.job_submission import job_submission_bp

from services.csv_manager import initialize_csv
from services.job_processor import run_job_processor
from services.cleanup import start_cleanup_scheduler

import threading

app = Flask(__name__)

# Initialize the CSV file
initialize_csv()

# Register blueprints for your existing routes
app.register_blueprint(convert_bp)
app.register_blueprint(transcribe_bp)
app.register_blueprint(combine_bp)
app.register_blueprint(audio_mixing_bp)
app.register_blueprint(gdrive_upload_bp)
app.register_blueprint(auth_bp)

# Register blueprints for job management
app.register_blueprint(job_status_bp)
app.register_blueprint(job_submission_bp)

# Start the job processor in a separate thread
processor_thread = threading.Thread(target=run_job_processor)
processor_thread.daemon = True
processor_thread.start()

# Start the daily cleanup scheduler
start_cleanup_scheduler()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
