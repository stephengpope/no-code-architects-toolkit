from flask import Blueprint, request, jsonify
from services.authentication import authenticate

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/authenticate', methods=['POST'])
@authenticate
def authenticate_route():
    return jsonify({"message": "Authorized"}), 200
