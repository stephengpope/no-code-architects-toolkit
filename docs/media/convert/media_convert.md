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

If a webhook URL is provided, the API will queue the task and return an immediate 202 Accepted response:

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

### Success Response (Webhook or Direct)

When the conversion is complete, the following response will be sent to the webhook URL (if provided) or returned directly (if no webhook URL):

```json
{
  "endpoint": "/v1/media/convert",
  "code": 200,
  "id": "custom-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": {
    "file_url": "https://storage.example.com/converted-file-123.webm"
  },
  "message": "success",
  "pid": 12345,
  "queue_id": 67890,
  "run_time": 5.234,
  "queue_time": 1.123,
  "total_time": 6.357,
  "queue_length": 2,
  "build_number": "1.0.0"
}
```

### Error Responses

#### Invalid Request (400 Bad Request)

```json
{
  "code": 400,
  "error": "Invalid request payload",
  "details": "Required field 'media_url' is missing"
}
```

#### Authentication Error (401 Unauthorized)

```json
{
  "code": 401,
  "error": "Authentication failed",
  "message": "Invalid or missing API key"
}
```

#### Queue Full (429 Too Many Requests)

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

#### Processing Error (500 Internal Server Error)

```json
{
  "endpoint": "/v1/media/convert",
  "code": 500,
  "id": "custom-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": null,
  "message": "Error downloading media file: Connection timeout",
  "pid": 12345,
  "queue_id": 67890,
  "run_time": 2.345,
  "queue_time": 0.567,
  "total_time": 2.912,
  "queue_length": 5,
  "build_number": "1.0.0"
}
```

## 5. Error Handling

The endpoint handles several types of errors:

- **Validation Errors (400)**: Occur when the request payload doesn't match the required schema (missing required fields, invalid formats, or additional properties).
- **Authentication Errors (401)**: Occur when the API key is invalid or missing.
- **Queue Limit Errors (429)**: Occur when the processing queue is full (if MAX_QUEUE_LENGTH is set).
- **Processing Errors (500)**: Occur during the media conversion process, such as:
  - Invalid media URL
  - Unsupported format
  - Media download failures
  - Conversion process failures
  - Cloud storage upload failures

All errors include descriptive messages to help diagnose the issue.

## 6. Usage Notes

- The conversion process is queued by default, making it suitable for handling larger files without blocking.
- When providing a `webhook_url`, you'll receive an immediate 202 response, and the final result will be sent to your webhook when processing completes.
- Without a `webhook_url`, the request will still be queued but the response will be held until processing completes.
- Using `"video_codec": "copy"` and `"audio_codec": "copy"` (the defaults) will attempt to copy the streams without re-encoding, which is faster but may not be compatible with all format conversions.
- The converted file is automatically uploaded to cloud storage, and the URL is provided in the response.

## 7. Common Issues

- **Unsupported Format Combinations**: Not all format and codec combinations are valid. For example, using an MP3 audio codec with a WebM container may fail.
- **Large File Timeouts**: Very large files may time out during download or upload. Consider using more direct file transfer methods for extremely large files.
- **Webhook Failures**: If your webhook endpoint is unavailable when the conversion completes, you may not receive the completion notification.
- **Queue Congestion**: During high load periods, the queue may fill up, resulting in 429 responses.
- **Invalid Media URLs**: The media URL must be directly accessible by the server. URLs requiring authentication or session cookies may fail.

## 8. Best Practices

- **Use Appropriate Codecs**: Only specify custom codecs if you have specific requirements. Using `"copy"` is faster and maintains quality.
- **Include an ID**: Always include a unique `id` in your requests to help track and identify them, especially when using webhooks.
- **Webhook Reliability**: Ensure your webhook endpoint is reliable and can handle the response payload. Implement retry logic on your webhook receiver.
- **Format Selection**: Choose the output format based on your target platform requirements. For web use, WebM or MP4 are generally recommended.
- **Monitor Queue Length**: If you're making many requests, monitor the `queue_length` in responses to avoid hitting queue limits.
- **Handle Errors Gracefully**: Implement proper error handling in your application to deal with potential conversion failures.