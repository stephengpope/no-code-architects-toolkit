# Audio Concatenation Endpoint

## 1. Overview

The `/v1/audio/concatenate` endpoint is a part of the Audio API and is responsible for combining multiple audio files into a single audio file. This endpoint fits into the overall API structure as a part of the version 1 (v1) routes, specifically under the `/v1/audio` namespace.

## 2. Endpoint

**URL Path:** `/v1/audio/concatenate`
**HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body must be a JSON object with the following properties:

- `audio_urls` (required, array of objects): An array of audio URLs to be concatenated. Each object in the array must have a `audio_url` property (string, URI format) containing the URL of the audio file.
- `webhook_url` (optional, string, URI format): The URL to which the response should be sent as a webhook.
- `id` (optional, string): An identifier for the request.

The `validate_payload` decorator in the routes file enforces the following JSON schema for the request body:

```json
{
    "type": "object",
    "properties": {
        "audio_urls": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "audio_url": {"type": "string", "format": "uri"}
                },
                "required": ["audio_url"]
            },
            "minItems": 1
        },
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["audio_urls"],
    "additionalProperties": False
}
```

### Example Request

```json
{
    "audio_urls": [
        {"audio_url": "https://example.com/audio1.mp3"},
        {"audio_url": "https://example.com/audio2.mp3"},
        {"audio_url": "https://example.com/audio3.mp3"}
    ],
    "webhook_url": "https://example.com/webhook",
    "id": "request-123"
}
```

```bash
curl -X POST \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
        "audio_urls": [
            {"audio_url": "https://example.com/audio1.mp3"},
            {"audio_url": "https://example.com/audio2.mp3"},
            {"audio_url": "https://example.com/audio3.mp3"}
        ],
        "webhook_url": "https://example.com/webhook",
        "id": "request-123"
     }' \
     https://your-api-endpoint.com/v1/audio/concatenate
```

## 4. Response

### Success Response

The success response follows the general response format defined in the `app.py` file. Here's an example:

```json
{
    "endpoint": "/v1/audio/concatenate",
    "code": 200,
    "id": "request-123",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "response": "https://cloud-storage.example.com/combined-audio.mp3",
    "message": "success",
    "pid": 12345,
    "queue_id": 6789,
    "run_time": 10.234,
    "queue_time": 2.345,
    "total_time": 12.579,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

The `response` field contains the URL of the combined audio file uploaded to cloud storage.

### Error Responses

- **400 Bad Request**: Returned when the request body is missing or invalid.

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

- **429 Too Many Requests**: Returned when the maximum queue length is reached.

  ```json
  {
    "code": 429,
    "id": "request-123",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "message": "MAX_QUEUE_LENGTH (100) reached",
    "pid": 12345,
    "queue_id": 6789,
    "queue_length": 100,
    "build_number": "1.0.0"
  }
  ```

- **500 Internal Server Error**: Returned when an unexpected error occurs during the audio concatenation process.

  ```json
  {
    "code": 500,
    "message": "An error occurred during audio concatenation"
  }
  ```

## 5. Error Handling

The endpoint handles the following common errors:

- **Missing or invalid request body**: If the request body is missing or does not conform to the expected JSON schema, a 400 Bad Request error is returned.
- **Missing or invalid API key**: If the `x-api-key` header is missing or invalid, a 401 Unauthorized error is returned.
- **Queue length exceeded**: If the maximum queue length is reached (determined by the `MAX_QUEUE_LENGTH` environment variable), a 429 Too Many Requests error is returned.
- **Unexpected errors during audio concatenation**: If an unexpected error occurs during the audio concatenation process, a 500 Internal Server Error is returned with the error message.

The main application context (`app.py`) also includes error handling for the task queue. If the queue length exceeds the `MAX_QUEUE_LENGTH` limit, the request is rejected with a 429 Too Many Requests error.

## 6. Usage Notes

- The audio files to be concatenated must be accessible via the provided URLs.
- The order of the audio files in the `audio_urls` array determines the order in which they will be concatenated.
- If the `webhook_url` parameter is provided, the response will be sent as a webhook to the specified URL.
- The `id` parameter can be used to identify the request in the response.

## 7. Common Issues

- Providing invalid or inaccessible audio URLs.
- Exceeding the maximum queue length, which can lead to requests being rejected with a 429 Too Many Requests error.
- Encountering unexpected errors during the audio concatenation process, which can result in a 500 Internal Server Error.

## 8. Best Practices

- Validate the audio URLs before sending the request to ensure they are accessible and in the correct format.
- Monitor the queue length and adjust the `MAX_QUEUE_LENGTH` value accordingly to prevent requests from being rejected due to a full queue.
- Implement retry mechanisms for handling temporary errors or failures during the audio concatenation process.
- Provide meaningful and descriptive `id` values to easily identify requests in the response.
-