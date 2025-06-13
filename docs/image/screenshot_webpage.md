# Playwright Screenshot Endpoint

**Implemented by:** [Harrison Fisher](https://github.com/HarrisonFisher)

## ⚠️ Disclaimer
- This endpoint is **not intended to bypass CAPTCHAs, Cloudflare**, or other anti-bot protections.
- Please **do not create issues or requests** asking for CAPTCHA or Cloudflare bypass features.
- It will not work for sites with such defenses, and attempting to automate against protected sites could result in your IP address being blacklisted by Cloudflare or similar services.
- The screenshot endpoint supports custom HTML, JavaScript, and CSS input for flexible rendering and automation, as an alternative to using a URL.
- This feature should only be used on sites you own or have explicit permission to automate.


## 1. Overview

The `/v1/image/screenshot/webpage` endpoint allows you to capture screenshots of web pages using the Playwright browser automation library. It supports advanced options such as viewport size, device emulation, cookies, headers, element targeting, and more. Screenshots are uploaded to cloud storage, and the resulting URL is returned. This endpoint is part of the v1 API suite and is registered in the main Flask application as a blueprint.

## 2. Endpoint

- **URL Path:** `/v1/image/screenshot/webpage`
- **HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): Your API key for authentication.
- `Content-Type`: `application/json`

### Body Parameters

The request body must be a JSON object with the following properties:

- `url` (string, required): The URL of the web page to capture.
- `html` (string, optional): Raw HTML content to render and capture.  
  **Note:** Either `url` or `html` must be provided, but not both.
- `viewport_width` (integer, optional): Viewport width in pixels.
- `viewport_height` (integer, optional): Viewport height in pixels.
- `full_page` (boolean, optional): Capture the full scrollable page. Default: `false`.
- `format` (string, optional): Image format, either `png` or `jpeg`. Default: `png`.
- `delay` (integer, optional): Delay in milliseconds before taking the screenshot.
- `device_scale_factor` (number, optional): Device scale factor (e.g., 2 for retina).
- `user_agent` (string, optional): Custom user agent string.
- `cookies` (array, optional): List of cookies to set. Each cookie is an object with `name`, `value`, and `domain`.
- `headers` (object, optional): Additional HTTP headers to set.
- `quality` (integer, optional): JPEG quality (0-100, only for `jpeg` format).
- `clip` (object, optional): Region to capture, with `x`, `y`, `width`, `height` (all numbers).
- `timeout` (integer, optional): Navigation timeout in milliseconds. Minimum: 100.
- `wait_until` (string, optional): When to consider navigation succeeded. One of `load`, `domcontentloaded`, `networkidle`, `networkidle2`. Default: `load`.
- `wait_for_selector` (string, optional): Wait for a selector before screenshot.
- `emulate` (object, optional): Emulation options, e.g., `{ "color_scheme": "dark" }`.
- `omit_background` (boolean, optional): Hide default white background. Default: `false`.
- `selector` (string, optional): CSS selector for a specific element to screenshot.
- `webhook_url` (string, optional): If provided, results are sent to this URL asynchronously.
- `id` (string, optional): Custom identifier for the request.
- `js` (string, optional): JavaScript code to inject into the page before taking the screenshot.
- `css` (string, optional): CSS code to inject into the page before taking the screenshot.

#### Example Request

```json
{
    "url": "https://example.com",
    "viewport_width": 1280,
    "viewport_height": 720,
    "js": "document.body.style.background = 'red';",
    "css": "body { font-size: 30px; }",
    "full_page": true,
    "format": "png",
    "delay": 500,
    "device_scale_factor": 2,
    "user_agent": "CustomAgent/1.0",
    "cookies": [
        {
            "name": "test_cookie",
            "value": "test_value",
            "domain": "example.com",
            "path": "/"
        }
    ],
    "headers": {
        "Accept-Language": "en-US,en;q=0.9"
    },
    "quality": 90,
    "clip": {
        "x": 0,
        "y": 0,
        "width": 800,
        "height": 600
    },
    "timeout": 10000,
    "wait_until": "networkidle",
    "wait_for_selector": "#main-content",
    "selector": "#main-content",
    "emulate": {
        "color_scheme": "dark"
    },
    "omit_background": true,
    "webhook_url": "https://your-webhook.com/callback",
    "id": "custom-job-123"
}
```

**cURL Example:**

```bash
curl -X POST \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "viewport_width": 1280,
    "viewport_height": 720,
    "js": "document.body.style.background = '\''red'\'';",
    "css": "body { font-size: 30px; }",
    "full_page": true,
    "format": "png",
    "delay": 500,
    "device_scale_factor": 2,
    "user_agent": "CustomAgent/1.0",
    "cookies": [
      {"name": "test_cookie", "value": "test_value", "domain": "example.com", "path": "/"}
    ],
    "headers": {"Accept-Language": "en-US,en;q=0.9"},
    "quality": 90,
    "clip": {"x": 0, "y": 0, "width": 800, "height": 600},
    "timeout": 10000,
    "wait_until": "networkidle",
    "wait_for_selector": "#main-content",
    "selector": "#main-content",
    "emulate": {"color_scheme": "dark"},
    "omit_background": true,
    "webhook_url": "https://your-webhook.com/callback",
    "id": "custom-job-123"
  }' \
  https://your-api-endpoint.com/v1/image/screenshot/webpage
```

## 4. Response

### Success Response

The response is a JSON object containing the cloud storage URL of the screenshot and job metadata. If a `webhook_url` is provided, the result is sent asynchronously to the webhook.

```json
{
  "endpoint": "/v1/image/screenshot/webpage",
  "code": 200,
  "id": "custom-job-123",
  "job_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
  "response": "https://cloud.example.com/screenshot.png",
  "message": "success",
  "pid": 12345,
  "queue_id": 140682639937472,
  "run_time": 2.345,
  "queue_time": 0.012,
  "total_time": 2.357,
  "queue_length": 0,
  "build_number": "1.0.0"
}
```

### Error Responses

- **400 Bad Request**: Invalid or missing parameters.
- **401 Unauthorized**: Invalid or missing API key.
- **429 Too Many Requests**: Queue is full.
- **500 Internal Server Error**: An error occurred during processing.

Example error response:

```json
{
  "endpoint": "/v1/image/screenshot/webpage",
  "code": 500,
  "id": "custom-job-123",
  "job_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
  "response": null,
  "message": "Error message details",
  "pid": 12345,
  "queue_id": 140682639937472,
  "run_time": 0.123,
  "queue_time": 0.056,
  "total_time": 0.179,
  "queue_length": 1,
  "build_number": "1.0.0"
}
```

## 5. Error Handling

- **Missing or invalid parameters**: Returns 400 with details.
- **Authentication failure**: Returns 401.
- **Queue full**: Returns 429.
- **Processing error**: Returns 500 with error message.

## 6. Usage Notes

- If `webhook_url` is provided, the request is processed asynchronously and the result is sent to the webhook.
- Screenshots are always uploaded to cloud storage; the response contains the file URL.
- Use `selector` to capture a specific element instead of the full page.
- The `clip` parameter allows capturing a specific region.
- The endpoint enforces strict payload validation.

## 7. Common Issues

- Invalid or inaccessible URL.
- Selector not found (if using `wait_for_selector` or `selector`).
- Cookie domain mismatch.
- Timeout errors for slow-loading pages.
- Invalid API key.

## 8. Best Practices

- Always validate your input parameters before sending the request.
- Use unique `id` values for tracking jobs.
- Monitor queue length and handle 429 errors gracefully.
- Use HTTPS for all URLs and webhooks.
- Test your selectors and page state locally before automating screenshots.
