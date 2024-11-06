
# `/transcribe-media` API Documentation

## Overview
The `/transcribe-media` endpoint transcribes audio from a media URL to text or subtitle formats (e.g., `srt`, `vtt`, `ass`), with optional character limit and webhook notifications.

## Endpoint
- **URL**: `/transcribe-media`
- **Method**: `POST`

## Request

### Headers
- **X-API-Key** (string, required): The API key used for authentication.

### Body Parameters
- **media_url** (string, required): URL of the media file to be transcribed.
- **output** (string, optional): Desired output format (`transcript`, `srt`, `vtt`, `ass`). Defaults to `transcript`.
- **webhook_url** (string, optional): URL for sending the transcription result.
- **max_chars** (integer, optional): Maximum number of characters per subtitle line.
- **id** (string, optional): Unique identifier for tracking the job.

### Example Request
```json
{
  "media_url": "https://example.com/audio.mp3",
  "output": "srt",
  "webhook_url": "https://your-webhook-url.com/notify",
  "max_chars": 56,
  "id": "abc123"
}
```

### Example using `curl`
```bash
curl -X POST "https://your-api-domain.com/transcribe-media" \
-H "X-API-Key: your_api_key" \
-H "Content-Type: application/json" \
-d '{
      "media_url": "https://example.com/audio.mp3",
      "output": "srt",
      "webhook_url": "https://your-webhook-url.com/notify",
      "max_chars": 56,
      "id": "abc123"
    }'
```

## Response

### Success Response (200 OK)
If the transcription is successful and no `webhook_url` is provided:
- **Status Code**: `200 OK`
- **Body**:
    ```json
    {
      "job_id": "abc123",
      "response": "transcript_text_or_url",
      "message": "success"
    }
    ```

### Accepted Response (202 Accepted)
If a `webhook_url` is provided, the request is queued, and this response is returned:
- **Status Code**: `202 Accepted`
- **Body**:
    ```json
    {
      "job_id": "abc123",
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
- **400 Bad Request**: Returned if `media_url` is missing or invalid.
- **500 Internal Server Error**: Returned if transcription fails.

## Usage Notes
- Ensure `media_url` points to a compatible media file format (e.g., MP3, MP4).
- If using `srt`, `vtt`, or `ass` formats, subtitles will follow specified `max_chars` limits if provided.

## Common Issues
1. **Invalid Media URL**: Ensure `media_url` is directly accessible.
2. **Unsupported Format**: Confirm that the provided media file is in a format compatible with transcription.

## Best Practices
- **Use Webhooks for Long Transcriptions**: For large files, consider using `webhook_url` to asynchronously receive transcription results.
- **Optimize for Readability**: Adjust `max_chars` based on display needs when using subtitle formats.
