# Video Captioning Endpoint (v1)

## 1. Overview

The `/v1/video/caption` endpoint is part of the Video API and is responsible for adding captions to a video file. It accepts a video URL, caption text, and various styling options for the captions. The endpoint utilizes the `process_captioning_v1` service to generate a captioned video file, which is then uploaded to cloud storage, and the cloud URL is returned in the response.

## 2. Endpoint

**URL:** `/v1/video/caption`
**Method:** `POST`

## 3. Request

### Headers

- `x-api-key`: Required. The API key for authentication.

### Body Parameters

The request body must be a JSON object with the following properties:

- `video_url` (string, required): The URL of the video file to be captioned.
- `captions` (string, optional): The caption text to be added to the video.
- `settings` (object, optional): An object containing various styling options for the captions. See the schema below for available options.
- `replace` (array, optional): An array of objects with `find` and `replace` properties, specifying text replacements to be made in the captions.
- `webhook_url` (string, optional): A URL to receive a webhook notification when the captioning process is complete.
- `id` (string, optional): An identifier for the request.
- `language` (string, optional): The language code for the captions (e.g., "en", "fr"). Defaults to "auto".

#### Settings Schema

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
    "additionalProperties": false
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
        "bold": false,
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
    "id": "request-123",
    "language": "en"
}
```

```bash
curl -X POST \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
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
            "bold": false,
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
        "id": "request-123",
        "language": "en"
    }' \
    https://your-api-endpoint.com/v1/video/caption
```

## 4. Response

### Success Response

The response will be a JSON object with the following properties:

- `code` (integer): The HTTP status code (200 for success).
- `id` (string): The request identifier, if provided in the request.
- `job_id` (string): A unique identifier for the job.
- `response` (string): The cloud URL of the captioned video file.
- `message` (string): A success message.
- `pid` (integer): The process ID of the worker that processed the request.
- `queue_id` (integer): The ID of the queue used for processing the request.
- `run_time` (float): The time taken to process the request (in seconds).
- `queue_time` (float): The time the request spent in the queue (in seconds).
- `total_time` (float): The total time taken for the request (in seconds).
- `queue_length` (integer): The current length of the processing queue.
- `build_number` (string): The build number of the application.

Example:

```json
{
    "code": 200,
    "id": "request-123",
    "job_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
    "response": "https://cloud.example.com/captioned-video.mp4",
    "message": "success",
    "pid": 12345,
    "queue_id": 140682639937472,
    "run_time": 5.234,
    "queue_time": 0.012,
    "total_time": 5.246,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

### Error Responses

#### Missing or Invalid Parameters

**Status Code:** 400 Bad Request

```json
{
    "code": 400,
    "id": "request-123",
    "job_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
    "message": "Missing or invalid parameters",
    "pid": 12345,
    "queue_id": 140682639937472,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

#### Font Error

**Status Code:** 400 Bad Request

```json
{
    "code": 400,
    "error": "The requested font 'InvalidFont' is not available. Please choose from the available fonts.",
    "available_fonts": ["Arial", "Times New Roman", "Courier New", ...],
    "pid": 12345,
    "queue_id": 140682639937472,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

#### Internal Server Error

**Status Code:** 500 Internal Server Error

```json
{
    "code": 500,
    "id": "request-123",
    "job_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
    "error": "An unexpected error occurred during the captioning process.",
    "pid": 12345,
    "queue_id": 140682639937472,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

## 5. Error Handling

The endpoint handles the following common errors:

- **Missing or Invalid Parameters**: If any required parameters are missing or invalid, a 400 Bad Request error is returned with a descriptive error message.
- **Font Error**: If the requested font is not available, a 400 Bad Request error is returned with a list of available fonts.
- **Internal Server Error**: If an unexpected error occurs during the captioning process, a 500 Internal Server Error is returned with an error message.

Additionally, the main application context (`app.py`) includes error handling for queue overload. If the maximum queue length (`MAX_QUEUE_LENGTH`) is set and the queue size reaches that limit, a 429 Too Many Requests error is returned with a descriptive message.

## 6. Usage Notes

- The `video_url` parameter must be a valid URL pointing to a video file.
- The `captions` parameter is optional. If not provided, the video will be returned without captions.
- The `settings` parameter allows for customization of the caption appearance and behavior.
- The `replace` parameter can be used to perform text replacements in the captions.
- The `webhook_url` parameter is optional and can be used to receive a notification when the captioning process is complete.
- The `id` parameter is optional and can be used to identify the request.
- The `language` parameter is optional and can be used to specify the language of the captions. If not provided, the language will be automatically detected.

## 7. Common Issues

- Providing an invalid or inaccessible `video_url`.
- Requesting an unavailable font in the `settings` object.
- Exceeding the maximum queue length, resulting in a 429 Too Many Requests error.

## 8. Best Practices

- Validate the `video_url` parameter before sending the request to ensure it points to a valid and accessible video file.
- Use the `webhook_url` parameter to receive notifications about the captioning process, rather than polling the API for updates.
- Provide descriptive and meaningful `id` values to easily identify requests in logs and responses.
- Use the `replace` parameter judiciously to avoid unintended text replacements in the captions.
- Consider caching the captioned video files for frequently requested videos to improve performance and reduce processing time.