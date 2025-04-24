# Video Split Endpoint

## 1. Overview

The `/v1/video/split` endpoint is part of the Video API and is used to split a video file into multiple segments based on specified start and end times. This endpoint fits into the overall API structure as a part of the version 1 (`v1`) routes, specifically under the `video` category.

## 2. Endpoint

**URL Path:** `/v1/video/split`
**HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body must be a JSON object with the following properties:

- `video_url` (required, string): The URL of the video file to be split.
- `splits` (required, array of objects): An array of objects specifying the start and end times for each split. Each object must have the following properties:
  - `start` (required, string): The start time of the split in the format `hh:mm:ss.ms`.
  - `end` (required, string): The end time of the split in the format `hh:mm:ss.ms`.
- `video_codec` (optional, string): The video codec to use for encoding the split videos. Default is `libx264`.
- `video_preset` (optional, string): The video preset to use for encoding the split videos. Default is `medium`.
- `video_crf` (optional, number): The Constant Rate Factor (CRF) value for video encoding. Must be between 0 and 51. Default is 23.
- `audio_codec` (optional, string): The audio codec to use for encoding the split videos. Default is `aac`.
- `audio_bitrate` (optional, string): The audio bitrate to use for encoding the split videos. Default is `128k`.
- `webhook_url` (optional, string): The URL to receive a webhook notification when the split operation is complete.
- `id` (optional, string): A unique identifier for the request.

### Example Request

```json
{
  "video_url": "https://example.com/video.mp4",
  "splits": [
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
  https://api.example.com/v1/video/split \
  -H 'x-api-key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "video_url": "https://example.com/video.mp4",
    "splits": [
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

The success response follows the general response format specified in `app.py`. Here's an example:

```json
{
  "endpoint": "/v1/video/split",
  "code": 200,
  "id": "unique-request-id",
  "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "response": [
    {
      "file_url": "https://example.com/split-1.mp4"
    },
    {
      "file_url": "https://example.com/split-2.mp4"
    }
  ],
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

The `response` field contains an array of objects, each representing a split video file. Each object has a `file_url` property containing the URL of the split video file.

### Error Responses

- **400 Bad Request**: Returned when the request payload is missing or invalid.
- **401 Unauthorized**: Returned when the `x-api-key` header is missing or invalid.
- **429 Too Many Requests**: Returned when the maximum queue length has been reached.
- **500 Internal Server Error**: Returned when an unexpected error occurs during the video split process.

Example error response:

```json
{
  "code": 400,
  "id": "unique-request-id",
  "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "message": "Invalid request payload: 'splits' is a required property",
  "pid": 12345,
  "queue_id": 6789,
  "queue_length": 2,
  "build_number": "1.0.0"
}
```

## 5. Error Handling

The endpoint handles the following common errors:

- Missing or invalid request parameters: Returns a 400 Bad Request error with a descriptive error message.
- Authentication failure: Returns a 401 Unauthorized error if the `x-api-key` header is missing or invalid.
- Queue length exceeded: Returns a 429 Too Many Requests error if the maximum queue length has been reached.
- Unexpected exceptions: Returns a 500 Internal Server Error with the exception message.

The main application context (`app.py`) also includes error handling for queue length limits and webhook notifications.

## 6. Usage Notes

- The `video_url` parameter must be a valid URL pointing to a video file.
- The `splits` array must contain at least one object specifying the start and end times for a split.
- The start and end times must be in the format `hh:mm:ss.ms` (hours:minutes:seconds.milliseconds).
- The `video_codec`, `video_preset`, `video_crf`, `audio_codec`, and `audio_bitrate` parameters are optional and can be used to customize the encoding settings for the split videos.
- If the `webhook_url` parameter is provided, a webhook notification will be sent to the specified URL when the split operation is complete.
- The `id` parameter is optional and can be used to uniquely identify the request.

## 7. Common Issues

- Providing an invalid or inaccessible `video_url`.
- Specifying overlapping or invalid start and end times in the `splits` array.
- Exceeding the maximum queue length, which can result in a 429 Too Many Requests error.

## 8. Best Practices

- Validate the `video_url` parameter before sending the request to ensure it points to a valid video file.
- Ensure that the start and end times in the `splits` array are correctly formatted and do not overlap.
- Consider using the `webhook_url` parameter to receive notifications about the completion of the split operation, especially for long-running or asynchronous requests.
- Implement retry mechanisms and error handling in your client application to handle potential errors and failures.
- Monitor the queue length and adjust the `MAX_QUEUE_LENGTH` environment variable as needed to prevent excessive queuing and potential timeouts.