from flask import Blueprint, request, jsonify
import logging
import json
from datetime import datetime
from pathlib import Path
import glob

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

v1_video_comments_bp = Blueprint('v1_video_comments', __name__)

# Get the directory where this file is located
CURRENT_DIR = Path(__file__).parent
# Create comments directory adjacent to this file
COMMENTS_DIR = CURRENT_DIR / 'comments'

def get_video_id(video_url):
    """Extract a clean video ID from the URL."""
    # Remove any query parameters
    base_url = video_url.split('?')[0]
    # Get the last part of the path
    video_id = base_url.split('/')[-1]
    # Remove any file extension
    video_id = Path(video_id).stem
    # Remove any special characters
    return ''.join(c for c in video_id if c.isalnum())

@v1_video_comments_bp.route('/api/comments/<video_id>', methods=['GET'])
def load_comments(video_id):
    try:
        # Find all comment files for this video ID
        pattern = str(COMMENTS_DIR / f"{video_id}_*.json")
        comment_files = sorted(glob.glob(pattern), reverse=True)
        
        if not comment_files:
            logger.info(f"No comments found for video ID: {video_id}")
            return jsonify({
                "message": "No comments found for this video",
                "data": {"comments": []}
            }), 404

        # Load the most recent comments file
        with open(comment_files[0], 'r') as f:
            comments_data = json.load(f)
        
        logger.info(f"Successfully loaded comments from {comment_files[0]}")
        return jsonify({
            "message": "Comments loaded successfully",
            "data": comments_data,
            "filename": Path(comment_files[0]).name
        }), 200

    except Exception as e:
        logger.error(f"Error loading comments for video ID {video_id}: {str(e)}")
        return jsonify({
            "error": "Failed to load comments",
            "details": str(e)
        }), 500

@v1_video_comments_bp.route('/api/comments', methods=['POST'])
def save_comments():
    try:
        data = request.get_json()
        if not data or 'comments' not in data or 'videoUrl' not in data or 'videoId' not in data:
            logger.error("Invalid request data: Missing required fields")
            return jsonify({"error": "Missing required fields"}), 400

        # Use provided video ID and create filename
        video_id = data['videoId']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{video_id}_{timestamp}.json"
        filepath = COMMENTS_DIR / filename

        # Save comments to file
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Successfully saved comments to {filepath}")
        return jsonify({
            "message": "Comments saved successfully",
            "filename": filename,
            "timestamp": timestamp
        }), 200

    except Exception as e:
        logger.error(f"Error saving comments: {str(e)}")
        return jsonify({"error": "Failed to save comments"}), 500 