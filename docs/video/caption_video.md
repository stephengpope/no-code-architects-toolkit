# Video Captioning Endpoint (v1)

## 1. Overview

The `/v1/video/caption` endpoint is part of the Video API in version 1 of the application. It allows users to add captions to a video file, with various customization options for the caption appearance and behavior. This endpoint utilizes the enhanced `process_captioning_v1` service, which provides more advanced captioning capabilities compared to the previous version.

## 2. Endpoint

```
POST /v1/video/caption
```

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body should be a JSON object with the following properties:

- `video_url` (required, string): The URL of the video file to be captioned.
- `captions` (optional, string): The caption text to be added to the video.
- `settings` (optional, object): An object containing various settings for customizing the caption appearance and behavior. See the schema below for available options.
- `replace` (optional, array): An array of objects with `find` and `replace` properties, specifying text replacements to be made in the captions.
- `webhook_url` (optional, string): The URL to receive a webhook notification when the captioning process is complete.
- `id` (optional, string): A unique identifier for the request.
- `language` (optional, string): The language code for the captions (e.g., 'en', 'fr'). Defaults to 'auto'.

The `settings` object has the following schema:

```json
{
    "type": "object",
    "properties": {
        "line_color": {"type": "string"},
        "word_color": {"type": "string"},
        "outline_color": {"type": "string"},
        "all_caps": {"type": "boolean"},
        "max_words_per_line": {"type": "integer"},
        "x": {"type": "integer"},
        "y": {"type": "integer"},
        "position": {
            "type": "string",
            "enum": [
                "bottom_left", "bottom_center", "bottom_right",
                "middle_left", "middle_center", "middle_right",
                "top_left", "top_center", "top_right"
            ]
        },
        "alignment": {
            "type": "string",
            "enum": ["left", "center", "right"]
        },
        "font_family": {"type": "string"},
        "font_size": {"type": "integer"},
        "bold": {"type": "boolean"},
        "italic": {"type": "boolean"},
        "underline": {"type": "boolean"},
        "strikeout": {"type": "boolean"},
        "style": {
            "type": "string",
            "enum": ["classic", "karaoke", "highlight", "underline", "word_by_word"]
        },
        "outline_width": {"type": "integer"},
        "spacing": {"type": "integer"},
        "angle": {"type": "integer"},
        "shadow_offset": {"type": "integer"}
    },
    "additionalProperties": False
}
```

### Example Request

```json
{
    "video_url": "https://example.com/video.mp4",
    "captions": "This is a sample caption text.",
    "settings": {
        "line_color": "#FFFFFF",
        "word_color": "#000000",
        "outline_color": "#000000",
        "all_caps": false,
        "max_words_per_line": 10,
        "x": 20,
        "y": 40,
        "position": "bottom_left",
        "alignment": "left",
        "font_family": "Arial",
        "font_size": 24,
        "bold": true,
        "italic": false,
        "underline": false,
        "strikeout": false,
        "style": "classic",
        "outline_width": 2,
        "spacing": 2,
        "angle": 0,
        "shadow_offset": 2
    },
    "replace": [
        {
            "find": "sample",
            "replace": "example"
        }
    ],
    "webhook_url": "https://example.com/webhook",
    "id": "unique-request-id",
    "language": "en"
}
```

```bash
curl -X POST \
  https://api.example.com/v1/video/caption \
  -H 'x-api-key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "video_url": "https://example.com/video.mp4",
    "captions": "This is a sample caption text.",
    "settings": {
        "line_color": "#FFFFFF",
        "word_color": "#000000",
        "outline_color": "#000000",
        "all_caps": false,
        "max_words_per_line": 10,
        "x": 20,
        "y": 40,
        "position": "bottom_left",
        "alignment": "left",
        "font_family": "Arial",
        "font_size": 24,
        "bold": true,
        "italic": false,
        "underline": false,
        "strikeout": false,
        "style": "classic",
        "outline_width": 2,
        "spacing": 2,
        "angle": 0,
        "shadow_offset": 2
    },
    "replace": [
        {
            "find": "sample",
            "replace": "example"
        }
    ],
    "webhook_url": "https://example.com/webhook",
    "id": "unique-request-id",
    "language": "en"
}'
```

## 4. Response

### Success Response

**Status Code:** 200 OK

```json
{
    "response": "https://cloud.example.com/captioned-video.mp4",
    "endpoint": "/v1/video/caption",
    "code": 200,
    "id": "unique-request-id",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "message": "success",
    "pid": 12345,
    "queue_id": 6789,
    "run_time": 5.234,
    "queue_time": 0.123,
    "total_time": 5.357,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

The response contains the URL of the captioned video file uploaded to cloud storage.

### Error Responses

**Status Code:** 400 Bad Request

```json
{
    "error": "Invalid video URL",
    "endpoint": "/v1/video/caption",
    "code": 400,
    "id": "unique-request-id",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "message": "Invalid video URL",
    "pid": 12345,
    "queue_id": 6789,
    "run_time": 0.001,
    "queue_time": 0.0,
    "total_time": 0.001,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

**Status Code:** 400 Bad Request (Font Error)

```json
{
    "error": "Font 'CustomFont' is not available. Please choose from the available fonts.",
    "available_fonts": ["Arial", "Times New Roman", "Courier New", ...],
    "endpoint": "/v1/video/caption",
    "code": 400,
    "id": "unique-request-id",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "message": "Font 'CustomFont' is not available. Please choose from the available fonts.",
    "pid": 12345,
    "queue_id": 6789,
    "run_time": 0.001,
    "queue_time": 0.0,
    "total_time": 0.001,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

**Status Code:** 500 Internal Server Error

```json
{
    "error": "An unexpected error occurred during captioning process.",
    "endpoint": "/v1/video/caption",
    "code": 500,
    "id": "unique-request-id",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "message": "An unexpected error occurred during captioning process.",
    "pid": 12345,
    "queue_id": 6789,
    "run_time": 0.001,
    "queue_time": 0.0,
    "total_time": 0.001,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

## 5. Error Handling

The endpoint handles the following common errors:

- **Missing or invalid parameters**: If required parameters are missing or have an invalid format, a 400 Bad Request error is returned with an appropriate error message.
- **Font errors**: If the specified font is not available, a 400 Bad Request error is returned with a list of available fonts.
- **Unexpected errors**: If an unexpected error occurs during the captioning process, a 500 Internal Server Error is returned with a generic error message.

Additionally, the main application context (`app.py`) includes error handling for queue overload. If the maximum queue length (`MAX_QUEUE_LENGTH`) is set and the queue size reaches that limit, a 429 Too Many Requests error is returned with a message indicating that the queue is full.

## 6. Usage Notes

- The `video_url` parameter is required, and it should be a valid URL pointing to a video file.
- The `captions` parameter is optional. If not provided, the video will be processed without captions.
- The `settings` parameter allows customizing various aspects of the caption appearance and behavior. Refer to the schema for available options.
- The `replace` parameter allows specifying text replacements to be made in the captions.
- The `webhook_url` parameter is optional. If provided, a webhook notification will be sent to the specified URL when the captioning process is complete.
- The `id` parameter is optional and can be used to uniquely identify the request.
- The `language` parameter is optional and specifies the language code for the captions. If not provided, it defaults to 'auto'.

## 7. Common Issues

- Providing an invalid or inaccessible `video_url`.
- Specifying invalid or unsupported values for the `settings` parameters.
- Requesting an unavailable font family.
- Exceeding the maximum queue length, if set.

## 8. Best Practices

- Validate the `video_url` parameter before sending the request to ensure it points to a valid and accessible video file.
- Test the caption settings with sample videos to ensure the desired appearance and behavior.
- Use the `replace` parameter judiciously to avoid unintended text replacements in the captions.
- Monitor the queue length and adjust the `MAX_QUEUE_LENGTH` setting as needed to prevent queue overload.
- Implement error handling and retry mechanisms in your client application to handle potential errors and failures.