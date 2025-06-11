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


# Author: Harrison Fisher (https://github.com/HarrisonFisher)
# Date: April 2025
# Created new route: /v1/playwright/screenshot

from flask import Blueprint, request, jsonify
from app_utils import *
from app_utils import validate_payload, queue_task_wrapper
import logging
import os
from services.v1.image.screenshot_webpage import take_screenshot
from services.authentication import authenticate
from services.cloud_storage import upload_file
from playwright.sync_api import sync_playwright
from io import BytesIO


v1_image_screenshot_webpage_bp = Blueprint('v1_image_screenshot_webpage', __name__)
logger = logging.getLogger(__name__)


@v1_image_screenshot_webpage_bp.route('/v1/image/screenshot/webpage', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "url": {"type": "string", "format": "uri"},
        "html": {"type": "string"},
        "viewport_width": {"type": "integer", "minimum": 1},
        "viewport_height": {"type": "integer", "minimum": 1},
        "full_page": {"type": "boolean", "default": False},
        "format": {"type": "string", "enum": ["png", "jpeg"], "default": "png"},
        "delay": {"type": "integer", "minimum": 0},
        "device_scale_factor": {"type": "number", "minimum": 0.1},
        "user_agent": {"type": "string"},
        "cookies": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "value", "domain"],
                "properties": {
                    "name": {"type": "string"},
                    "value": {"type": "string"},
                    "domain": {"type": "string"},
                    "path": {"type": "string", "default": "/"},
                },
                "additionalProperties": True
            }
        },
        "headers": {
            "type": "object",
            "additionalProperties": {"type": "string"}
        },
        "quality": {"type": "integer", "minimum": 0, "maximum": 100},
        "clip": {
            "type": "object",
            "required": ["x", "y", "width", "height"],
            "properties": {
                "x": {"type": "number"},
                "y": {"type": "number"},
                "width": {"type": "number", "exclusiveMinimum": 0},
                "height": {"type": "number", "exclusiveMinimum": 0}
            }
        },
        "timeout": {"type": "integer", "minimum": 100},
        "wait_until": {"type": "string", "enum": ["load", "domcontentloaded", "networkidle", "networkidle2"], "default": "load"},
        "wait_for_selector": {"type": "string"},
        "emulate": {
            "type": "object",
            "properties": {
                "color_scheme": {
                    "type": "string",
                    "enum": ["light", "dark"]
                }
            }
        },
        "omit_background": {"type": "boolean", "default": False},
        "selector": {"type": "string"},
        "js": {"type": "string"},
        "css": {"type": "string"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "oneOf": [
        {"required": ["url"]},
        {"required": ["html"]}
    ],
    "not": {"required": ["url", "html"]},
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def screenshot(job_id, data):
    logger.info(f"Job {job_id}: Received screenshot request for {data.get('url')}")
    try:
        screenshot_io = take_screenshot(data, job_id)
        if isinstance(screenshot_io, dict) and 'error' in screenshot_io:
            logger.error(f"Job {job_id}: Screenshot error: {screenshot_io['error']}")
            return {"error": screenshot_io['error']}, "/v1/image/screenshot/webpage", 400
        format = data.get("format", "png")
        temp_file_path = f"{job_id}_screenshot.{format}"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(screenshot_io.read())
        cloud_url = upload_file(temp_file_path)
        os.remove(temp_file_path)
        logger.info(f"Job {job_id}: Screenshot successfully processed and uploaded.")
        return cloud_url, "/v1/image/screenshot/webpage", 200
    except Exception as e:
        logger.error(f"Job {job_id}: Error processing screenshot: {str(e)}", exc_info=True)
        return {"error": str(e)}, "/v1/image/screenshot/webpage", 500