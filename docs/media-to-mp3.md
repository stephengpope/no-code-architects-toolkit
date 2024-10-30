# `/media-to-mp3` API Documentation

## Overview
The `/media-to-mp3` endpoint converts a media file from a provided URL to MP3 format with an optional bitrate. 

## Endpoint
- **URL**: `/media-to-mp3`
- **Method**: `POST`

## Request

### Headers
- **X-API-Key** (string, required): The API key used for authentication.

### Body Parameters
- **media_url** (string, required): The URL of the media file to convert.
- **bitrate** (string, optional): Desired audio bitrate for the MP3 file (e.g., `128k`, `192k`). Defaults to `128k`.
- **webhook_url** (string, optional): URL to receive the response after conversion.
- **id** (string, optional): A unique identifier for tracking the job.

### Example Request
```json
{
  "media_url": "https://example.com/video.mp4",
  "bitrate": "192k",
  "webhook_url": "https://your-webhook-url.com/notify",
  "id": "12345"
}
```

### Example using `curl`
```bash
curl -X POST "https://your-api-domain.com/media-to-mp3" \
-H "X-API-Key: your_api_key" \
-H "Content-Type: application/json" \
-d '{
      "media_url": "https://example.com/video.mp4",
      "bitrate": "192k",
      "webhook_url": "https://your-webhook-url.com/notify",
      "id": "12345"
    }'
```

## Response

### Success Response (200 OK)
If the conversion is successful and no `webhook_url` is provided:
- **Status Code**: `200 OK`
- **Body**:
    ```json
    {
      "job_id": "12345",
      "filename": "12345.mp3",
      "message": "success"
    }
    ```

### Accepted Response (202 Accepted)
If a `webhook_url` is provided, the request is queued, and this response is returned:
- **Status Code**: `202 Accepted`
- **Body**:
    ```json
    {
      "job_id": "12345",
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
- **500 Internal Server Error**: Conversion failed.
  ```json
  {
    "error": "Error during media conversion"
  }
  ```

## Error Handling
- **400 Bad Request**: Returned if `media_url` is missing or malformed.
- **500 Internal Server Error**: Returned if there’s an error during media processing.

## Usage Notes
- Ensure the `media_url` points to a downloadable media file format (e.g., MP4, WAV).
- When `webhook_url` is provided, the system will notify the specified URL upon job completion.

## Common Issues
1. **Invalid Media URL**: The `media_url` should be accessible and point directly to the media file.
2. **Unsupported File Type**: Ensure the input media is in a compatible format (e.g., video or audio).

## Best Practices
- **Async Processing**: If processing large files, use the `webhook_url` to avoid waiting for completion.
- **Resource Management**: Avoid excessively high bitrate values as they may impact file size and processing time.
