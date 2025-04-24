# Video Thumbnail Generation API

## Overview

The `/v1/video/thumbnail` endpoint allows users to extract a thumbnail image from a specific timestamp in a video. This endpoint is part of the video processing capabilities of the API, which includes other features like video concatenation and captioning. The endpoint processes the request asynchronously using a queue system, uploads the generated thumbnail to cloud storage, and returns the URL of the uploaded image.

## Endpoint

- **URL**: `/v1/video/thumbnail`
- **Method**: `POST`

## Request

### Headers

- `x-api-key`: Required. Your API authentication key.

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `video_url` | string (URI format) | Yes | URL of the video from which to extract the thumbnail |
| `second` | number (minimum: 0) | No | Timestamp in seconds at which to extract the thumbnail (defaults to 0) |
| `webhook_url` | string (URI format) | No | URL to receive the processing result asynchronously |
| `id` | string | No | Custom identifier for tracking the request |

### Example Request

```json
{
  "video_url": "https://example.com/video.mp4",
  "second": 30,
  "webhook_url": "https://your-service.com/webhook",
  "id": "custom-request-123"
}
```

### Example cURL Command

```bash
curl -X POST \
  https://api.example.com/v1/video/thumbnail \
  -H 'Content-Type: application/json' \
  -H 'x-api-key: your-api-key' \
  -d '{
    "video_url": "https://example.com/video.mp4",
    "second": 30,
    "webhook_url": "https://your-service.com/webhook",
    "id": "custom-request-123"
  }'
```

## Response

### Immediate Response (Status Code: 202)

When a webhook URL is provided, the API immediately returns a 202 Accepted response and processes the request asynchronously:

```json
{
  "code": 202,
  "id": "custom-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "processing",
  "pid": 12345,
  "queue_id": 67890,
  "max_queue_length": "unlimited",
  "queue_length": 1,
  "build_number": "1.0.0"
}
```

### Success Response (Status Code: 200)

When no webhook URL is provided or when the webhook is called after processing:

```json
{
  "code": 200,
  "id": "custom-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "https://storage.example.com/thumbnails/video-thumbnail-123.jpg",
  "message": "success",
  "run_time": 1.234,
  "queue_time": 0.567,
  "total_time": 1.801,
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 0,
  "build_number": "1.0.0"
}
```

### Error Responses

#### Invalid Request (Status Code: 400)

```json
{
  "code": 400,
  "message": "Invalid request: 'video_url' is a required property",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Queue Full (Status Code: 429)

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

#### Server Error (Status Code: 500)

```json
{
  "code": 500,
  "id": "custom-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Failed to download video from provided URL",
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 0,
  "build_number": "1.0.0"
}
```

## Error Handling

The endpoint handles various error scenarios:

- **Missing Required Parameters**: Returns a 400 error if `video_url` is missing.
- **Invalid Parameter Format**: Returns a 400 error if parameters don't match the expected format (e.g., invalid URLs).
- **Queue Capacity**: Returns a 429 error if the processing queue is full.
- **Processing Errors**: Returns a 500 error if there are issues during thumbnail extraction or upload.

## Usage Notes

1. **Asynchronous Processing**: For long-running operations, provide a `webhook_url` to receive the result asynchronously.
2. **Timestamp Selection**: Choose an appropriate `second` value to capture a meaningful frame from the video.
3. **Request Tracking**: Use the `id` parameter to track your requests across your systems.
4. **Queue Management**: The API uses a queue system with configurable maximum length (set by the `MAX_QUEUE_LENGTH` environment variable).

## Common Issues

1. **Inaccessible Video URLs**: Ensure the video URL is publicly accessible or has proper authentication.
2. **Invalid Timestamp**: If the specified second exceeds the video duration, the API may use the last frame or return an error.
3. **Webhook Failures**: If your webhook endpoint is unavailable, you won't receive the processing result.
4. **Large Videos**: Processing very large videos may take longer and could time out.

## Best Practices

1. **Use Webhooks for Long Videos**: Always use webhooks when processing large videos to avoid HTTP timeout issues.
2. **Optimize Thumbnail Selection**: Choose meaningful timestamps for thumbnails (e.g., after intro sequences).
3. **Error Handling**: Implement proper error handling in your application to manage API errors gracefully.
4. **Rate Limiting**: Monitor the queue length in responses to avoid overwhelming the service.
5. **Idempotent Requests**: Use the `id` parameter to make requests idempotent and avoid duplicate processing.