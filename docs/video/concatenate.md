# Video Concatenation Endpoint

## 1. Overview

The `/v1/video/concatenate` endpoint is part of the Flask API application and is responsible for combining multiple video files into a single video file. This endpoint fits into the overall API structure as a part of the `v1` blueprint, which is dedicated to handling version 1 of the API.

## 2. Endpoint

**URL Path:** `/v1/video/concatenate`
**HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body must be a JSON object with the following properties:

- `video_urls` (required, array of objects): An array of video URLs to be combined. Each object in the array must have a `video_url` property (string, URI format) containing the URL of the video file.
- `webhook_url` (optional, string, URI format): The URL to which the webhook notification will be sent upon completion of the video combination process.
- `id` (optional, string): An identifier for the request.

#### Example Request

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
  -H 'x-api-key: YOUR_API_KEY' \
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

## 4. Response

### Success Response

**Status Code:** `200 OK`

**Response Body:**

```json
{
  "code": 200,
  "id": "request-123",
  "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "response": "https://example.com/combined-video.mp4",
  "message": "success",
  "run_time": 10.234,
  "queue_time": 0.0,
  "total_time": 10.234,
  "pid": 12345,
  "queue_id": 1234567890,
  "queue_length": 0,
  "build_number": "1.0.0"
}
```

The response contains the URL of the combined video file uploaded to cloud storage.

### Error Responses

**Status Code:** `500 Internal Server Error`

**Response Body:**

```json
{
  "code": 500,
  "id": "request-123",
  "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "message": "Error message describing the issue",
  "pid": 12345,
  "queue_id": 1234567890,
  "queue_length": 0,
  "build_number": "1.0.0"
}
```

**Status Code:** `429 Too Many Requests`

**Response Body:**

```json
{
  "code": 429,
  "id": "request-123",
  "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "message": "MAX_QUEUE_LENGTH (10) reached",
  "pid": 12345,
  "queue_id": 1234567890,
  "queue_length": 10,
  "build_number": "1.0.0"
}
```

## 5. Error Handling

- Missing or invalid `video_urls` parameter: Returns a `400 Bad Request` error.
- Invalid `webhook_url` format: Returns a `400 Bad Request` error.
- Error during the video combination process: Returns a `500 Internal Server Error` with the error message.
- If the maximum queue length is reached (determined by the `MAX_QUEUE_LENGTH` environment variable), the endpoint returns a `429 Too Many Requests` error.

## 6. Usage Notes

- The `video_urls` parameter must contain at least one video URL.
- The `webhook_url` parameter is optional and can be used to receive a notification when the video combination process is complete.
- The `id` parameter is optional and can be used to identify the request.

## 7. Common Issues

- Providing invalid video URLs or URLs that are not accessible.
- Attempting to combine video files with incompatible codecs or formats.
- Reaching the maximum queue length, which can cause requests to be rejected with a `429 Too Many Requests` error.

## 8. Best Practices

- Ensure that the provided video URLs are valid and accessible.
- Consider the video file formats and codecs when combining videos to avoid compatibility issues.
- Monitor the queue length and adjust the `MAX_QUEUE_LENGTH` environment variable as needed to prevent the queue from becoming overloaded.
- Implement error handling and retries for failed requests.