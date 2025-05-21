# Image to Video Conversion

## 1. Overview

The `/v1/image/convert/video` endpoint is part of the Flask API application and is responsible for converting an image into a video file. This endpoint is registered in the `app.py` file under the `v1_image_convert_video_bp` blueprint, which is imported from the `routes.v1.image.convert.image_to_video` module.

## 2. Endpoint

**URL Path:** `/v1/image/convert/video`
**HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body must be in JSON format and should include the following parameters:

| Parameter   | Type   | Required | Description                                                  |
|-------------|--------|----------|--------------------------------------------------------------|
| `image_url` | string | Yes      | The URL of the image to be converted into a video.          |
| `length`    | number | No       | The desired length of the video in seconds (default: 5).    |
| `frame_rate`| integer| No       | The frame rate of the output video (default: 30).           |
| `zoom_speed`| number | No       | The speed of the zoom effect (0-100, default: 3).           |
| `webhook_url`| string| No       | The URL to receive a webhook notification upon completion.  |
| `id`        | string | No       | An optional identifier for the request.                      |

The `validate_payload` decorator in the `routes.v1.image.convert.image_to_video` module enforces the following JSON schema for the request body:

```json
{
    "type": "object",
    "properties": {
        "image_url": {"type": "string", "format": "uri"},
        "length": {"type": "number", "minimum": 1, "maximum": 60},
        "frame_rate": {"type": "integer", "minimum": 15, "maximum": 60},
        "zoom_speed": {"type": "number", "minimum": 0, "maximum": 100},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["image_url"],
    "additionalProperties": false
}
```

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
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"image_url": "https://example.com/image.jpg", "length": 10, "frame_rate": 24, "zoom_speed": 5, "webhook_url": "https://example.com/webhook", "id": "request-123"}' \
     http://your-api-endpoint/v1/image/convert/video
```

## 4. Response

### Success Response

Upon successful processing, the endpoint returns a JSON response with the following structure:

```json
{
    "code": 200,
    "id": "request-123",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "response": "https://cloud-storage.example.com/converted-video.mp4",
    "message": "success",
    "run_time": 2.345,
    "queue_time": 0.123,
    "total_time": 2.468,
    "pid": 12345,
    "queue_id": 1234567890,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

The `response` field contains the URL of the converted video file uploaded to cloud storage.

### Error Responses

#### 429 Too Many Requests

If the maximum queue length is reached, the endpoint returns a 429 Too Many Requests response:

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

#### 500 Internal Server Error

If an exception occurs during the image-to-video conversion process, the endpoint returns a 500 Internal Server Error response:

```json
{
    "code": 500,
    "id": "request-123",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "message": "Error message describing the exception",
    "pid": 12345,
    "queue_id": 1234567890,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

## 5. Error Handling

The endpoint handles the following types of errors:

- **Missing or invalid parameters**: If the request body is missing required parameters or contains invalid parameter values, the `validate_payload` decorator will return a 400 Bad Request response with a descriptive error message.
- **Queue length exceeded**: If the maximum queue length is reached and the `bypass_queue` parameter is set to `False`, the endpoint returns a 429 Too Many Requests response.
- **Exceptions during processing**: If an exception occurs during the image-to-video conversion process, the endpoint returns a 500 Internal Server Error response with the error message.

## 6. Usage Notes

- The `image_url` parameter must be a valid URL pointing to an image file.
- The `length` parameter specifies the duration of the output video in seconds and must be between 1 and 60.
- The `frame_rate` parameter specifies the frame rate of the output video and must be between 15 and 60.
- The `zoom_speed` parameter controls the speed of the zoom effect and must be between 0 and 100.
- The `webhook_url` parameter is optional and can be used to receive a notification when the conversion is complete.
- The `id` parameter is optional and can be used to identify the request.

## 7. Common Issues

- Providing an invalid or inaccessible `image_url` will result in an error during processing.
- Specifying invalid parameter values outside the allowed ranges will result in a 400 Bad Request response.
- If the maximum queue length is reached and the `bypass_queue` parameter is set to `False`, the request will be rejected with a 429 Too Many Requests response.

## 8. Best Practices

- Validate the `image_url` parameter before sending the request to ensure it points to a valid and accessible image file.
- Use the `webhook_url` parameter to receive notifications about the completion of the conversion process, rather than polling the API repeatedly.
- Provide the `id` parameter to easily identify and track the request in logs or notifications.
- Consider setting the `bypass_queue` parameter to `True` for time-sensitive requests to bypass the queue and process the request immediately.
