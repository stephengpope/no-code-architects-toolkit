
# `/image-to-video` API Documentation

## Overview
The `/image-to-video` endpoint converts an image into a video with options for frame rate, length, and zoom speed, allowing for custom animations like slow zoom.

## Endpoint
- **URL**: `/image-to-video`
- **Method**: `POST`

## Request

### Headers
- **X-API-Key** (string, required): The API key used for authentication.

### Body Parameters
- **image_url** (string, required): URL of the image to convert into a video.
- **length** (integer, optional): Duration of the output video in seconds. Defaults to 10 seconds.
- **frame_rate** (integer, optional): Frame rate for the video. Defaults to 24 frames per second.
- **zoom_speed** (float, optional): Rate of zoom applied to the image (e.g., `1.1` for slight zoom-in effect). Defaults to `1.0` (no zoom).
- **webhook_url** (string, optional): URL to receive the video URL upon completion.
- **id** (string, optional): Unique identifier for tracking the job.

### Example Request
```json
{
  "image_url": "https://example.com/image.jpg",
  "length": 15,
  "frame_rate": 30,
  "zoom_speed": 1.2,
  "webhook_url": "https://your-webhook-url.com/notify",
  "id": "video123"
}
```

### Example using `curl`
```bash
curl -X POST "https://your-api-domain.com/image-to-video" \
-H "X-API-Key: your_api_key" \
-H "Content-Type: application/json" \
-d '{
      "image_url": "https://example.com/image.jpg",
      "length": 15,
      "frame_rate": 30,
      "zoom_speed": 1.2,
      "webhook_url": "https://your-webhook-url.com/notify",
      "id": "video123"
    }'
```

## Response

### Success Response (200 OK)
If the video conversion is successful and no `webhook_url` is provided:
- **Status Code**: `200 OK`
- **Body**:
    ```json
    {
      "job_id": "video123",
      "video_url": "https://cloud-storage-url.com/output.mp4",
      "message": "success"
    }
    ```

### Accepted Response (202 Accepted)
If a `webhook_url` is provided, the request is queued, and this response is returned:
- **Status Code**: `202 Accepted`
- **Body**:
    ```json
    {
      "job_id": "video123",
      "message": "processing"
    }
    ```

### Error Responses
- **400 Bad Request**: Missing or invalid `image_url`.
  ```json
  {
    "error": "Missing image_url parameter"
  }
  ```
- **500 Internal Server Error**: Conversion process failed.
  ```json
  {
    "error": "Error during image-to-video conversion"
  }
  ```

## Error Handling
- **400 Bad Request**: Returned if `image_url` is missing or invalid.
- **500 Internal Server Error**: Returned if there is an error during video conversion.

## Usage Notes
- `zoom_speed` values greater than `1.0` apply a zoom-in effect; values below `1.0` apply a zoom-out effect.
- The `frame_rate` can be adjusted for smoother or more cinematic animations.

## Common Issues
1. **Invalid Image URL**: Make sure `image_url` is accessible and points directly to the image file.
2. **Unsupported Frame Rate or Length**: Check if the `frame_rate` or `length` values are too high for server resources.

## Best Practices
- **Use `webhook_url` for Long Conversions**: For large images or high frame rates, use `webhook_url` to receive the video asynchronously.
- **Optimize Frame Rate**: A `frame_rate` of 24 is generally smooth, but adjust as needed based on animation requirements.
