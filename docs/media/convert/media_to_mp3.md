# Media to MP3 Conversion

The `/v1/media/convert/mp3` endpoint is part of the Flask API application and is responsible for converting various media files into MP3 format. This endpoint is registered in the `app.py` file under the `v1_media_convert_mp3_bp` blueprint.

## Endpoint Details

**URL Path:** `/v1/media/convert/mp3`

## 1. Overview

The `/v1/media/convert/mp3` endpoint is a part of the API's media transformation functionality. It allows users to convert various media files (audio or video) to MP3 format. This endpoint fits into the overall API structure as a part of the `v1` namespace, which represents the first version of the API.

## 2. Endpoint

```
POST /v1/media/convert/mp3
```

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

- `media_url` (required, string): The URL of the media file to be converted.
- `webhook_url` (optional, string): The URL to receive a webhook notification upon completion.
- `id` (optional, string): A unique identifier for the request.
- `bitrate` (optional, string): The desired bitrate for the output MP3 file, in the format `<value>k` (e.g., `128k`). If not provided, defaults to `128k`.

The `validate_payload` directive in the routes file enforces the following JSON schema for the request body:

```json
{
    "type": "object",
    "properties": {
        "media_url": {"type": "string", "format": "uri"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"},
        "bitrate": {"type": "string", "pattern": "^[0-9]+k$"}
    },
    "required": ["media_url"],
    "additionalProperties": False
}
```

### Example Request

```json
{
    "media_url": "https://example.com/video.mp4",
    "webhook_url": "https://example.com/webhook",
    "id": "unique-request-id",
    "bitrate": "192k"
}
```

```bash
curl -X POST \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"media_url": "https://example.com/video.mp4", "webhook_url": "https://example.com/webhook", "id": "unique-request-id", "bitrate": "192k"}' \
     https://your-api-endpoint.com/v1/media/convert/mp3
```

## 4. Response

### Success Response

The success response follows the general response structure defined in `app.py`. Here's an example:

```json
{
    "endpoint": "/v1/media/convert/mp3",
    "code": 200,
    "id": "unique-request-id",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "response": "https://cloud-storage.example.com/converted-file.mp3",
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

- **400 Bad Request**: Returned when the request payload is invalid or missing required parameters.
- **401 Unauthorized**: Returned when the `x-api-key` header is missing or invalid.
- **500 Internal Server Error**: Returned when an unexpected error occurs during the conversion process.

Example error response:

```json
{
    "code": 400,
    "id": "unique-request-id",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "message": "Invalid request payload: 'media_url' is a required property",
    "pid": 12345,
    "queue_id": 6789,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

## 5. Error Handling

The endpoint handles the following common errors:

- Missing or invalid `media_url` parameter: Returns a 400 Bad Request error.
- Invalid `bitrate` parameter: Returns a 400 Bad Request error.
- Authentication failure: Returns a 401 Unauthorized error.
- Unexpected exceptions during the conversion process: Returns a 500 Internal Server Error.

Additionally, the main application context (`app.py`) includes error handling for queue overload. If the maximum queue length is reached, the endpoint will return a 429 Too Many Requests error.

## 6. Usage Notes

- The `media_url` parameter should point to a valid media file (audio or video) that can be converted to MP3 format.
- If the `webhook_url` parameter is provided, a webhook notification will be sent to the specified URL upon completion of the conversion process.
- The `id` parameter can be used to uniquely identify the request, which can be helpful for tracking and logging purposes.
- The `bitrate` parameter allows you to specify the desired bitrate for the output MP3 file. If not provided, the default bitrate of 128k will be used.

## 7. Common Issues

- Providing an invalid or inaccessible `media_url`.
- Attempting to convert unsupported media formats.
- Exceeding the maximum queue length, resulting in a 429 Too Many Requests error.

## 8. Best Practices

- Validate the `media_url` parameter before sending the request to ensure it points to a valid and accessible media file.
- Consider providing a `webhook_url` parameter to receive notifications about the conversion process completion.
- Use a unique `id` parameter for each request to facilitate tracking and logging.
- Implement retry mechanisms in case of transient errors or queue overload situations.
- Monitor the API logs for any errors or issues during the conversion process.