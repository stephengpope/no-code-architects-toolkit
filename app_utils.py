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
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Access current_app within the request context
            queue_task_decorator = current_app.queue_task(bypass_queue=bypass_queue)
            return queue_task_decorator(f)(*args, **kwargs)
        return wrapped
    return decorator