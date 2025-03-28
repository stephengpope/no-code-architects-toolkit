from flask import Blueprint, send_from_directory, current_app, request, redirect, url_for, make_response
import os
import mimetypes
import re
from services.v1.media.feedback.feedback import get_feedback_path

# Ensure correct MIME types for Next.js assets
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('font/woff2', '.woff2')

# Base URL path for assets
BASE_PATH = '/v1/media/feedback'

v1_media_feedback_bp = Blueprint('v1_media_feedback', __name__, url_prefix='/v1/media/feedback', static_folder=None)

def create_root_next_routes(app):
    """
    Create routes at the application root level to handle Next.js asset paths
    This helps with client-side navigation and dynamic asset loading
    """
    @app.route('/_next/<path:path>')
    def root_next_static(path):
        """Redirect root-level Next.js requests to our namespaced route"""
        return redirect(f'{BASE_PATH}/_next/{path}')
        
    @app.route('/favicon.ico')
    def root_favicon():
        """Redirect favicon requests to our namespaced route"""
        return redirect(f'{BASE_PATH}/favicon.ico')
        
    @app.route('/logo.png')
    def root_logo():
        """Redirect logo requests to our namespaced route"""
        return redirect(f'{BASE_PATH}/logo.png')

@v1_media_feedback_bp.route('', methods=['GET'])
def serve_feedback_page():
    """
    Serve the feedback HTML page with path corrections
    """
    try:
        # Get the feedback static files directory path
        feedback_path = get_feedback_path()
        
        # Read the HTML file content
        with open(os.path.join(feedback_path, 'index.html'), 'r') as f:
            content = f.read()
        
        # Fix paths in the HTML content to include the base path
        # Replace resource paths
        content = content.replace('href="/_next/', f'href="{BASE_PATH}/_next/')
        content = content.replace('src="/_next/', f'src="{BASE_PATH}/_next/')
        content = content.replace('href="/favicon.ico', f'href="{BASE_PATH}/favicon.ico')
        content = content.replace('href="/logo.png', f'href="{BASE_PATH}/logo.png')
        content = content.replace('src="/logo.png', f'src="{BASE_PATH}/logo.png')
        
        # Create response with modified content
        response = make_response(content)
        response.headers['Content-Type'] = 'text/html'
        return response
    except Exception as e:
        current_app.logger.error(f"Error serving index.html: {str(e)}")
        return str(e), 'serve_feedback_page', 500

@v1_media_feedback_bp.route('/_next/<path:path>', methods=['GET'])
def serve_next_static(path):
    """
    Serve Next.js static files from _next directory
    """
    try:
        feedback_path = get_feedback_path()
        file_path = os.path.join('_next', path)
        full_path = os.path.join(feedback_path, file_path)
        
        # Get the file extension for MIME type detection
        _, ext = os.path.splitext(path)
        
        # Handle special case for JS files to fix paths
        if ext == '.js':
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                        
                    # Fix paths in JS files that might reference other assets
                    if '/_next/' in content:
                        content = content.replace('href:"/_next/', f'href:"{BASE_PATH}/_next/')
                        content = content.replace('src:"/_next/', f'src:"{BASE_PATH}/_next/')
                        
                        # Create response with modified content
                        response = make_response(content)
                        response.headers['Content-Type'] = 'application/javascript'
                        return response
                except UnicodeDecodeError:
                    # If we can't read as text, serve as binary
                    pass
        
        # Handle special case for font files
        if ext == '.woff2' or ext == '.woff' or ext == '.ttf' or ext == '.eot':
            response = send_from_directory(feedback_path, file_path)
            if ext == '.woff2':
                response.headers['Content-Type'] = 'font/woff2'
            elif ext == '.woff':
                response.headers['Content-Type'] = 'font/woff'
            elif ext == '.ttf':
                response.headers['Content-Type'] = 'font/ttf'
            elif ext == '.eot':
                response.headers['Content-Type'] = 'application/vnd.ms-fontobject'
            
            # Add CORS headers for font files
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        
        # For other files, serve directly
        mime_type = mimetypes.types_map.get(ext, 'application/octet-stream')
        
        response = send_from_directory(feedback_path, file_path)
        response.headers['Content-Type'] = mime_type

        # Add CORS headers for font files
        if ext == '.woff2' or ext == '.woff' or ext == '.ttf' or ext == '.eot':
            response.headers['Access-Control-Allow-Origin'] = '*'
            
        return response
    except Exception as e:
        current_app.logger.error(f"Error serving Next.js static file {path}: {str(e)}")
        return str(e), 'serve_next_static', 500

@v1_media_feedback_bp.route('/<path:filename>', methods=['GET'])
def serve_feedback_static(filename):
    """
    Serve static files for the feedback page (CSS, JS, images, etc.)
    """
    try:
        # Get the feedback static files directory path
        feedback_path = get_feedback_path()
        
        # Special handling for CSS files that might need path rewriting
        _, ext = os.path.splitext(filename)
        if ext == '.css':
            full_path = os.path.join(feedback_path, filename)
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    content = f.read()
                
                # Rewrite paths in CSS if needed
                if 'url(/_next/' in content:
                    content = content.replace('url(/_next/', f'url({BASE_PATH}/_next/')
                    
                    # Create response with modified content
                    response = make_response(content)
                    response.headers['Content-Type'] = 'text/css'
                    return response
        
        # Handle JavaScript files
        if ext == '.js':
            full_path = os.path.join(feedback_path, filename)
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    content = f.read()
                
                # Rewrite paths in JS if needed
                if '/_next/' in content:
                    content = content.replace('href:"/_next/', f'href:"{BASE_PATH}/_next/')
                    content = content.replace('src:"/_next/', f'src:"{BASE_PATH}/_next/')
                    
                    # Create response with modified content
                    response = make_response(content)
                    response.headers['Content-Type'] = 'application/javascript'
                    return response
        
        # For image and other static files
        mime_type = mimetypes.types_map.get(ext, 'application/octet-stream')
        
        # Serve the requested static file
        response = send_from_directory(feedback_path, filename)
        response.headers['Content-Type'] = mime_type
        return response
    except FileNotFoundError:
        current_app.logger.error(f"Static file not found: {filename}")
        return "File not found", 404
    except Exception as e:
        current_app.logger.error(f"Error serving static file {filename}: {str(e)}")
        return str(e), 500
