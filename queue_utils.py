from flask import request, jsonify, current_app
from functools import wraps

def validate_payload(*required_fields):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.json:
                return jsonify({"message": "Missing JSON in request"}), 400
            
            missing_fields = [field for field in required_fields if field not in request.json]
            if missing_fields:
                return jsonify({"message": f"Missing required fields: {', '.join(missing_fields)}"}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def queue_task_wrapper(bypass_queue=False):
    def decorator(f):
        def wrapper(*args, **kwargs):
            return current_app.queue_task(bypass_queue=bypass_queue)(f)(*args, **kwargs)
        return wrapper
    return decorator