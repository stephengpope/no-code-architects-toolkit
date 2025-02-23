from flask import Blueprint, request, jsonify
import logging
import json
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

v1_video_comments_bp = Blueprint('v1_video_comments', __name__)

# Ensure comments directory exists
COMMENTS_DIR = 'comments'
if not os.path.exists(COMMENTS_DIR):
    os.makedirs(COMMENTS_DIR)

@v1_video_comments_bp.route('/api/comments', methods=['POST'])
def save_comments():
    try:
        data = request.get_json()
        if not data or 'comments' not in data or 'videoUrl' not in data:
            logger.error("Invalid request data: Missing required fields")
            return jsonify({"error": "Missing required fields"}), 400

        # Create a filename based on video URL and timestamp
        video_id = data['videoUrl'].split('/')[-1]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{video_id}_{timestamp}.json"
        filepath = os.path.join(COMMENTS_DIR, filename)

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
