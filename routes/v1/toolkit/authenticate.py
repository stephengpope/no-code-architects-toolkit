from flask import Blueprint, request, jsonify, current_app
from app_utils import *
from functools import wraps
import os

v1_toolkit_auth_bp = Blueprint('v1_toolkit_auth', __name__)

API_KEY = os.environ.get('API_KEY')

@v1_toolkit_auth_bp.route('/v1/toolkit/authenticate', methods=['GET'])
@queue_task_wrapper(bypass_queue=True)
def authenticate_endpoint(**kwargs):
    api_key = request.headers.get('X-API-Key')
    if api_key == API_KEY:
        return "Authorized", "/authenticate", 200
    else:
        return "Unauthorized", "/authenticate", 401
