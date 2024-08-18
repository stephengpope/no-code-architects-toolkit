from flask import Blueprint, request, jsonify
import uuid
from services.csv_manager import add_job
from services.job_processor import submit_job_to_executor
from services.authentication import authenticate

job_submission_bp = Blueprint('job_submission', __name__)

@job_submission_bp.route('/submit-job', methods=['POST'])
@authenticate
def submit_job():
    """Submit a new job to the queue."""
    data = request.json
    job_id = str(uuid.uuid4())
    job = {
        'job_id': job_id,
        'service_type': data['service_type'],
        'status': 'pending',
        'start_time': None,
        'end_time': None,
        'retry_count': 0,
        'error_message': None,
        'file_path': data['file_path'],
        'result': None
    }
    add_job(job)
    submit_job_to_executor(job)
    return jsonify({"job_id": job_id}), 201
