# `/v1/video/concatenate` API Documentation

## Overview
This endpoint is used to combine multiple video files into a single video file. It accepts a list of video URLs, an optional webhook URL, and an optional ID. The combined video file is then uploaded to cloud storage, and the cloud URL of the combined video is returned.

## Endpoint
**URL Path:** `/v1/video/concatenate`
**HTTP Method:** `POST`

## Request

### Headers
- `Authorization` (required): Authentication header containing a valid token.

### Body Parameters
- `video_urls` (required, array of objects): A list of video URLs to be combined.
  - `video_url` (required, string): The URL of the video file.
- `webhook_url` (optional, string): The URL to which a webhook notification will be sent after the video combination process is complete.
- `id` (optional, string): An identifier for the request.

### Example Request

```json
{
  "video_urls": [
    {
      "video_url": "https://example.com/video1.mp4"
    },
    {
      "video_url": "https://example.com/video2.mp4"
    }
  ],
  "webhook_url": "https://example.com/webhook",
  "id": "request-123"
}
```

```bash
curl -X POST \
  https://api.example.com/v1/video/concatenate \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "video_urls": [
      {
        "video_url": "https://example.com/video1.mp4"
      },
      {
        "video_url": "https://example.com/video2.mp4"
      }
    ],
    "webhook_url": "https://example.com/webhook",
    "id": "request-123"
  }'
```

## Response

### Success Response
**Status Code:** `200 OK`

```json
{
  "data": "https://cloud.example.com/combined-video.mp4"
}
```

### Error Responses
**Status Code:** `400 Bad Request`

```json
{
  "error": "Invalid request payload"
}
```

**Status Code:** `401 Unauthorized`

```json
{
  "error": "Authentication failed"
}
```

**Status Code:** `500 Internal Server Error`

```json
{
  "error": "An error occurred during video combination process"
}
```

## Error Handling
- Missing or invalid request parameters will result in a `400 Bad Request` error.
- Authentication failures will result in a `401 Unauthorized` error.
- Any other errors during the video combination process will result in a `500 Internal Server Error`.

## Usage Notes
- The video combination process may take some time, depending on the number and size of the video files.
- If a webhook URL is provided, a notification will be sent to that URL after the video combination process is complete.
- The combined video file will be uploaded to cloud storage, and the cloud URL will be returned in the response.

## Common Issues
- Providing invalid video URLs or unsupported video formats.
- Authentication failures due to expired or invalid tokens.
- Network or server issues that may cause the video combination process to fail.

## Best Practices
- Validate the video URLs and formats before sending the request.
- Use a valid and up-to-date authentication token.
- Implement retry mechanisms and error handling in your client application.
- Monitor the webhook notifications for updates on the video combination process.