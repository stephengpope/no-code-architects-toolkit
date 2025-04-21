# Silence Detection Endpoint

## 1. Overview

The `/v1/media/silence` endpoint is part of the Media API and is designed to detect silence intervals in a given media file. It takes a media URL, along with various parameters for configuring the silence detection process, and returns the detected silence intervals. This endpoint fits into the overall API structure as a part of the version 1 (v1) media-related endpoints.

## 2. Endpoint

```
POST /v1/media/silence
```

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body should be a JSON object with the following parameters:

- `media_url` (required, string): The URL of the media file to be processed.
- `start` (optional, string): The start time for the silence detection process, in the format `HH:MM:SS.ms`. If not provided, the process will start from the beginning of the media file.
- `end` (optional, string): The end time for the silence detection process, in the format `HH:MM:SS.ms`. If not provided, the process will continue until the end of the media file.
- `noise` (optional, string): The noise threshold for silence detection, in decibels (dB). Default is `-30dB`.
- `duration` (required, number): The minimum duration (in seconds) for a silence interval to be considered valid.
- `mono` (optional, boolean): Whether to process the audio as mono (single channel) or not. Default is `true`.
- `webhook_url` (required, string): The URL to which the response should be sent as a webhook.
- `id` (required, string): A unique identifier for the request.

The `validate_payload` directive in the routes file enforces the following JSON schema for the request body:

```python
{
    "type": "object",
    "properties": {
        "media_url": {"type": "string", "format": "uri"},
        "start": {"type": "string"},
        "end": {"type": "string"},
        "noise": {"type": "string"},
        "duration": {"type": "number", "minimum": 0.1},
        "mono": {"type": "boolean"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["media_url", "duration"],
    "additionalProperties": False
}
```

### Example Request

```json
{
    "media_url": "https://example.com/audio.mp3",
    "start": "00:00:10.0",
    "end": "00:01:00.0",
    "noise": "-25dB",
    "duration": 0.5,
    "mono": false,
    "webhook_url": "https://example.com/webhook",
    "id": "unique-request-id"
}
```

```
curl -X POST \
  https://api.example.com/v1/media/silence \
  -H 'x-api-key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "media_url": "https://example.com/audio.mp3",
    "start": "00:00:10.0",
    "end": "00:01:00.0",
    "noise": "-25dB",
    "duration": 0.5,
    "mono": false,
    "webhook_url": "https://example.com/webhook",
    "id": "unique-request-id"
}'
```

## 4. Response

### Success Response

The success response will be sent as a webhook to the specified `webhook_url`. The response format follows the general response structure defined in the main application context (`app.py`). Here's an example:

```json
{
    "endpoint": "/v1/media/silence",
    "code": 200,
    "id": "unique-request-id",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "response": [
        {
            "start": 10.5,
            "end": 15.2
        },
        {
            "start": 20.0,
            "end": 25.7
        }
    ],
    "message": "success",
    "pid": 12345,
    "queue_id": 1234567890,
    "run_time": 1.234,
    "queue_time": 0.123,
    "total_time": 1.357,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

### Error Responses

- **400 Bad Request**: This error is returned when the request body is missing or contains invalid parameters. Example response:

```json
{
    "code": 400,
    "message": "Invalid request payload"
}
```

- **401 Unauthorized**: This error is returned when the `x-api-key` header is missing or invalid. Example response:

```json
{
    "code": 401,
    "message": "Unauthorized"
}
```

- **500 Internal Server Error**: This error is returned when an unexpected error occurs during the silence detection process. Example response:

```json
{
    "code": 500,
    "message": "An error occurred during the silence detection process"
}
```

## 5. Error Handling

The endpoint handles the following common errors:

- Missing or invalid request parameters: Returns a 400 Bad Request error.
- Missing or invalid `x-api-key` header: Returns a 401 Unauthorized error.
- Unexpected exceptions during the silence detection process: Returns a 500 Internal Server Error.

The main application context (`app.py`) also includes error handling for situations where the task queue has reached its maximum length (`MAX_QUEUE_LENGTH`). In such cases, a 429 Too Many Requests error is returned.

## 6. Usage Notes

- The `media_url` parameter should point to a valid media file that can be processed by the silence detection service.
- The `start` and `end` parameters are optional and can be used to specify a time range within the media file for silence detection.
- The `noise` parameter allows you to adjust the noise threshold for silence detection. Lower values (e.g., `-40dB`) will detect more silence intervals, while higher values (e.g., `-20dB`) will detect fewer silence intervals.
- The `duration` parameter specifies the minimum duration (in seconds) for a silence interval to be considered valid. This can be useful for filtering out very short silence intervals that may not be relevant.
- The `mono` parameter determines whether the audio should be processed as a single channel (mono) or multiple channels (stereo or surround).

## 7. Common Issues

- Providing an invalid or inaccessible `media_url`.
- Specifying `start` and `end` times that are outside the duration of the media file.
- Setting the `duration` parameter to an unreasonably low value, which may result in detecting too many short silence intervals.

## 8. Best Practices

- Validate the `media_url` parameter to ensure it points to a valid and accessible media file.
- Consider using the `start` and `end` parameters to focus the silence detection on a specific time range within the media file, if needed.
- Adjust the `noise` and `duration` parameters based on your specific use case and requirements for silence detection.
- If you need to process stereo or surround audio, set the `mono` parameter to `false`.
- Monitor the response from the endpoint to ensure that the silence detection process completed successfully and that the detected silence intervals meet your expectations.