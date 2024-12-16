# `/v1/image/transform/video` API Documentation

## Overview
This endpoint is used to convert an image into a video with a specified length, frame rate, and zoom speed. The resulting video file is uploaded to cloud storage, and the cloud URL is returned in the response.

## Endpoint
- URL Path: `/v1/image/transform/video`
- HTTP Method: `POST`

## Request

### Headers
- `Authorization` (required): Bearer token for authentication.

### Body Parameters
- `image_url` (required, string): The URL of the image to be converted into a video.
- `length` (optional, number): The desired length of the video in seconds. Default is 5 seconds. Minimum is 1, and maximum is 60.
- `frame_rate` (optional, integer): The desired frame rate of the video. Default is 30 frames per second. Minimum is 15, and maximum is 60.
- `zoom_speed` (optional, number): The desired zoom speed of the video, represented as a percentage. Default is 3%. Minimum is 0, and maximum is 100.
- `webhook_url` (optional, string): The URL to receive a webhook notification when the video conversion is complete.
- `id` (optional, string): An identifier for the request.

### Example Request

```json
{
  "image_url": "https://example.com/image.jpg",
  "length": 10,
  "frame_rate": 24,
  "zoom_speed": 5,
  "webhook_url": "https://example.com/webhook",
  "id": "request-123"
}
```

```bash
curl -X POST \
  https://api.example.com/v1/image/transform/video \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "length": 10,
    "frame_rate": 24,
    "zoom_speed": 5,
    "webhook_url": "https://example.com/webhook",
    "id": "request-123"
  }'
```

## Response

### Success Response
- Status Code: `200 OK`
- Response Body:
  ```json
  {
    "cloud_url": "https://storage.example.com/videos/converted_video.mp4"
  }
  ```

### Error Responses
- Status Code: `400 Bad Request`
  ```json
  {
    "error": "Invalid request payload"
  }
  ```

- Status Code: `401 Unauthorized`
  ```json
  {
    "error": "Authentication failed"
  }
  ```

- Status Code: `500 Internal Server Error`
  ```json
  {
    "error": "An error occurred while processing the request"
  }
  ```

## Error Handling
- Missing or invalid request parameters will result in a `400 Bad Request` error.
- Authentication failures will result in a `401 Unauthorized` error.
- Any other errors during the image-to-video conversion process will result in a `500 Internal Server Error`.

## Usage Notes
- The `image_url` parameter must be a valid URL pointing to an image file.
- The `length`, `frame_rate`, and `zoom_speed` parameters are optional and will use default values if not provided.
- The `webhook_url` parameter is optional and can be used to receive a notification when the video conversion is complete.
- The `id` parameter is optional and can be used to identify the request.

## Common Issues
- Providing an invalid or inaccessible `image_url`.
- Exceeding the maximum allowed values for `length`, `frame_rate`, or `zoom_speed`.

## Best Practices
- Validate the `image_url` parameter before sending the request to ensure it points to a valid image file.
- Use appropriate values for `length`, `frame_rate`, and `zoom_speed` based on your requirements and the capabilities of your system.
- Implement error handling and retries for failed requests.
- Monitor the webhook notifications (if provided) to track the progress and completion of the video conversion process.