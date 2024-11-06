Here’s the detailed README file for the `/v1/transcribe/media` endpoint.
# `/v1/transcribe/media` API Documentation

## Overview
The `/v1/transcribe/media` endpoint provides transcription or translation of media content with advanced options like word timestamps, segmenting, and output format customization.

## Endpoint
- **URL**: `/v1/transcribe/media`
- **Method**: `POST`

## Request

### Headers
- **X-API-Key** (string, required): The API key used for authentication.

### Body Parameters
- **media_url** (string, required): URL of the media file to transcribe or translate.
- **task** (string, optional): Action to perform, either `transcribe` (default) or `translate`.
- **format_type** (string, optional): Output format, such as `text`, `srt`, `vtt`, or `ass`. Defaults to `text`.
- **word_timestamps** (boolean, optional): Include timestamps for each word if `true`.
- **segments** (boolean, optional): If `true`, returns segmented transcription output.
- **response_type** (string, optional): Specifies the response format (`json` for JSON output or `cloud` for file URLs in cloud storage).
- **language** (string, optional): Language to be used during transcription.
- **webhook_url** (string, optional): URL for receiving results asynchronously.
- **id** (string, optional): Unique identifier for tracking the job.

### Example Request
```json
{
  "media_url": "https://example.com/audio.mp3",
  "task": "transcribe",
  "format_type": "srt",
  "word_timestamps": true,
  "segments": true,
  "response_type": "json",
  "language": "en",
  "webhook_url": "https://your-webhook-url.com/notify",
  "id": "xyz789"
}
```

### Example using `curl`
```bash
curl -X POST "https://your-api-domain.com/v1/transcribe/media" \
-H "X-API-Key: your_api_key" \
-H "Content-Type: application/json" \
-d '{
      "media_url": "https://example.com/audio.mp3",
      "task": "transcribe",
      "format_type": "srt",
      "word_timestamps": true,
      "segments": true,
      "response_type": "json",
      "language": "en",
      "webhook_url": "https://your-webhook-url.com/notify",
      "id": "xyz789"
    }'
```

## Response

### Success Response (200 OK)
If the transcription is successful and no `webhook_url` is provided:
- **Status Code**: `200 OK`
- **Body** (example for `json` response type):
    ```json
    {
      "job_id": "xyz789",
      "response": {
        "text": "Transcription text",
        "segments": [ ... ],
        "captions": "Subtitle content in chosen format"
      },
      "message": "success"
    }
    ```

### Accepted Response (202 Accepted)
If a `webhook_url` is provided, the request is queued, and this response is returned:
- **Status Code**: `202 Accepted`
- **Body**:
    ```json
    {
      "job_id": "xyz789",
      "message": "processing"
    }
    ```

### Error Responses
- **400 Bad Request**: Missing or invalid `media_url`.
  ```json
  {
    "error": "Missing media_url parameter"
  }
  ```
- **500 Internal Server Error**: Transcription process failed.
  ```json
  {
    "error": "Error during transcription"
  }
  ```

## Error Handling
- **400 Bad Request**: Returned if `media_url` is missing or malformed.
- **500 Internal Server Error**: Returned for transcription errors.

## Usage Notes
- Use `format_type` to specify the format of the output (e.g., `srt` for subtitles).
- `word_timestamps` and `segments` are useful for detailed analytics or segmented display of transcripts.

## Common Issues
1. **Invalid Media URL**: Ensure `media_url` points to a valid, accessible media file.
2. **Unsupported Task**: `task` should be either `transcribe` or `translate`.

## Best Practices
- **Async Processing**: Use `webhook_url` for large files to receive results asynchronously.
- **Detailed Analysis**: Enable `word_timestamps` and `segments` for more granular transcript control.
