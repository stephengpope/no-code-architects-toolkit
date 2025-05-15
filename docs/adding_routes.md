# Adding New Routes

This document explains how to add new routes to the application using the dynamic route registration system.

## Overview

The application now uses a dynamic route registration system that automatically discovers and registers all Flask blueprints in the `routes` directory. This means you no longer need to manually import and register blueprints in `app.py`.

## How to Add a New Route

1. **Create a new route file**

   Create a new Python file in the appropriate location in the `routes` directory. For a v1 API endpoint, you would typically place it in a subdirectory under `routes/v1/` based on the functionality.

   For example:
   ```
   routes/v1/email/send_email.py
   ```

2. **Define your Blueprint**

   In your route file, define a Flask Blueprint with a unique name. Make sure to follow the naming convention:
   
   ```python
   # routes/v1/email/send_email.py
   from flask import Blueprint, request
   from services.authentication import authenticate
   from app_utils import queue_task_wrapper

   v1_email_send_bp = Blueprint('v1_email_send', __name__)

   @v1_email_send_bp.route('/v1/email/send', methods=['POST'])
   @authenticate
   @queue_task_wrapper(bypass_queue=False)
   def send_email(job_id, data):
       """
       Send an email
       
       Args:
           job_id (str): Job ID assigned by queue_task_wrapper
           data (dict): Request data containing email details
       
       Returns:
           Tuple of (response_data, endpoint_string, status_code)
       """
       # Your implementation here
       endpoint = "/v1/email/send"
       
       # Return response
       return {"message": "Email sent"}, endpoint, 200
   ```

3. **That's it!**

   No need to modify `app.py`. The blueprint will be automatically discovered and registered when the application starts.

## Naming Conventions

When creating new routes, please follow these naming conventions:

1. **Blueprint names**: Use the format `{version}_{category}_{action}_bp`
   - Example: `v1_email_send_bp` for sending emails

2. **Route paths**: Use the format `/{version}/{category}/{action}`
   - Example: `/v1/email/send`

3. **File structure**: Place files in directories that match the route structure
   - Example: `routes/v1/email/send_email.py`

## Testing Your Route

After adding your route, restart the application and your new endpoint should be available immediately.

## Troubleshooting

If your route isn't being registered:

1. Check logs for any import errors
2. Ensure your blueprint variable is defined at the module level
3. Verify the blueprint name follows the naming convention
4. Make sure your Python file is in the correct directory under `routes/` 