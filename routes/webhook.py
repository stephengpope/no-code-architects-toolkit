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

from flask import Blueprint, request, jsonify
import logging
import json
from typing import Dict, Any

# Set up logging
logger = logging.getLogger(__name__)

# Create the blueprint
webhook_bp = Blueprint('webhook', __name__, url_prefix='/v1/webhook')

# In-memory storage for webhook results (in production, use Redis or database)
webhook_results = {}

@webhook_bp.route('/runpod', methods=['POST'])
def handle_runpod_webhook():
    """
    Handle webhook callbacks from Runpod API.
    
    This endpoint receives the results of async Runpod transcription jobs
    and stores them for later retrieval.
    """
    try:
        # Get the JSON payload from Runpod
        data = request.get_json()
        
        if not data:
            logger.error("No JSON data received in webhook")
            return jsonify({"error": "No JSON data received"}), 400
        
        # Extract job information
        job_id = data.get('id')
        status = data.get('status')
        output = data.get('output')
        error = data.get('error')
        
        logger.info(f"Received webhook for job {job_id} with status: {status}")
        
        if not job_id:
            logger.error("No job ID in webhook data")
            return jsonify({"error": "No job ID provided"}), 400
        
        # Store the result
        webhook_results[job_id] = {
            'job_id': job_id,
            'status': status,
            'output': output,
            'error': error,
            'timestamp': data.get('timestamp'),
            'raw_data': data
        }
        
        if status == 'COMPLETED':
            logger.info(f"Job {job_id} completed successfully")
        elif status == 'FAILED':
            logger.error(f"Job {job_id} failed: {error}")
        else:
            logger.info(f"Job {job_id} status update: {status}")
        
        # Return success response
        return jsonify({
            "status": "received",
            "job_id": job_id,
            "message": f"Webhook processed for job {job_id}"
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@webhook_bp.route('/runpod/status/<job_id>', methods=['GET'])
def get_webhook_result(job_id: str):
    """
    Get the result of a Runpod job from webhook storage.
    
    Args:
        job_id: The job ID to get results for
        
    Returns:
        JSON response with job results or status
    """
    try:
        if job_id not in webhook_results:
            return jsonify({
                "error": "Job not found",
                "job_id": job_id,
                "message": "Job ID not found in webhook results"
            }), 404
        
        result = webhook_results[job_id]
        
        if result['status'] == 'COMPLETED':
            # Transform the output to Whisper format if needed
            from services.runpod_whisper import runpod_client
            
            try:
                transformed_result = runpod_client._transform_runpod_response(result['output'])
                return jsonify({
                    "status": "completed",
                    "job_id": job_id,
                    "result": transformed_result
                }), 200
            except Exception as transform_error:
                logger.error(f"Error transforming result for job {job_id}: {str(transform_error)}")
                return jsonify({
                    "status": "completed",
                    "job_id": job_id,
                    "raw_output": result['output'],
                    "transform_error": str(transform_error)
                }), 200
                
        elif result['status'] == 'FAILED':
            return jsonify({
                "status": "failed",
                "job_id": job_id,
                "error": result['error']
            }), 200
            
        else:
            return jsonify({
                "status": result['status'],
                "job_id": job_id,
                "message": f"Job is {result['status']}"
            }), 200
            
    except Exception as e:
        logger.error(f"Error getting webhook result for job {job_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@webhook_bp.route('/runpod/jobs', methods=['GET'])
def list_webhook_jobs():
    """
    List all jobs stored in webhook results.
    
    Returns:
        JSON response with list of job IDs and their statuses
    """
    try:
        jobs = []
        for job_id, result in webhook_results.items():
            jobs.append({
                "job_id": job_id,
                "status": result['status'],
                "timestamp": result['timestamp']
            })
        
        return jsonify({
            "jobs": jobs,
            "total": len(jobs)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing webhook jobs: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@webhook_bp.route('/runpod/cleanup', methods=['POST'])
def cleanup_webhook_results():
    """
    Clean up completed or failed jobs from webhook storage.
    
    Returns:
        JSON response with cleanup results
    """
    try:
        data = request.get_json() or {}
        cleanup_completed = data.get('cleanup_completed', True)
        cleanup_failed = data.get('cleanup_failed', True)
        
        cleaned_jobs = []
        for job_id in list(webhook_results.keys()):
            result = webhook_results[job_id]
            should_clean = False
            
            if cleanup_completed and result['status'] == 'COMPLETED':
                should_clean = True
            elif cleanup_failed and result['status'] == 'FAILED':
                should_clean = True
            
            if should_clean:
                del webhook_results[job_id]
                cleaned_jobs.append(job_id)
        
        return jsonify({
            "cleaned_jobs": cleaned_jobs,
            "count": len(cleaned_jobs),
            "remaining_jobs": len(webhook_results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error cleaning up webhook results: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
