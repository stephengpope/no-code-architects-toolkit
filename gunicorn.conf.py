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


###########################################################################

# Author: Harrison Fisher (https://github.com/HarrisonFisher)
# Date: May 2025
# Description: This script configures the server to automatically trigger a job request
#              at startup when running as a GCP Cloud Run Job, and shut down the server
#              once the job completes or if an error occurs.

import os
import json
import requests
import time

def cloud_run_job_task():
    """Execute a single job request and shut down."""
    path = os.environ.get("GCP_JOB_PATH")
    payload_str = os.environ.get("GCP_JOB_PAYLOAD")
    api_key = os.environ.get("API_KEY")

    if not (path and payload_str and api_key):
        print("⚠️ Missing required environment variables: GCP_JOB_PATH, GCP_JOB_PAYLOAD, or API_KEY")
        os._exit(1)

    try:
        payload = json.loads(payload_str)
        webhook_url = payload.get("webhook_url")

        print(f"📤 Executing GCP job request to {path}...")
        time.sleep(1)  # Brief delay for server readiness

        response = requests.post(
            f"http://localhost:8080{path}",
            json=payload,
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json"
            }
        )

        if response.status_code in [200, 202]:
            print("✅ Job completed successfully")
            print(json.dumps(response.json(), indent=2))
            # Webhook already sent by app.py if needed

        else:
            # Error case - we need to notify user via webhook
            print(f"❌ Job failed with status {response.status_code}")
            try:
                error_response = response.json() if response.headers.get('content-type') == 'application/json' else {"error": response.text}
            except:
                error_response = {"error": response.text}
            print(json.dumps(error_response, indent=2))

            # Send webhook notification of failure
            if webhook_url:
                try:
                    webhook_data = {
                        "code": response.status_code,
                        "id": payload.get("id"),
                        "message": f"Job failed with status {response.status_code}",
                        "error": error_response
                    }
                    print(f"🔔 Sending error webhook to {webhook_url}")
                    webhook_response = requests.post(webhook_url, json=webhook_data)
                    webhook_response.raise_for_status()
                    print("✅ Error webhook sent successfully")
                except Exception as webhook_error:
                    print(f"❌ Failed to send error webhook: {webhook_error}")

    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        # Try to send webhook about the error
        try:
            if webhook_url:
                webhook_data = {
                    "code": 500,
                    "id": payload.get("id"),
                    "message": f"Job request failed: {str(e)}",
                    "error": str(e)
                }
                requests.post(webhook_url, json=webhook_data)
        except:
            pass
        os._exit(1)

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        os._exit(1)

    finally:
        print("🛑 Shutting down...")
        os._exit(0)


def when_ready(server):
    """Hook called when Gunicorn server is ready."""
    if os.environ.get("CLOUD_RUN_JOB"):
        import threading
        thread = threading.Thread(target=cloud_run_job_task)
        thread.start()
