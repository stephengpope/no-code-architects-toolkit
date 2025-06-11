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
                url_domain = None
                if data.get("url"):
                    url_domain = urlparse(data["url"]).hostname
                elif data.get("html"):
                    url_domain = None
                for cookie in data["cookies"]:
                    cookie.setdefault("path", "/")
                    cookie_domain = cookie["domain"].lstrip(".")
                    if url_domain and not (url_domain == cookie_domain or url_domain.endswith(f".{cookie_domain}")):
                        raise Exception("COOKIE_DOMAIN_MISMATCH")
                context.add_cookies(data["cookies"])

            # Set page content from html or navigate to url
            if data.get("html"):
                page.set_content(data["html"])
            elif data.get("url"):
                page.goto(data["url"], timeout=data.get("timeout", 30000), wait_until=data.get("wait_until", "load"))
            else:
                raise Exception("MISSING_URL_OR_HTML")

            # Wait for a selector if specified
            if data.get("wait_for_selector"):
                try:
                    page.wait_for_selector(data["wait_for_selector"])
                except Exception as e:
                    raise Exception("WAIT_FOR_SELECTOR_NOT_FOUND")

            # Emulate media features
            if data.get("emulate"):
                if "color_scheme" in data["emulate"]:
                    page.emulate_media(color_scheme=data["emulate"]["color_scheme"])

            # Delay if specified
            if data.get("delay"):
                page.wait_for_timeout(data["delay"])

            # Inject custom CSS if provided
            if data.get("css"):
                page.add_style_tag(content=data["css"])
            # Inject custom JS if provided
            if data.get("js"):
                page.add_script_tag(content=data["js"])

            screenshot_io = BytesIO()

            # Ensure omit_background is only used with PNG
            if data.get("omit_background", False) and data.get("format", "png") == "jpeg":
                raise Exception("OMIT_BACKGROUND_JPEG_UNSUPPORTED")

            # and doesn't support quality settings - quality parameter only works with JPEG
            if data.get("format", "png") == "png" and data.get("quality") is not None:
                raise Exception("QUALITY_PNG_UNSUPPORTED")
            
            # Take a screenshot of a specific element or the full page
            if data.get("selector"):
                element = page.locator(data["selector"])
                if element.count() == 0:
                    raise Exception("ELEMENT_NOT_FOUND")
                screenshot = element.screenshot(
                    type=data.get("format", "png"),
                    quality=data.get("quality"),
                    omit_background=data.get("omit_background")
                )
            else:
                # Validate clip dimensions if provided
                if data.get("clip"):
                    clip = data["clip"]
                    if clip["x"] < 0 or clip["y"] < 0 or clip["width"] <= 0 or clip["height"] <= 0:
                        raise Exception("INVALID_CLIP_DIMENSIONS")
                screenshot = page.screenshot(
                    full_page=data.get("full_page", False),
                    type=data.get("format", "png"),
                    quality=data.get("quality"),
                    clip=data.get("clip"),
                    omit_background=data.get("omit_background")
                )

            screenshot_io.write(screenshot)
            screenshot_io.seek(0)
            return screenshot_io
        finally:
            browser.close()
    except Exception as e:
        logger.error(f"Job {job_id}: Error taking screenshot: {str(e)}", exc_info=True)
        error_message = str(e)
        error_map = {
            "ELEMENT_NOT_FOUND": f"The selector '{data.get('selector')}' was not found on the page. Please check your selector.",
            "INVALID_CLIP_DIMENSIONS": "Clip dimensions must be positive and non-negative.",
            "COOKIE_DOMAIN_MISMATCH": "A cookie domain does not match or is not a parent of the URL domain.",
            "OMIT_BACKGROUND_JPEG_UNSUPPORTED": "'omit_background' is only supported for PNG format.",
            "MISSING_URL_OR_HTML": "You must provide either a 'url' or 'html' field.",
            "WAIT_FOR_SELECTOR_NOT_FOUND": "The selector specified in 'wait_for_selector' was not found on the page.",
            "QUALITY_PNG_UNSUPPORTED": "'quality' is not supported for PNG (default format). Use JPEG format instead.",
        }
        error_message = error_map.get(error_message, str(e))
        return {"error": error_message}
    finally:
        p.stop()
