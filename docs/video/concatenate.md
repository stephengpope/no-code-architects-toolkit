# Video Concatenation Endpoint

## 1. Overview

The `/v1/video/concatenate` endpoint is part of the Video API and is responsible for combining multiple video files into a single video file. This endpoint fits into the overall API structure by providing a way to concatenate videos, which can be useful in various scenarios, such as creating video compilations or combining multiple video segments into a single file.

## 2. Endpoint

**URL Path:** `/v1/video/concatenate`
**HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body must be a JSON object with the following properties:

- `video_urls` (required, array of objects): An array of video URLs to be concatenated. Each object in the array must have a `video_url` property (string, URI format) containing the URL of the video file.
- `webhook_url` (optional, string, URI format): The URL to receive a webhook notification when the video concatenation process is complete.
- `id` (optional, string): A unique identifier for the request.

The `validate_payload` decorator in the route file enforces the following JSON schema for the request body:

```json
{
    "type": "object",
    "properties": {
        "video_urls": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "video_url": {"type": "string", "format": "uri"}
                },
                "required": ["video_url"]
            },
            "minItems": 1
        },
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["video_urls"],
    "additionalProperties": False
}
```

### Example Request

```json
{
    "video_urls": [
        {"video_url": "https://example.com/video1.mp4"},
        {"video_url": "https://example.com/video2.mp4"},
        {"video_url": "https://example.com/video3.mp4"}
    ],
    "webhook_url": "https://example.com/webhook",
    "id": "unique-request-id"
}
```

```bash
curl -X POST \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
        "video_urls": [
            {"video_url": "https://example.com/video1.mp4"},
            {"video_url": "https://example.com/video2.mp4"},
            {"video_url": "https://example.com/video3.mp4"}
        ],
        "webhook_url": "https://example.com/webhook",
        "id": "unique-request-id"
     }' \
     https://your-api-endpoint.com/v1/video/concatenate
```

## 4. Response

### Success Response

The success response follows the general response format defined in the `app.py` file. Here's an example:

```json
{
    "endpoint": "/v1/video/concatenate",
    "code": 200,
    "id": "unique-request-id",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "response": "https://cloud-storage.com/combined-video.mp4",
    "message": "success",
    "pid": 12345,
    "queue_id": 67890,
    "run_time": 10.234,
    "queue_time": 2.345,
    "total_time": 12.579,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

The `response` field contains the URL of the combined video file uploaded to cloud storage.

### Error Responses

- **400 Bad Request**: Returned when the request body is missing or invalid.
- **401 Unauthorized**: Returned when the `x-api-key` header is missing or invalid.
- **429 Too Many Requests**: Returned when the maximum queue length is reached (if configured).
- **500 Internal Server Error**: Returned when an unexpected error occurs during the video concatenation process.

Example error response:

```json
{
    "code": 400,
    "id": "unique-request-id",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "message": "Invalid request payload: 'video_urls' is a required property",
    "pid": 12345,
    "queue_id": 67890,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

## 5. Error Handling

The endpoint handles the following common errors:

- Missing or invalid request parameters: Returns a 400 Bad Request error with a descriptive error message.
- Authentication failure: Returns a 401 Unauthorized error if the `x-api-key` header is missing or invalid.
- Queue length exceeded: Returns a 429 Too Many Requests error if the maximum queue length is reached (if configured).
- Unexpected exceptions during video concatenation: Returns a 500 Internal Server Error with the exception message.

The main application context (`app.py`) also includes error handling for queue-related errors, such as reaching the maximum queue length.

## 6. Usage Notes

- The order of the video files in the `video_urls` array determines the order in which they will be concatenated.
- The endpoint supports various video file formats, but the specific supported formats may depend on the underlying video processing library (e.g., FFmpeg).
- The combined video file will be uploaded to cloud storage, and the response will include the URL of the uploaded file.
- If a `webhook_url` is provided, a webhook notification will be sent to that URL when the video concatenation process is complete.

## 7. Common Issues

- Providing invalid or inaccessible video URLs in the `video_urls` array.
- Exceeding the maximum queue length, if configured, which can result in a 429 Too Many Requests error.
- Encountering issues during the video concatenation process, such as unsupported video formats or corrupted video files.

## 8. Best Practices

- Validate the video URLs before sending the request to ensure they are accessible and in a supported format.
- Monitor the queue length and adjust the maximum queue length as needed to prevent overloading the system.
- Implement retry mechanisms for failed requests or consider using a message queue system for better reliability and scalability.
- Implement proper error handling and logging to aid in troubleshooting and monitoring.
- Consider implementing rate limiting or throttling mechanisms to prevent abuse or excessive load on the system.