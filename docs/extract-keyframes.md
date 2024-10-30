# `/extract-keyframes` API Documentation

## Overview
The `/extract-keyframes` endpoint extracts keyframes from a video file, providing snapshots at key moments in the video. This can be useful for generating thumbnails or preview images.

## Endpoint
- **URL**: `/extract-keyframes`
- **Method**: `POST`

## Request

### Headers
- **X-API-Key** (string, required): The API key used for authentication.

### Body Parameters
- **video_url** (string, required): URL of the video file from which keyframes are to be extracted.
- **webhook_url** (string, optional): URL to receive the URLs of extracted keyframes upon completion.
- **id** (string, optional): Unique identifier for tracking the job.

### Example Request
```json
{
  "video_url": "https://example.com/video.mp4",
  "webhook_url": "https://your-webhook-url.com/notify",
  "id": "keyframes123"
}
```

### Example using `curl`
```bash
curl -X POST "https://your-api-domain.com/extract-keyframes" \
-H "X-API-Key: your_api_key" \
-H "Content-Type: application/json" \
-d '{
      "video_url": "https://example.com/video.mp4",
      "webhook_url": "https://your-webhook-url.com/notify",
      "id": "keyframes123"
    }'
```

## Response

### Success Response (200 OK)
If the keyframe extraction is successful and no `webhook_url` is provided:
- **Status Code**: `200 OK`
- **Body**:
    ```json
    {
      "job_id": "keyframes123",
      "keyframes": [
        "https://cloud-storage-url.com/keyframe1.jpg",
        "https://cloud-storage-url.com/keyframe2.jpg",
        "https://cloud-storage-url.com/keyframe3.jpg"
      ],
      "message": "success"
    }
    ```

### Accepted Response (202 Accepted)
If a `webhook_url` is provided, the request is queued, and this response is returned:
- **Status Code**: `202 Accepted`
- **Body**:
    ```json
    {
      "job_id": "keyframes123",
      "message": "processing"
    }
    ```

### Error Responses
- **400 Bad Request**: Missing or invalid `video_url`.
  ```json
  {
    "error": "Missing or invalid video_url parameter"
  }
  ```
- **500 Internal Server Error**: Keyframe extraction process failed.
  ```json
  {
    "error": "Error during keyframe extraction"
  }
  ```

## Error Handling
- **400 Bad Request**: Returned if `video_url` is missing or invalid.
- **500 Internal Server Error**: Returned if an error occurs during keyframe extraction.

## Usage Notes
- This endpoint extracts keyframes only; it does not provide evenly spaced frames.
- Keyframes are typically chosen based on scene changes or significant moments in the video.

## Common Issues
1. **Invalid Video URL**: Ensure that `video_url` points directly to the video file and is accessible.
2. **Large Video Files**: Processing very large video files may take longer or require higher server resources.

## Best Practices
- **Asynchronous Processing**: Use `webhook_url` for large video files to receive keyframe URLs asynchronously.
- **Optimize for Thumbnails**: Extracted keyframes can be used to create thumbnails or video previews, so plan for storage and accessibility of these images.
