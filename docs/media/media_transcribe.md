# Media Transcription API Documentation

## Overview
The Media Transcription endpoint is part of the v1 API suite, providing audio/video transcription and translation capabilities. This endpoint leverages a queuing system for handling long-running transcription tasks, with webhook support for asynchronous processing. It's integrated into the main Flask application as a Blueprint and supports both direct response and cloud storage options for the transcription results.

## Endpoint
- **URL**: `/v1/media/transcribe`
- **Method**: `POST`
- **Blueprint**: `v1_media_transcribe_bp`

## Request

### Headers
- `x-api-key`: Required. Authentication key for API access.
- `Content-Type`: Required. Must be `application/json`.

### Body Parameters

#### Required Parameters
- `media_url` (string)
  - Format: URI
  - Description: URL of the media file to be transcribed

#### Optional Parameters
- `task` (string)
  - Allowed values: `"transcribe"`, `"translate"`
  - Default: `"transcribe"`
  - Description: Specifies whether to transcribe or translate the audio
  
- `include_text` (boolean)
  - Default: `true`
  - Description: Include plain text transcription in the response
  
- `include_srt` (boolean)
  - Default: `false`
  - Description: Include SRT format subtitles in the response
  
- `include_segments` (boolean)
  - Default: `false`
  - Description: Include timestamped segments in the response
  
- `word_timestamps` (boolean)
  - Default: `false`
  - Description: Include timestamps for individual words
  
- `response_type` (string)
  - Allowed values: `"direct"`, `"cloud"`
  - Default: `"direct"`
  - Description: Whether to return results directly or as cloud storage URLs
  
- `language` (string)
  - Optional
  - Description: Source language code for transcription
  
- `webhook_url` (string)
  - Format: URI
  - Description: URL to receive the transcription results asynchronously
  
- `id` (string)
  - Description: Custom identifier for the transcription job

- `max_words_per_line` (integer)
  - Minimum: 1
  - Description: Controls the maximum number of words per line in the SRT file. When specified, each segment's text will be split into multiple lines with at most the specified number of words per line.

### Example Request

```bash
curl -X POST "https://api.example.com/v1/media/transcribe" \
  -H "x-api-key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "https://example.com/media/file.mp3",
    "task": "transcribe",
    "include_text": true,
    "include_srt": true,
    "include_segments": true,
    "response_type": "cloud",
    "webhook_url": "https://your-webhook.com/callback",
    "id": "custom-job-123",
    "max_words_per_line": 5
  }'
```

## Response

### Immediate Response (202 Accepted)
When a webhook URL is provided, the API returns an immediate acknowledgment:

```json
{
  "code": 202,
  "id": "custom-job-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "processing",
  "pid": 12345,
  "queue_id": 67890,
  "max_queue_length": "unlimited",
  "queue_length": 1,
  "build_number": "1.0.0"
}
```

### Success Response (via Webhook)
For direct response_type:

```json
{
  "endpoint": "/v1/transcribe/media",
  "code": 200,
  "id": "custom-job-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": {
    "text": "Transcribed text content...",
    "srt": "SRT formatted content...",
    "segments": [...],
    "text_url": null,
    "srt_url": null,
    "segments_url": null
  },
  "message": "success",
  "pid": 12345,
  "queue_id": 67890,
  "run_time": 5.234,
  "queue_time": 0.123,
  "total_time": 5.357,
  "queue_length": 0,
  "build_number": "1.0.0"
}
```

For cloud response_type:

```json
{
  "endpoint": "/v1/transcribe/media",
  "code": 200,
  "id": "custom-job-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": {
    "text": null,
    "srt": null,
    "segments": null,
    "text_url": "https://storage.example.com/text.txt",
    "srt_url": "https://storage.example.com/subtitles.srt",
    "segments_url": "https://storage.example.com/segments.json"
  },
  "message": "success",
  "pid": 12345,
  "queue_id": 67890,
  "run_time": 5.234,
  "queue_time": 0.123,
  "total_time": 5.357,
  "queue_length": 0,
  "build_number": "1.0.0"
}
```

### Error Responses

#### Queue Full (429 Too Many Requests)
```json
{
  "code": 429,
  "id": "custom-job-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "MAX_QUEUE_LENGTH (100) reached",
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 100,
  "build_number": "1.0.0"
}
```

#### Server Error (500 Internal Server Error)
```json
{
  "endpoint": "/v1/transcribe/media",
  "code": 500,
  "id": "custom-job-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": null,
  "message": "Error message details",
  "pid": 12345,
  "queue_id": 67890,
  "run_time": 0.123,
  "queue_time": 0.056,
  "total_time": 0.179,
  "queue_length": 1,
  "build_number": "1.0.0"
}
```

## Error Handling

### Common Errors
- **Invalid API Key**: 401 Unauthorized
- **Invalid JSON Payload**: 400 Bad Request
- **Missing Required Fields**: 400 Bad Request
- **Invalid media_url**: 400 Bad Request
- **Queue Full**: 429 Too Many Requests
- **Processing Error**: 500 Internal Server Error

### Validation Errors
The endpoint performs strict validation of the request payload using JSON Schema. Common validation errors include:
- Invalid URI format for media_url or webhook_url
- Invalid task value (must be "transcribe" or "translate")
- Invalid response_type value (must be "direct" or "cloud")
- Unknown properties in the request body

## Usage Notes

1. **Webhook Processing**
   - When a webhook_url is provided, the request is processed asynchronously
   - The API returns an immediate 202 response with a job_id
   - Final results are sent to the webhook_url when processing completes

2. **Queue Management**
   - Requests with webhook_url are queued for processing
   - MAX_QUEUE_LENGTH environment variable controls queue size
   - Set MAX_QUEUE_LENGTH to 0 for unlimited queue size

3. **File Management**
   - For cloud response_type, temporary files are automatically cleaned up
   - Results are uploaded to cloud storage before deletion
   - URLs in the response provide access to the stored files

4. **SRT Formatting**
   - The `max_words_per_line` parameter allows control over the maximum number of words per line in the SRT file
   - When specified, each segment's text will be split into multiple lines with at most the specified number of words per line
   - This is useful for creating more readable subtitles with consistent line lengths

## Common Issues

1. **Media Access**
   - Ensure media_url is publicly accessible
   - Verify media file format is supported
   - Check for media file corruption

2. **Webhook Delivery**
   - Ensure webhook_url is publicly accessible
   - Implement webhook endpoint retry logic
   - Monitor webhook endpoint availability

3. **Resource Usage**
   - Large media files may take significant processing time
   - Monitor queue length for production deployments
   - Consider implementing request size limits

## Best Practices

1. **Request Handling**
   - Always provide a unique id for job tracking
   - Implement webhook retry logic
   - Store job_id for result correlation

2. **Resource Management**
   - Monitor queue length in production
   - Implement appropriate timeout handling
   - Use cloud response_type for large files

3. **Error Handling**
   - Implement comprehensive webhook error handling
   - Log job_id with all related operations
   - Monitor processing times and error rates

4. **Security**
   - Use HTTPS for media_url and webhook_url
   - Implement webhook authentication
   - Validate media file types before processing