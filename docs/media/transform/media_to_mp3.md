# Media to MP3 Conversion Endpoint

## 1. Overview

The `/v1/media/transform/mp3` endpoint is a part of the API's media transformation functionality. It allows users to convert various media files (audio or video) to MP3 format. This endpoint fits into the overall API structure as a part of the `v1` namespace, specifically under the `media/transform` category.

## 2. Endpoint

```
POST /v1/media/transform/mp3
```

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body must be in JSON format and should include the following parameters:

- `media_url` (required, string): The URL of the media file to be converted.
- `webhook_url` (optional, string): The URL to receive a webhook notification upon completion.
- `id` (optional, string): A unique identifier for the request.
- `bitrate` (optional, string): The desired bitrate for the output MP3 file, specified in the format `<value>k` (e.g., `128k`). If not provided, the default bitrate of `128k` will be used.

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
  https://api.example.com/v1/media/transform/mp3 \
  -H 'x-api-key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "media_url": "https://example.com/video.mp4",
    "webhook_url": "https://example.com/webhook",
    "id": "unique-request-id",
    "bitrate": "192k"
  }'
```

## 4. Response

### Success Response

**Status Code:** 200 OK

```json
{
  "code": 200,
  "id": "unique-request-id",
  "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "response": "https://cloud.example.com/converted.mp3",
  "message": "success",
  "run_time": 12.345,
  "queue_time": 0.123,
  "total_time": 12.468,
  "pid": 12345,
  "queue_id": 1234567890,
  "queue_length": 0,
  "build_number": "1.0.0"
}
```

The `response` field contains the URL of the converted MP3 file uploaded to cloud storage.

### Error Responses

**Status Code:** 400 Bad Request

```json
{
  "code": 400,
  "id": "unique-request-id",
  "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "message": "Invalid request payload",
  "pid": 12345,
  "queue_id": 1234567890,
  "queue_length": 0,
  "build_number": "1.0.0"
}
```

**Status Code:** 401 Unauthorized

```json
{
  "code": 401,
  "id": "unique-request-id",
  "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "message": "Missing or invalid API key",
  "pid": 12345,
  "queue_id": 1234567890,
  "queue_length": 0,
  "build_number": "1.0.0"
}
```

**Status Code:** 500 Internal Server Error

```json
{
  "code": 500,
  "id": "unique-request-id",
  "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "message": "An error occurred during media conversion",
  "pid": 12345,
  "queue_id": 1234567890,
  "queue_length": 0,
  "build_number": "1.0.0"
}
```

## 5. Error Handling

- **Missing or Invalid Parameters**: If the required `media_url` parameter is missing or invalid, or if any other provided parameters are invalid, the endpoint will return a 400 Bad Request error.
- **Authentication Error**: If the `x-api-key` header is missing or invalid, the endpoint will return a 401 Unauthorized error.
- **Internal Server Error**: If an unexpected error occurs during the media conversion process, the endpoint will return a 500 Internal Server Error.
- **Queue Limit Reached**: If the maximum queue length (`MAX_QUEUE_LENGTH`) is set and the task queue has reached its limit, the endpoint will return a 429 Too Many Requests error.

## 6. Usage Notes

- The `media_url` parameter should point to a valid media file (audio or video) that can be converted to MP3 format.
- If the `webhook_url` parameter is provided, a webhook notification will be sent to the specified URL upon completion of the conversion process.
- The `id` parameter can be used to uniquely identify the request, which can be helpful for tracking and logging purposes.
- The `bitrate` parameter allows you to specify the desired bitrate for the output MP3 file. If not provided, the default bitrate of `128k` will be used.

## 7. Common Issues

- Providing an invalid or inaccessible `media_url`.
- Attempting to convert unsupported media formats.
- Providing an invalid `bitrate` value (e.g., not following the `<value>k` format).

## 8. Best Practices

- Always provide a valid `x-api-key` header for authentication.
- Consider using the `webhook_url` parameter to receive notifications about the conversion process completion.
- Ensure that the provided `media_url` is accessible and points to a valid media file.
- If you need to convert multiple media files, consider using a queue or batch processing approach to avoid overwhelming the server with too many concurrent requests.