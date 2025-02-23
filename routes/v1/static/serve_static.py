from flask import Blueprint, send_from_directory

v1_static_serve_bp = Blueprint('v1_static_serve', __name__)

@v1_static_serve_bp.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@v1_static_serve_bp.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path) 