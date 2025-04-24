# Video Trim Endpoint

## 1. Overview

The `/v1/video/trim` endpoint is part of the Video API and allows users to trim a video by removing specified portions from the beginning and/or end. It also provides optional encoding settings to control the output video quality. This endpoint fits into the overall API structure as a part of the version 1 (`v1`) routes, specifically under the `video` category.

## 2. Endpoint

**URL Path:** `/v1/video/trim`
**HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

- `video_url` (required, string): The URL of the video file to be trimmed.
- `start` (optional, string): The start time for trimming in the format `hh:mm:ss` or `mm:ss`.
- `end` (optional, string): The end time for trimming in the format `hh:mm:ss` or `mm:ss`.
- `video_codec` (optional, string): The video codec to be used for encoding the output video. Default is `libx264`.
- `video_preset` (optional, string): The video preset to be used for encoding the output video. Default is `medium`.
- `video_crf` (optional, number): The Constant Rate Factor (CRF) value for video encoding, ranging from 0 to 51. Default is 23.
- `audio_codec` (optional, string): The audio codec to be used for encoding the output video. Default is `aac`.
- `audio_bitrate` (optional, string): The audio bitrate to be used for encoding the output video. Default is `128k`.
- `webhook_url` (optional, string): The URL to receive a webhook notification upon completion of the task.
- `id` (optional, string): A unique identifier for the request.

The `validate_payload` directive in the routes file ensures that the request payload adheres to the specified schema, which includes the required and optional parameters, their data types, and any additional constraints.

### Example Request

```json
{
  "video_url": "https://example.com/video.mp4",
  "start": "00:01:00",
  "end": "00:03:00",
  "video_codec": "libx264",
  "video_preset": "faster",
  "video_crf": 28,
  "audio_codec": "aac",
  "audio_bitrate": "128k",
  "webhook_url": "https://example.com/webhook",
  "id": "unique-request-id"
}
```

```bash
curl -X POST \
  https://api.example.com/v1/video/trim \
  -H 'x-api-key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "video_url": "https://example.com/video.mp4",
    "start": "00:01:00",
    "end": "00:03:00",
    "video_codec": "libx264",
    "video_preset": "faster",
    "video_crf": 28,
    "audio_codec": "aac",
    "audio_bitrate": "128k",
    "webhook_url": "https://example.com/webhook",
    "id": "unique-request-id"
  }'
```

## 4. Response

### Success Response

The success response follows the general response structure defined in the `app.py` file. Here's an example:

```json
{
  "endpoint": "/v1/video/trim",
  "code": 200,
  "id": "unique-request-id",
  "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "response": "https://example.com/trimmed-video.mp4",
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

### Error Responses

- **400 Bad Request**: Returned when the request payload is missing or contains invalid parameters.

  ```json
  {
    "code": 400,
    "message": "Invalid request payload"
  }
  ```

- **401 Unauthorized**: Returned when the `x-api-key` header is missing or invalid.

  ```json
  {
    "code": 401,
    "message": "Unauthorized"
  }
  ```

- **500 Internal Server Error**: Returned when an unexpected error occurs during the video trimming process.

  ```json
  {
    "code": 500,
    "message": "An error occurred during the video trimming process"
  }
  ```

## 5. Error Handling

The endpoint handles common errors such as missing or invalid parameters by returning appropriate HTTP status codes and error messages. The `validate_payload` decorator ensures that the request payload adheres to the specified schema, and any violations will result in a 400 Bad Request error.

The main application context (`app.py`) includes error handling for the task queue. If the maximum queue length is reached, the endpoint will return a 429 Too Many Requests error with a corresponding message.

## 6. Usage Notes

- The `start` and `end` parameters are optional, but at least one of them must be provided to perform the trimming operation.
- The `video_codec`, `video_preset`, `video_crf`, `audio_codec`, and `audio_bitrate` parameters are optional and allow users to customize the encoding settings for the output video.
- The `webhook_url` parameter is optional and can be used to receive a notification when the task is completed.
- The `id` parameter is optional and can be used to uniquely identify the request.

## 7. Common Issues

- Providing an invalid or inaccessible `video_url`.
- Specifying invalid or unsupported values for the encoding parameters (`video_codec`, `video_preset`, `video_crf`, `audio_codec`, `audio_bitrate`).
- Encountering issues with the video trimming process due to unsupported video formats or corrupted files.

## 8. Best Practices

- Validate the `video_url` parameter to ensure it points to a valid and accessible video file.
- Use appropriate encoding settings based on the desired output quality and file size requirements.
- Implement error handling and retry mechanisms for failed requests or network issues.
- Monitor the task queue length and adjust the `MAX_QUEUE_LENGTH` value accordingly to prevent overloading the system.
- Implement rate limiting or throttling mechanisms to prevent abuse or excessive requests.