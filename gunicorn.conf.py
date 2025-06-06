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
#              at startup, monitor its status if a webhook URL is provided, 
#              and shut down the server once the job completes or if an error occurs.

import os
import json
import requests
import signal
import sys
import time
import threading
from flask import request

def wait_for_job_to_complete(api_url, api_key, job_id, poll_interval=5):
    headers = {'x-api-key': api_key}
    consecutive_failures = 0
    max_failures = 2

    while consecutive_failures <= max_failures:
        try:
            response = requests.post(
                f"{api_url}/v1/toolkit/job/status",
                json={"job_id": job_id},
                headers=headers
            )

            if response.status_code != 200:
                print(f"Failed to get job status: {response.status_code}")
                consecutive_failures += 1
            else:
                job_status = response.json()
                status = job_status.get("response", {}).get("job_status")

                if status and status != "running":
                    print(f"✅ Job {job_id} has completed with status: {status}")
                    return True

                consecutive_failures = 0  # Reset on success

        except Exception as e:
            print("Error checking job status:", e)
            consecutive_failures += 1

        if consecutive_failures > max_failures:
            print("❌ Too many consecutive failures. Giving up.")
            return False

        time.sleep(poll_interval)

    print("🔁 Exited polling loop without determining job status.")
    return False


def cloud_run_job_task():
    path = os.environ.get("CLOUD_RUN_JOB_PATH")
    payload = os.environ.get("CLOUD_RUN_JOB_PAYLOAD")
    api_key = os.environ.get("API_KEY")

    if path and payload and api_key:
        try:
            print("📤 Sending auto request...")
            time.sleep(1)
            response = requests.post(f"http://localhost:8080{path}", json=json.loads(payload), headers={
                "x-api-key": api_key,
                "Content-Type": "application/json"
            })

            if response.status_code == 200 or response.status_code == 202:
                print("✅ Request sent successfully. Response:")
                response_json = response.json()
                print(json.dumps(response_json, indent=4))

                job_id = response_json.get("job_id")
            
                if job_id:
                    parsed_payload = json.loads(payload)
                    if "webhook_url" in parsed_payload:
                        print("🔔 Webhook URL detected in payload. Monitoring job to trigger webhook.")
                        wait_for_job_to_complete(
                            "http://localhost:8080",
                            api_key,
                            job_id,
                        )
                        time.sleep(1) # Wait for webhook to trigger (could be optimized???)
                    else:
                        print("📭 No webhook URL found. Skipping job monitoring.")
                else:
                    print("⚠️ No job_id found in response. Cannot monitor job status.")

            else:
                print(f"❌ Request failed with status code {response.status_code}. Response:")
                print(json.dumps(response.json(), indent=4))
            

        except Exception as e:
            print("❌ Error sending auto request:", e)
            os._exit(1)
        finally:
            print("🛑 Shutting down server...")
            os._exit(0)
    else:
        print("⚠️ Environment variables PATH, PAYLOAD, and API_KEY must be set.")
        os._exit(1)    


def when_ready(server):
    """Hook called when the server is ready."""
    if os.environ.get("CLOUD_RUN_JOB", "") != "":
        thread = threading.Thread(target=cloud_run_job_task)
        thread.start()