# Media Cut Endpoint

## 1. Overview

The `/v1/media/cut` endpoint is part of the Flask API application and is designed to cut specified segments from a media file (video or audio) with optional encoding settings. This endpoint fits into the overall API structure as a part of the `v1` blueprint, which contains various media-related functionalities.

## 2. Endpoint

**URL Path:** `/v1/media/cut`
**HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body must be a JSON object with the following properties:

- `media_url` (required, string): The URL of the media file to be cut.
- `cuts` (required, array of objects): An array of cut segments, where each object has the following properties:
  - `start` (required, string): The start time of the cut segment in the format `hh:mm:ss.ms`.
  - `end` (required, string): The end time of the cut segment in the format `hh:mm:ss.ms`.
- `video_codec` (optional, string): The video codec to be used for encoding the output file. Default is `libx264`.
- `video_preset` (optional, string): The video preset to be used for encoding the output file. Default is `medium`.
- `video_crf` (optional, number): The Constant Rate Factor (CRF) value for video encoding. Must be between 0 and 51. Default is 23.
- `audio_codec` (optional, string): The audio codec to be used for encoding the output file. Default is `aac`.
- `audio_bitrate` (optional, string): The audio bitrate to be used for encoding the output file. Default is `128k`.
- `webhook_url` (optional, string): The URL to receive a webhook notification upon completion of the task.
- `id` (optional, string): A unique identifier for the request.

### Example Request

```json
{
  "media_url": "https://example.com/video.mp4",
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

```
curl -X POST \
  https://api.example.com/v1/media/cut \
  -H 'x-api-key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "media_url": "https://example.com/video.mp4",
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

The success response follows the general response structure defined in the `app.py` file. Here's an example:

```json
{
  "code": 200,
  "id": "unique-request-id",
  "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "response": {
    "file_url": "https://example.com/output.mp4"
  },
  "message": "success",
  "run_time": 5.234,
  "queue_time": 0.012,
  "total_time": 5.246,
  "pid": 12345,
  "queue_id": 1234567890,
  "queue_length": 0,
  "build_number": "1.0.0"
}
```

### Error Responses

- **400 Bad Request**: Returned when the request payload is missing or invalid.

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

- **500 Internal Server Error**: Returned when an unexpected error occurs on the server.

  ```json
  {
    "code": 500,
    "message": "Internal Server Error"
  }
  ```

## 5. Error Handling

The endpoint handles the following common errors:

- Missing or invalid request parameters: Returns a 400 Bad Request error.
- Authentication failure: Returns a 401 Unauthorized error if the `x-api-key` header is missing or invalid.
- Unexpected exceptions: Returns a 500 Internal Server Error if an unexpected exception occurs during the media cut process.

The main application context (`app.py`) also includes error handling for queue overload. If the maximum queue length is reached, the endpoint returns a 429 Too Many Requests error.

## 6. Usage Notes

- The `media_url` parameter must be a valid URL pointing to a media file (video or audio).
- The `cuts` parameter must be an array of objects, where each object specifies a start and end time for a cut segment in the format `hh:mm:ss.ms`.
- The optional encoding parameters (`video_codec`, `video_preset`, `video_crf`, `audio_codec`, `audio_bitrate`) can be used to customize the output file encoding settings.
- The `webhook_url` parameter is optional and can be used to receive a webhook notification upon completion of the task.
- The `id` parameter is optional and can be used to uniquely identify the request.

## 7. Common Issues

- Providing an invalid or inaccessible `media_url`.
- Providing invalid or out-of-range values for the encoding parameters.
- Providing overlapping or invalid cut segments in the `cuts` parameter.

## 8. Best Practices

- Validate the input parameters on the client-side before sending the request.
- Use the `webhook_url` parameter to receive notifications and handle the response asynchronously.
- Monitor the `queue_length` parameter in the response to manage the load on the API.
- Use the `id` parameter to correlate requests and responses for better tracking and debugging.