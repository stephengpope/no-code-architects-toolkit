from flask import Blueprint, jsonify, request
from services.csv_manager import get_jobs
from services.authentication import authenticate

job_status_bp = Blueprint('job_status', __name__)

@job_status_bp.route('/job-status', methods=['GET'])
@authenticate
def get_job_status():
    """Return the status of all jobs in JSON format."""
    jobs = get_jobs()
    return jsonify(jobs), 200
