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

The request body should be a JSON object with the following properties:

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
}'
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
- `total_time` (float): The total time taken to process the request, including queue time (in seconds).
- `queue_length` (integer): The current length of the processing queue.
- `build_number` (string): The build number of the application.

```json
{
    "code": 200,
    "id": "request-123",
    "job_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
    "response": "https://storage.example.com/captioned-video.mp4",
    "message": "success",
    "pid": 123,
    "queue_id": 140567495862272,
    "run_time": 5.234,
    "queue_time": 0.012,
    "total_time": 5.246,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

### Error Responses

#### 400 Bad Request

Returned when there is an issue with the request payload, such as missing or invalid parameters.

```json
{
    "code": 400,
    "id": "request-123",
    "job_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
    "message": "Invalid request payload",
    "pid": 123,
    "queue_id": 140567495862272,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

#### 400 Font Error

Returned when there is an issue with the requested font family.

```json
{
    "error": "The requested font family 'InvalidFont' is not available. Please choose from the available fonts.",
    "available_fonts": ["Arial", "Times New Roman", "Courier New", ...],
    "code": 400,
    "id": "request-123",
    "job_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
    "pid": 123,
    "queue_id": 140567495862272,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

#### 429 Too Many Requests

Returned when the processing queue has reached its maximum length.

```json
{
    "code": 429,
    "id": "request-123",
    "job_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
    "message": "MAX_QUEUE_LENGTH (100) reached",
    "pid": 123,
    "queue_id": 140567495862272,
    "queue_length": 100,
    "build_number": "1.0.0"
}
```

#### 500 Internal Server Error

Returned when an unexpected error occurs during the captioning process.

```json
{
    "code": 500,
    "id": "request-123",
    "job_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
    "message": "An unexpected error occurred during the captioning process.",
    "pid": 123,
    "queue_id": 140567495862272,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

## 5. Error Handling

The endpoint handles the following common errors:

- **Missing or invalid parameters**: If any required parameters are missing or invalid, a 400 Bad Request error is returned.
- **Font error**: If the requested font family is not available, a 400 Bad Request error is returned, along with a list of available fonts.
- **Queue limit reached**: If the processing queue has reached its maximum length (determined by the `MAX_QUEUE_LENGTH` environment variable), a 429 Too Many Requests error is returned.
- **Unexpected errors**: If an unexpected error occurs during the captioning process, a 500 Internal Server Error is returned.

## 6. Usage Notes

- The `video_url` parameter is required, and it should be a valid URL pointing to a video file.
- The `captions` parameter is optional. If not provided, the video will be processed without captions.
- The `settings` parameter allows you to customize the appearance and behavior of the captions. Refer to the settings schema for available options.
- The `replace` parameter allows you to specify text replacements to be made in the captions.
- The `webhook_url` parameter is optional. If provided, a webhook notification will be sent to the specified URL when the captioning process is complete.
- The `id` parameter is optional and can be used to identify the request.
- The `language` parameter is optional and specifies the language of the captions. If not provided, the language will be automatically detected.

## 7. Common Issues

- **Invalid video URL**: Ensure that the `video_url` parameter points to a valid and accessible video file.
- **Unsupported video format**: The captioning process may not support certain video formats. If you encounter issues, try converting the video to a more common format like MP4 or AVI.
- **Font availability**: The captioning process may not have access to certain font families. If you encounter a font error, choose from the list of available fonts provided in the error response.

## 8. Best Practices

- **Validate input**: Always validate the input parameters to ensure they meet the expected format and requirements.
- **Use webhooks**: Utilize the `webhook_url` parameter to receive notifications when the captioning process is complete, rather than polling for the result.
- **Optimize settings**: Adjust the caption settings based on the video resolution and content to ensure readability and aesthetics.
- **Test locally**: Before deploying to production, test the captioning process locally with various video files and settings to identify and resolve any issues.