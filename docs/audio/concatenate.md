# Audio Concatenation API Endpoint Documentation

## Overview

The `/v1/audio/concatenate` endpoint provides functionality to combine multiple audio files into a single audio file. This endpoint is part of the v1 API structure and is registered in the main application through the `v1_audio_concatenate_bp` Blueprint. It leverages the application's queuing system to handle asynchronous processing, which is particularly useful for potentially time-consuming audio processing operations.

## Endpoint

- **URL**: `/v1/audio/concatenate`
- **Method**: `POST`

## Request

### Headers

- `x-api-key`: Required. Your API authentication key.

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `audio_urls` | Array | Yes | An array of objects, each containing an `audio_url` property pointing to an audio file to be concatenated. Must contain at least one item. |
| `webhook_url` | String | No | A URL to receive a callback notification when processing is complete. If provided, the request will be processed asynchronously. |
| `id` | String | No | A custom identifier for tracking the request. |

Each object in the `audio_urls` array must have:
- `audio_url`: String (URI format). The URL of an audio file to be concatenated.

### Example Request

```json
{
  "audio_urls": [
    { "audio_url": "https://example.com/audio1.mp3" },
    { "audio_url": "https://example.com/audio2.mp3" },
    { "audio_url": "https://example.com/audio3.mp3" }
  ],
  "webhook_url": "https://your-webhook-endpoint.com/callback",
  "id": "custom-request-id-123"
}
```

### Example cURL Command

```bash
curl -X POST \
  https://api.example.com/v1/audio/concatenate \
  -H 'Content-Type: application/json' \
  -H 'x-api-key: your-api-key-here' \
  -d '{
    "audio_urls": [
      { "audio_url": "https://example.com/audio1.mp3" },
      { "audio_url": "https://example.com/audio2.mp3" }
    ],
    "webhook_url": "https://your-webhook-endpoint.com/callback",
    "id": "custom-request-id-123"
  }'
```

## Response

### Synchronous Response (No webhook_url provided)

If no `webhook_url` is provided, the request will be processed synchronously and return:

```json
{
  "code": 200,
  "id": "custom-request-id-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "https://storage.example.com/combined-audio-file.mp3",
  "message": "success",
  "run_time": 2.345,
  "queue_time": 0,
  "total_time": 2.345,
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 0,
  "build_number": "1.0.123"
}
```

### Asynchronous Response (webhook_url provided)

If a `webhook_url` is provided, the request will be queued for processing and immediately return:

```json
{
  "code": 202,
  "id": "custom-request-id-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "processing",
  "pid": 12345,
  "queue_id": 67890,
  "max_queue_length": "unlimited",
  "queue_length": 1,
  "build_number": "1.0.123"
}
```

When processing is complete, a webhook will be sent to the provided URL with the following payload:

```json
{
  "endpoint": "/v1/audio/concatenate",
  "code": 200,
  "id": "custom-request-id-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "https://storage.example.com/combined-audio-file.mp3",
  "message": "success",
  "pid": 12345,
  "queue_id": 67890,
  "run_time": 3.456,
  "queue_time": 1.234,
  "total_time": 4.690,
  "queue_length": 0,
  "build_number": "1.0.123"
}
```

### Error Responses

#### Invalid Request Format (400 Bad Request)

```json
{
  "code": 400,
  "id": null,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Invalid request: 'audio_urls' is a required property",
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 0,
  "build_number": "1.0.123"
}
```

#### Authentication Error (401 Unauthorized)

```json
{
  "code": 401,
  "message": "Invalid or missing API key",
  "build_number": "1.0.123"
}
```

#### Queue Limit Reached (429 Too Many Requests)

```json
{
  "code": 429,
  "id": "custom-request-id-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "MAX_QUEUE_LENGTH (100) reached",
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 100,
  "build_number": "1.0.123"
}
```

#### Processing Error (500 Internal Server Error)

```json
{
  "code": 500,
  "id": "custom-request-id-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Error downloading audio file: Connection refused",
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 0,
  "build_number": "1.0.123"
}
```

## Error Handling

- **Missing Required Parameters**: If `audio_urls` is missing or empty, a 400 Bad Request response will be returned.
- **Invalid URL Format**: If any `audio_url` is not a valid URI, a 400 Bad Request response will be returned.
- **Authentication Failure**: If the API key is invalid or missing, a 401 Unauthorized response will be returned.
- **Queue Limit**: If the queue is full (when MAX_QUEUE_LENGTH is set), a 429 Too Many Requests response will be returned.
- **Processing Errors**: Any errors during audio download, processing, or upload will result in a 500 Internal Server Error response with details in the message field.

## Usage Notes

1. **Asynchronous Processing**: For long audio files, it's recommended to use the `webhook_url` parameter to process the request asynchronously.
2. **File Formats**: The service supports common audio formats. The output will be in a standard format (typically MP3).
3. **File Size**: There may be limits on the size of audio files that can be processed. Very large files might cause timeouts or failures.
4. **Queue Behavior**: If the system is under heavy load, requests with `webhook_url` will be queued. The MAX_QUEUE_LENGTH environment variable controls the maximum queue size.

## Common Issues

1. **Inaccessible Audio URLs**: Ensure all audio URLs are publicly accessible. Private or authentication-required URLs will cause failures.
2. **Incompatible Audio Formats**: Some exotic audio formats might not be supported. Stick to common formats like MP3, WAV, or AAC.
3. **Webhook Failures**: If your webhook endpoint is unavailable when the processing completes, you might not receive the completion notification.
4. **Timeout Issues**: Very large audio files might cause timeouts during download or processing.

## Best Practices

1. **Use Webhooks for Large Files**: Always use the webhook approach for large audio files or when concatenating many files.
2. **Include an ID**: Always include a custom `id` parameter to help track your requests, especially in webhook responses.
3. **Error Handling**: Implement robust error handling in your client application to handle various HTTP status codes.
4. **Webhook Reliability**: Ensure your webhook endpoint is reliable and can handle retries if necessary.
5. **File Preparation**: Pre-process your audio files to ensure they have compatible formats, sample rates, and channel configurations for best results.
6. **Queue Monitoring**: Monitor the `queue_length` in responses to understand system load and adjust your request patterns if needed.