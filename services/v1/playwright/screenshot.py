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
# Created new service: /v1/playwright/screenshot

import os
import logging
from io import BytesIO
from playwright.sync_api import sync_playwright

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def take_screenshot(data: dict, job_id=None):
    p = sync_playwright().start()
    try:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context(
                viewport={"width": data.get("viewport_width", 1280), "height": data.get("viewport_height", 720)},
                device_scale_factor=data.get("device_scale_factor", 1),
                user_agent=data.get("user_agent")
            )
            page = context.new_page()

            # Validate and set headers
            if data.get("headers"):
                page.set_extra_http_headers(data["headers"])

            # Validate and set cookies
            if data.get("cookies"):
                from urllib.parse import urlparse
                url_domain = urlparse(data["url"]).hostname
                if not url_domain:
                    raise ValueError("Invalid URL provided.")
                for cookie in data["cookies"]:
                    cookie_domain = cookie["domain"].lstrip(".")
                    if not (url_domain == cookie_domain or url_domain.endswith(f".{cookie_domain}")):
                        raise ValueError(f"Cookie domain '{cookie['domain']}' does not match or is not a parent domain of URL domain '{url_domain}'.")
                context.add_cookies(data["cookies"])

            # Navigate to the URL
            page.goto(data["url"], timeout=data.get("timeout", 30000), wait_until=data.get("wait_until", "load"))

            # Wait for a selector if specified
            if data.get("wait_for_selector"):
                try:
                    page.wait_for_selector(data["wait_for_selector"])
                except Exception as e:
                    raise ValueError(f"Selector '{data['wait_for_selector']}' not found: {e}")

            # Emulate media features
            if data.get("emulate"):
                if "color_scheme" in data["emulate"]:
                    page.emulate_media(color_scheme=data["emulate"]["color_scheme"])

            # Delay if specified
            if data.get("delay"):
                page.wait_for_timeout(data["delay"])

            screenshot_io = BytesIO()

            # Take a screenshot of a specific element or the full page
            if data.get("selector"):
                element = page.locator(data["selector"])
                if element.count() == 0:
                    raise ValueError(f"Element '{data['selector']}' not found on the page.")
                screenshot = element.screenshot(
                    type=data.get("format", "png"),
                    quality=data.get("quality") if data.get("format") == "jpeg" else None,
                    omit_background=data.get("omit_background", False)
                )
            else:
                # Validate clip dimensions if provided
                if data.get("clip"):
                    clip = data["clip"]
                    if clip["x"] < 0 or clip["y"] < 0 or clip["width"] <= 0 or clip["height"] <= 0:
                        raise ValueError("Invalid clip dimensions.")
                screenshot = page.screenshot(
                    full_page=data.get("full_page", False),
                    type=data.get("format", "png"),
                    quality=data.get("quality") if data.get("format") == "jpeg" else None,
                    clip=data.get("clip"),
                    omit_background=data.get("omit_background", False)
                )

            # Ensure omit_background is only used with PNG
            if data.get("omit_background", False) and data.get("format", "png") == "jpeg":
                raise ValueError("The 'omit_background' option is not supported for JPEG format.")

            screenshot_io.write(screenshot)
            screenshot_io.seek(0)
            return screenshot_io
        finally:
            browser.close()
    except Exception as e:
        logger.error(f"Job {job_id}: Error taking screenshot: {str(e)}", exc_info=True)
        return {"error": str(e)}
    finally:
        p.stop()
