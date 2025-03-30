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
