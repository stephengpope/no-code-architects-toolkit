# `/caption-video` API Documentation

## Overview
The `/caption-video` endpoint adds captions to a video from an SRT or ASS file, allowing for easy subtitle embedding.

## Endpoint
- **URL**: `/caption-video`
- **Method**: `POST`

## Request

### Headers
- **X-API-Key** (string, required): The API key used for authentication.

### Body Parameters
- **video_url** (string, required): URL of the video to which captions will be added.
- **srt_url** or **ass_url** (string, required): URL of the subtitle file in SRT or ASS format.
- **webhook_url** (string, optional): URL to receive the processed video link upon completion.
- **id** (string, optional): Unique identifier for tracking the job.

### Example Request
```json
{
  "video_url": "https://example.com/video.mp4",
  "srt_url": "https://example.com/captions.srt",
  "webhook_url": "https://your-webhook-url.com/notify",
  "id": "caption123"
}
```

### Example using `curl`
```bash
curl -X POST "https://your-api-domain.com/caption-video" \
-H "X-API-Key: your_api_key" \
-H "Content-Type: application/json" \
-d '{
      "video_url": "https://example.com/video.mp4",
      "srt_url": "https://example.com/captions.srt",
      "webhook_url": "https://your-webhook-url.com/notify",
      "id": "caption123"
    }'
```

## Response

### Success Response (200 OK)
If the captioning is successful and no `webhook_url` is provided:
- **Status Code**: `200 OK`
- **Body**:
    ```json
    {
      "job_id": "caption123",
      "video_url": "https://cloud-storage-url.com/output_with_captions.mp4",
      "message": "success"
    }
    ```

### Accepted Response (202 Accepted)
If a `webhook_url` is provided, the request is queued, and this response is returned:
- **Status Code**: `202 Accepted`
- **Body**:
    ```json
    {
      "job_id": "caption123",
      "message": "processing"
    }
    ```

### Error Responses
- **400 Bad Request**: Missing or invalid parameters (`video_url`, `srt_url`, or `ass_url`).
  ```json
  {
    "error": "Missing required video_url and subtitle file (srt_url or ass_url)"
  }
  ```
- **500 Internal Server Error**: Captioning process failed.
  ```json
  {
    "error": "Error during video captioning"
  }
  ```

## Error Handling
- **400 Bad Request**: Returned if `video_url` or subtitle file (`srt_url` or `ass_url`) is missing or malformed.
- **500 Internal Server Error**: Returned if there’s an error during captioning.

## Usage Notes
- Either `srt_url` or `ass_url` must be provided to add captions to the video.
- The endpoint supports popular subtitle formats (SRT and ASS) for embedding captions.

## Common Issues
1. **Invalid Video or Subtitle URL**: Ensure `video_url` and subtitle URL are valid and accessible.
2. **Unsupported Subtitle Format**: Use either SRT or ASS formats for compatibility.

## Best Practices
- **Asynchronous Processing**: For large video files, use `webhook_url` to receive the processed video asynchronously.
- **Verify Subtitle Sync**: Ensure the subtitle timing matches the video length and content for best results.
