import os
import logging
from flask import Blueprint, request, send_file, jsonify
from services.authentication import authenticate

logger = logging.getLogger(__name__)
v1_files_content_bp = Blueprint('v1_files_content', __name__)

ALLOWED_DIRS = ['/data/output', os.environ.get('LOCAL_STORAGE_PATH', '/tmp')]


@v1_files_content_bp.route('/v1/files/content', methods=['GET'])
@authenticate
def files_content():
    """Serve a file from the local output directory.

    Query params:
        path: The container path to serve (e.g., /data/output/uuid.mp4)

    Returns the file as a binary download with appropriate content type.
    """
    file_path = request.args.get('path', '')
    if not file_path:
        return jsonify({"message": "Missing 'path' query parameter"}), 400

    # Security: resolve to absolute path and verify it's within allowed dirs
    real_path = os.path.realpath(file_path)
    allowed = any(real_path.startswith(os.path.realpath(d)) for d in ALLOWED_DIRS)
    if not allowed:
        logger.warning(f"Rejected file content request for: {file_path} (resolved: {real_path})")
        return jsonify({"message": "Access denied"}), 403

    if not os.path.isfile(real_path):
        return jsonify({"message": "File not found"}), 404

    return send_file(real_path, as_attachment=True)
