# Video Cut Endpoint

## 1. Overview

The `/v1/video/cut` endpoint is part of the Video API and allows users to cut specified segments from a video file with optional encoding settings. This endpoint fits into the overall API structure as a part of the version 1 (`v1`) routes, specifically under the `video` category.

## 2. Endpoint

```
POST /v1/video/cut
```

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body must be a JSON object with the following properties:

- `video_url` (required, string): The URL of the video file to be cut.
- `cuts` (required, array of objects): An array of cut segments, where each object has the following properties:
  - `start` (required, string): The start time of the cut segment in the format `hh:mm:ss.ms`.
  - `end` (required, string): The end time of the cut segment in the format `hh:mm:ss.ms`.
- `video_codec` (optional, string): The video codec to use for encoding the output video. Default is `libx264`.
- `video_preset` (optional, string): The video preset to use for encoding the output video. Default is `medium`.
- `video_crf` (optional, number): The Constant Rate Factor (CRF) value for video encoding. Must be between 0 and 51. Default is 23.
- `audio_codec` (optional, string): The audio codec to use for encoding the output video. Default is `aac`.
- `audio_bitrate` (optional, string): The audio bitrate to use for encoding the output video. Default is `128k`.
- `webhook_url` (optional, string): The URL to receive a webhook notification when the job is completed.
- `id` (optional, string): A unique identifier for the request.

### Example Request

```json
{
  "video_url": "https://example.com/video.mp4",
  "cuts": [
    {
      "start": "00:00:10.000",
      "end": "00:00:20.000"
    },
    {
      "start": "00:00:30.000",
      "end": "00:00:40.000"
    }
  ],
  "video_codec": "libx264",
  "video_preset": "medium",
  "video_crf": 23,
  "audio_codec": "aac",
  "audio_bitrate": "128k",
  "webhook_url": "https://example.com/webhook",
  "id": "unique-request-id"
}
```

```bash
curl -X POST \
  https://api.example.com/v1/video/cut \
  -H 'x-api-key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "video_url": "https://example.com/video.mp4",
    "cuts": [
      {
        "start": "00:00:10.000",
        "end": "00:00:20.000"
      },
      {
        "start": "00:00:30.000",
        "end": "00:00:40.000"
      }
    ],
    "video_codec": "libx264",
    "video_preset": "medium",
    "video_crf": 23,
    "audio_codec": "aac",
    "audio_bitrate": "128k",
    "webhook_url": "https://example.com/webhook",
    "id": "unique-request-id"
  }'
```

## 4. Response

### Success Response

The response follows the general response format defined in the main application context (`app.py`). Here's an example of a successful response:

```json
{
  "endpoint": "/v1/video/cut",
  "code": 200,
  "id": "unique-request-id",
  "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "response": "https://example.com/processed-video.mp4",
  "message": "success",
  "pid": 12345,
  "queue_id": 6789,
  "run_time": 5.234,
  "queue_time": 0.123,
  "total_time": 5.357,
  "queue_length": 0,
  "build_number": "1.0.0"
}
```

The `response` field contains the URL of the processed video file.

### Error Responses

- **400 Bad Request**

  ```json
  {
    "code": 400,
    "message": "Invalid request payload"
  }
  ```

  This error occurs when the request payload is missing required fields or contains invalid data.

- **401 Unauthorized**

  ```json
  {
    "code": 401,
    "message": "Invalid API key"
  }
  ```

  This error occurs when the provided `x-api-key` header is missing or invalid.

- **429 Too Many Requests**

  ```json
  {
    "code": 429,
    "id": "unique-request-id",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "message": "MAX_QUEUE_LENGTH (100) reached",
    "pid": 12345,
    "queue_id": 6789,
    "queue_length": 100,
    "build_number": "1.0.0"
  }
  ```

  This error occurs when the maximum queue length has been reached, and the request cannot be processed immediately.

- **500 Internal Server Error**

  ```json
  {
    "code": 500,
    "message": "An error occurred during video processing"
  }
  ```

  This error occurs when an unexpected error occurs during the video processing or encoding.

## 5. Error Handling

The endpoint handles the following common errors:

- **Missing or invalid request parameters**: If any required parameters are missing or invalid, the endpoint returns a 400 Bad Request error with an appropriate error message.
- **Invalid API key**: If the provided `x-api-key` header is missing or invalid, the endpoint returns a 401 Unauthorized error.
- **Queue limit reached**: If the maximum queue length has been reached, the endpoint returns a 429 Too Many Requests error with the current queue length and the maximum queue length.
- **Unexpected errors during video processing**: If an unexpected error occurs during the video processing or encoding, the endpoint returns a 500 Internal Server Error with a generic error message.

The main application context (`app.py`) also includes error handling for the queue system and webhook notifications.

## 6. Usage Notes

- The `video_url` parameter must be a valid URL that points to a video file accessible by the server.
- The `cuts` parameter must be an array of objects, where each object represents a cut segment with a start and end time in the format `hh:mm:ss.ms`.
- The optional encoding parameters (`video_codec`, `video_preset`, `video_crf`, `audio_codec`, `audio_bitrate`) allow you to customize the encoding settings for the output video file.
- If the `webhook_url` parameter is provided, the server will send a webhook notification to the specified URL when the job is completed.
- The `id` parameter can be used to associate the request with a unique identifier for tracking purposes.

## 7. Common Issues

- Providing an invalid or inaccessible `video_url`.
- Specifying overlapping or invalid cut segments in the `cuts` parameter.
- Providing invalid encoding settings that are not supported by the server.
- Reaching the maximum queue length, which can cause requests to be rejected with a 429 Too Many Requests error.

## 8. Best Practices

- Validate the `video_url` parameter before sending the request to ensure it points to a valid and accessible video file.
- Ensure that the cut segments in the `cuts` parameter are correctly formatted and do not overlap or exceed the duration of the video.
- Use the optional encoding parameters judiciously, as they can impact the processing time and output video quality.
- Implement retry mechanisms for handling 429 Too Many Requests errors, as the queue length may fluctuate over time.
- Monitor the webhook notifications or poll the server for job status updates to track the progress of long-running jobs.