# Media to MP3 Conversion Endpoint

## 1. Overview

The `/v1/media/transform/mp3` endpoint is a part of the API's media transformation functionality. It allows users to convert various media files (audio or video) to MP3 format. This endpoint fits into the overall API structure as a part of the `v1` namespace, which is dedicated to the first version of the API.

## 2. Endpoint

```
POST /v1/media/transform/mp3
```

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

- `media_url` (required, string): The URL of the media file to be converted.
- `webhook_url` (optional, string): The URL to receive a webhook notification upon completion.
- `id` (optional, string): A unique identifier for the request.
- `bitrate` (optional, string): The desired bitrate for the MP3 output, specified in the format `<value>k` (e.g., `128k`). If not provided, defaults to `128k`.

The `validate_payload` directive in the routes file enforces the following JSON schema for the request body:

```json
{
    "type": "object",
    "properties": {
        "media_url": {"type": "string", "format": "uri"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"},
        "bitrate": {"type": "string", "pattern": "^[0-9]+k$"}
    },
    "required": ["media_url"],
    "additionalProperties": False
}
```

### Example Request

```json
{
    "media_url": "https://example.com/video.mp4",
    "webhook_url": "https://example.com/webhook",
    "id": "unique-request-id",
    "bitrate": "192k"
}
```

```bash
curl -X POST \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"media_url": "https://example.com/video.mp4", "webhook_url": "https://example.com/webhook", "id": "unique-request-id", "bitrate": "192k"}' \
     https://your-api-endpoint.com/v1/media/transform/mp3
```

## 4. Response

### Success Response

Upon successful conversion, the endpoint returns a JSON response with the following structure:

```json
{
    "endpoint": "/v1/media/transform/mp3",
    "code": 200,
    "id": "unique-request-id",
    "job_id": "generated-job-id",
    "response": "https://cloud-storage.com/converted-file.mp3",
    "message": "success",
    "pid": 12345,
    "queue_id": 1234567890,
    "run_time": 5.123,
    "queue_time": 0.456,
    "total_time": 5.579,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

The `response` field contains the URL of the converted MP3 file uploaded to cloud storage.

### Error Responses

- **400 Bad Request**: Returned when the request payload is invalid or missing required parameters.
- **401 Unauthorized**: Returned when the `x-api-key` header is missing or invalid.
- **500 Internal Server Error**: Returned when an unexpected error occurs during the conversion process.

Example error response:

```json
{
    "code": 400,
    "message": "Invalid request payload: 'media_url' is a required property"
}
```

## 5. Error Handling

The endpoint handles the following common errors:

- Missing or invalid `media_url` parameter: Returns a 400 Bad Request error.
- Invalid `bitrate` parameter: Returns a 400 Bad Request error.
- Authentication failure: Returns a 401 Unauthorized error.
- Unexpected exceptions during the conversion process: Returns a 500 Internal Server Error error.

Additionally, the main application context (`app.py`) includes error handling for queue overload. If the maximum queue length is reached, the endpoint returns a 429 Too Many Requests error.

## 6. Usage Notes

- The `media_url` parameter should point to a valid media file (audio or video) that can be processed by the conversion service.
- The `webhook_url` parameter is optional and can be used to receive a notification when the conversion is complete.
- The `id` parameter is optional and can be used to associate the request with a specific identifier.
- The `bitrate` parameter is optional and defaults to `128k` if not provided.

## 7. Common Issues

- Providing an invalid or inaccessible `media_url`.
- Specifying an invalid `bitrate` value (e.g., not following the `<value>k` format).
- Reaching the maximum queue length, resulting in a 429 Too Many Requests error.

## 8. Best Practices

- Validate the `media_url` parameter before sending the request to ensure it points to a valid and accessible media file.
- Use the `id` parameter to associate requests with specific identifiers for better tracking and debugging.
- Consider providing a `webhook_url` to receive notifications about the conversion status and the resulting file URL.
- Monitor the queue length and adjust the `MAX_QUEUE_LENGTH` environment variable accordingly to prevent overloading the system.