# Media Convert API Endpoint Documentation

## 1. Overview

The `/v1/media/convert` endpoint provides a service for converting media files from one format to another. It allows users to specify the desired output format and optionally set video and audio codecs. This endpoint is part of the v1 API structure and integrates with the application's queuing system to handle potentially resource-intensive conversion tasks asynchronously.

The endpoint fits into the overall API structure as one of several media processing services, registered in the main application as the `v1_media_convert_bp` blueprint.

## 2. Endpoint

- **URL**: `/v1/media/convert`
- **Method**: `POST`

## 3. Request

### Headers

- `x-api-key`: Required. Your API authentication key.

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `media_url` | string | Yes | URL of the media file to convert (must be a valid URI) |
| `format` | string | Yes | Desired output format (e.g., "mp4", "webm", "mov") |
| `video_codec` | string | No | Video codec to use (defaults to "copy") |
| `audio_codec` | string | No | Audio codec to use (defaults to "copy") |
| `webhook_url` | string | No | URL to receive conversion completion notification (must be a valid URI) |
| `id` | string | No | Custom identifier for tracking the request |

### Example Request

```json
{
  "media_url": "https://example.com/input-video.mp4",
  "format": "webm",
  "video_codec": "vp9",
  "audio_codec": "opus",
  "webhook_url": "https://your-server.com/webhook",
  "id": "custom-request-123"
}
```

### Example cURL Command

```bash
curl -X POST https://api.example.com/v1/media/convert \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -d '{
    "media_url": "https://example.com/input-video.mp4",
    "format": "webm",
    "video_codec": "vp9",
    "audio_codec": "opus",
    "webhook_url": "https://your-server.com/webhook",
    "id": "custom-request-123"
  }'
```

## 4. Response

### Success Response (Immediate)

When a webhook URL is provided, the API will queue the task and return an immediate 202 Accepted response:

```json
{
  "code": 202,
  "id": "custom-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "processing",
  "pid": 12345,
  "queue_id": 67890,
  "max_queue_length": "unlimited",
  "queue_length": 3,
  "build_number": "1.0.0"
}
```

### Success Response (Webhook)

When the conversion is complete, a webhook will be sent to the provided URL with the following data:

```json
{
  "endpoint": "/v1/media/convert",
  "code": 200,
  "id": "custom-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": {
    "file_url": "https://storage.example.com/converted-file-550e8400.webm"
  },
  "message": "success",
  "pid": 12345,
  "queue_id": 67890,
  "run_time": 5.321,
  "queue_time": 1.234,
  "total_time": 6.555,
  "queue_length": 2,
  "build_number": "1.0.0"
}
```

### Success Response (Synchronous)

When no webhook URL is provided, the API will process the request synchronously and return:

```json
{
  "code": 200,
  "id": "custom-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": {
    "file_url": "https://storage.example.com/converted-file-550e8400.webm"
  },
  "message": "success",
  "run_time": 5.321,
  "queue_time": 0,
  "total_time": 5.321,
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 2,
  "build_number": "1.0.0"
}
```

### Error Responses

#### 400 Bad Request

```json
{
  "code": 400,
  "error": "Invalid request payload",
  "details": "Required field 'media_url' is missing"
}
```

#### 401 Unauthorized

```json
{
  "code": 401,
  "error": "Authentication failed",
  "message": "Invalid or missing API key"
}
```

#### 429 Too Many Requests

```json
{
  "code": 429,
  "id": "custom-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "MAX_QUEUE_LENGTH (100) reached",
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 100,
  "build_number": "1.0.0"
}
```

#### 500 Internal Server Error

```json
{
  "code": 500,
  "id": "custom-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Failed to download media from provided URL",
  "pid": 12345,
  "queue_id": 67890,
  "build_number": "1.0.0"
}
```

## 5. Error Handling

- **Missing Required Parameters**: If `media_url` or `format` is missing, the API will return a 400 Bad Request error.
- **Invalid URI Format**: If `media_url` or `webhook_url` is not a valid URI, a 400 Bad Request error will be returned.
- **Authentication Failure**: If the API key is invalid or missing, a 401 Unauthorized error will be returned.
- **Queue Limit Reached**: If the queue is full (when MAX_QUEUE_LENGTH is set), a 429 Too Many Requests error will be returned.
- **Media Processing Errors**: If there are issues during the conversion process (e.g., invalid media file, unsupported format), a 500 Internal Server Error will be returned with details in the error message.

## 6. Usage Notes

- The default behavior for both video and audio codecs is "copy", which preserves the original streams without re-encoding, resulting in faster processing.
- When specifying codecs, ensure they are compatible with the output format to avoid conversion errors.
- For large media files, it's recommended to use the webhook approach to avoid timeout issues.
- The converted file is automatically uploaded to cloud storage, and the URL is provided in the response.

## 7. Common Issues

- **Inaccessible Media URL**: Ensure the `media_url` is publicly accessible or has proper authentication.
- **Incompatible Codec and Format**: Some codecs are not compatible with certain formats. For example, VP9 video codec is not compatible with MP4 containers.
- **Webhook Failures**: If the webhook URL is unreachable, the system will not retry sending the notification.
- **Large File Timeouts**: Very large files may cause timeouts during download or upload. Consider using pre-signed URLs for direct cloud-to-cloud transfers.

## 8. Best Practices

- Always provide a `webhook_url` for processing large media files to avoid HTTP timeout issues.
- Include a unique `id` in your requests to help track and identify conversions in your application.
- Use the most appropriate codec for your target format to optimize quality and file size.
- Monitor the queue length in responses to understand system load and adjust request timing if needed.
- For simple format changes without re-encoding, keep the default "copy" codecs to speed up processing.
- Test with small files first to ensure your format and codec combinations work as expected.