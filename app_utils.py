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



from flask import request, jsonify, current_app
from functools import wraps
import jsonschema

def validate_payload(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.json:
                return jsonify({"message": "Missing JSON in request"}), 400
            try:
                jsonschema.validate(instance=request.json, schema=schema)
            except jsonschema.exceptions.ValidationError as validation_error:
                return jsonify({"message": f"Invalid payload: {validation_error.message}"}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def queue_task_wrapper(bypass_queue=False):
    def decorator(f):
        def wrapper(*args, **kwargs):
            return current_app.queue_task(bypass_queue=bypass_queue)(f)(*args, **kwargs)
        return wrapper
    return decorator