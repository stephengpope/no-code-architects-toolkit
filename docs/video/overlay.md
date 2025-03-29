# Video Overlay API

This API allows you to overlay one video on top of another video.

## Endpoint

```
POST /v1/video/overlay
```

## Authentication

This endpoint requires authentication. Include your API key in the Authorization header.

```
Authorization: Bearer YOUR_API_KEY
```

## Request Body

| Parameter | Type | Description |
|-----------|------|-------------|
| video_url | string | URL of the base video |
| overlay_video_url | string | URL of the video to overlay |
| start_time | number | Time in seconds when the overlay should start |
| webhook_url | string (optional) | URL to receive a callback when processing is complete |
| id | string (optional) | Optional ID for tracking this request |

## Example Request

```json
{
  "video_url": "https://example.com/base-video.mp4",
  "overlay_video_url": "https://example.com/overlay-video.mp4",
  "start_time": 5.5,
  "webhook_url": "https://your-server.com/webhook"
}
```

## Response

For synchronous requests (no webhook_url):

```json
{
  "job_id": "d8b3a030-16e0-469e-8a4a-d1e3d0d82120",
  "response": "https://storage.googleapis.com/your-bucket/d8b3a030-16e0-469e-8a4a-d1e3d0d82120.mp4",
  "code": 200,
  "message": "success",
  "run_time": 5.21,
  "queue_time": 0,
  "total_time": 5.21
}
```

For asynchronous requests (with webhook_url):

```json
{
  "job_id": "d8b3a030-16e0-469e-8a4a-d1e3d0d82120",
  "code": 202,
  "message": "processing",
  "queue_length": 1,
  "max_queue_length": "unlimited"
}
```

## Notes

- Both videos should have the same dimensions for best results
- The overlay video will be positioned at coordinates 0,0 (top-left corner)
- The overlay video will play starting at the specified start_time in the base video
- When the overlay video ends, it will disappear and the original video will be shown again
- The duration of the overlay is determined by the length of the overlay video
- Processing time depends on the size and length of the videos