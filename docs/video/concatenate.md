# Video Concatenation Endpoint

## 1. Overview

The `/v1/video/concatenate` endpoint is a part of the Video API and is responsible for combining multiple video files into a single video file. This endpoint fits into the overall API structure as a part of the version 1 (v1) routes, specifically under the `/v1/video` namespace.

## 2. Endpoint

**URL Path:** `/v1/video/concatenate`
**HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body must be a JSON object with the following properties:

- `video_urls` (required, array of objects): An array of video URLs to be concatenated. Each object in the array must have a `video_url` property (string, URI format) containing the URL of the video file.
- `webhook_url` (optional, string, URI format): The URL to which the response should be sent as a webhook.
- `id` (optional, string): An identifier for the request.

The `validate_payload` decorator in the routes file enforces the following JSON schema for the request body:

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
    "id": "request-123"
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
        "id": "request-123"
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
    "id": "request-123",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "response": "https://cloud-storage.example.com/combined-video.mp4",
    "message": "success",
    "pid": 12345,
    "queue_id": 6789,
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

  ```json
  {
    "code": 400,
    "message": "Invalid request payload"
  }
  ```

- **401 Unauthorized**: Returned when the `x-api-key` header is missing or invalid.

  ```json
  {
    "code": 401,
    "message": "Unauthorized"
  }
  ```

- **429 Too Many Requests**: Returned when the maximum queue length is reached.

  ```json
  {
    "code": 429,
    "id": "request-123",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "message": "MAX_QUEUE_LENGTH (100) reached",
    "pid": 12345,
    "queue_id": 6789,
    "queue_length": 100,
    "build_number": "1.0.0"
  }
  ```

- **500 Internal Server Error**: Returned when an unexpected error occurs during the video concatenation process.

  ```json
  {
    "code": 500,
    "message": "An error occurred during video concatenation"
  }
  ```

## 5. Error Handling

The endpoint handles the following common errors:

- **Missing or invalid request body**: If the request body is missing or does not conform to the expected JSON schema, a 400 Bad Request error is returned.
- **Missing or invalid API key**: If the `x-api-key` header is missing or invalid, a 401 Unauthorized error is returned.
- **Queue length exceeded**: If the maximum queue length is reached (determined by the `MAX_QUEUE_LENGTH` environment variable), a 429 Too Many Requests error is returned.
- **Unexpected errors during video concatenation**: If an unexpected error occurs during the video concatenation process, a 500 Internal Server Error is returned with the error message.

The main application context (`app.py`) also includes error handling for the task queue. If the queue length exceeds the `MAX_QUEUE_LENGTH` limit, the request is rejected with a 429 Too Many Requests error.

## 6. Usage Notes

- The video files to be concatenated must be accessible via the provided URLs.
- The order of the video files in the `video_urls` array determines the order in which they will be concatenated.
- If the `webhook_url` parameter is provided, the response will be sent as a webhook to the specified URL.
- The `id` parameter can be used to identify the request in the response.

## 7. Common Issues

- Providing invalid or inaccessible video URLs.
- Exceeding the maximum queue length, which can lead to requests being rejected with a 429 Too Many Requests error.
- Encountering unexpected errors during the video concatenation process, which can result in a 500 Internal Server Error.

## 8. Best Practices

- Validate the video URLs before sending the request to ensure they are accessible and in the correct format.
- Monitor the queue length and adjust the `MAX_QUEUE_LENGTH` value accordingly to prevent requests from being rejected due to a full queue.
- Implement retry mechanisms for handling temporary errors or failures during the video concatenation process.
- Provide meaningful and descriptive `id` values to easily identify requests in the response.