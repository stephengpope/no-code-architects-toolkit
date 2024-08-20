from flask import Blueprint, request, jsonify
from functools import wraps
import os

auth_bp = Blueprint('auth', __name__)

API_KEY = os.environ.get('API_KEY')

def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper

@auth_bp.route('/authenticate', methods=['POST'])
def authenticate_endpoint():
    api_key = request.headers.get('X-API-Key')
    if api_key == API_KEY:
        return jsonify({"message": "Authorized"}), 200
    else:
        return jsonify({"message": "Unauthorized"}), 401
