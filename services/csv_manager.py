import csv
import threading
import os
from datetime import datetime, timedelta
from config import STORAGE_PATH

CSV_FILE_PATH = os.path.join(STORAGE_PATH, 'job_queue.csv')
CSV_LOCK = threading.Lock()

# Define the headers for the CSV file
CSV_HEADERS = [
    'job_id', 'service_type', 'status', 'start_time', 'end_time', 
    'retry_count', 'error_message', 'file_path', 'result'
]

def initialize_csv():
    """Initialize the CSV file with headers if it does not exist."""
    if not os.path.exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
            writer.writeheader()

def add_job(job):
    """Add a new job to the CSV file."""
    with CSV_LOCK:
        with open(CSV_FILE_PATH, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
            writer.writerow(job)

def update_job(job_id, updates):
    """Update the status of a job in the CSV file."""
    with CSV_LOCK:
        rows = []
        with open(CSV_FILE_PATH, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['job_id'] == job_id:
                    row.update(updates)
                rows.append(row)
        
        with open(CSV_FILE_PATH, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(rows)

def get_jobs(status=None):
    """Retrieve jobs from the CSV file. Optionally filter by status."""
    with CSV_LOCK:
        with open(CSV_FILE_PATH, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            jobs = [row for row in reader if status is None or row['status'] == status]
    return jobs

def remove_old_jobs(retention_days=1):
    """Remove jobs that are older than the retention period."""
    cutoff_time = datetime.now() - timedelta(days=retention_days)
    with CSV_LOCK:
        rows = []
        with open(CSV_FILE_PATH, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                end_time = datetime.strptime(row['end_time'], '%Y-%m-%d %H:%M:%S') if row['end_time'] else None
                if end_time is None or end_time >= cutoff_time:
                    rows.append(row)
        
        with open(CSV_FILE_PATH, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(rows)
