import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.csv_manager import get_jobs, update_job
from services.ffmpeg_processing import process_conversion
from services.whisper_transcription import process_transcription
from services.gdrive_service import process_gdrive_upload
from datetime import datetime

MAX_WORKERS = 4  # Number of concurrent workers; adjust based on your system's capability

executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

def process_job(job):
    """Process an individual job based on its service type."""
    job_id = job['job_id']
    service_type = job['service_type']
    retry_count = int(job['retry_count'])

    try:
        update_job(job_id, {'status': 'working', 'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        
        # Determine the service type and process accordingly
        if service_type == 'convert_media_to_mp3':
            process_conversion(job['file_path'], job.get('webhook_url'))
        elif service_type == 'transcribe_media':
            process_transcription(job['file_path'], job['result'], job.get('webhook_url'))
        elif service_type == 'gdrive_upload':
            process_gdrive_upload(job['file_path'], job['result'], job.get('folder_id'), job.get('webhook_url'))

        update_job(job_id, {'status': 'completed', 'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    except Exception as e:
        # Retry logic
        if retry_count < 1:
            update_job(job_id, {'retry_count': retry_count + 1, 'status': 'pending', 'error_message': str(e)})
        else:
            update_job(job_id, {'status': 'failed', 'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'error_message': str(e)})

def submit_job_to_executor(job):
    """Submit a job to the ThreadPoolExecutor for processing."""
    future = executor.submit(process_job, job)
    return future

def run_job_processor():
    """Continuously process jobs from the queue."""
    while True:
        pending_jobs = get_jobs(status='pending')
        for job in pending_jobs:
            submit_job_to_executor(job)
        time.sleep(5)  # Wait before checking for new jobs
