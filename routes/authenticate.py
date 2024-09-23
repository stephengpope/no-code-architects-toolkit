from flask import Blueprint, request, jsonify, current_app
from app_utils import *
from functools import wraps
import os

auth_bp = Blueprint('auth', __name__)

API_KEY = os.environ.get('API_KEY')

@auth_bp.route('/authenticate', methods=['GET'])
@queue_task_wrapper(bypass_queue=True)
def authenticate_endpoint(**kwargs):
    api_key = request.headers.get('X-API-Key')
    if api_key == API_KEY:
        return "Authorized", "/authenticate", 200
    else:
        return "Unauthorized", "/authenticate", 401
