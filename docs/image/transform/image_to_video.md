# Image to Video Endpoint Documentation

## 1. Overview

The `/v1/image/transform/video` endpoint is part of the Flask API application and is responsible for converting an image into a video file. This endpoint is registered in the `app.py` file under the `v1_image_transform_video_bp` blueprint, which is imported from the `routes.v1.image.transform.image_to_video` module.

## 2. Endpoint

**URL Path:** `/v1/image/transform/video`
**HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body must be a JSON object with the following properties:

| Parameter   | Type   | Required | Description                                                  |
|-------------|--------|----------|--------------------------------------------------------------|
| `image_url` | string | Yes      | The URL of the image to be converted into a video.          |
| `length`    | number | No       | The desired length of the video in seconds (default: 5).     |
| `frame_rate`| integer| No       | The frame rate of the output video (default: 30).           |
| `zoom_speed`| number | No       | The speed of the zoom effect (0-100, default: 3).           |
| `webhook_url`| string| No       | The URL to receive a webhook notification upon completion.  |
| `id`        | string | No       | An optional ID to associate with the request.               |

The `validate_payload` decorator in the `routes` file enforces the following JSON schema for the request body:

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
    "additionalProperties": False
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
     http://your-api-url/v1/image/transform/video
```

## 4. Response

### Success Response

Upon successful conversion, the endpoint returns a JSON response with the following structure:

```json
{
    "code": 200,
    "id": "request-123",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "response": "https://cloud-storage.example.com/converted-video.mp4",
    "message": "success",
    "run_time": 5.123,
    "queue_time": 0.456,
    "total_time": 5.579,
    "pid": 12345,
    "queue_id": 1234567890,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

The `response` field contains the URL of the converted video file uploaded to cloud storage.

### Error Responses

- **400 Bad Request**

```json
{
    "code": 400,
    "id": "request-123",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "message": "Invalid request payload",
    "pid": 12345,
    "queue_id": 1234567890,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

- **401 Unauthorized**

```json
{
    "code": 401,
    "id": "request-123",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "message": "Invalid API key",
    "pid": 12345,
    "queue_id": 1234567890,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

- **429 Too Many Requests**

```json
{
    "code": 429,
    "id": "request-123",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "message": "MAX_QUEUE_LENGTH (100) reached",
    "pid": 12345,
    "queue_id": 1234567890,
    "queue_length": 100,
    "build_number": "1.0.0"
}
```

- **500 Internal Server Error**

```json
{
    "code": 500,
    "id": "request-123",
    "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "message": "Error processing image to video: <error_message>",
    "pid": 12345,
    "queue_id": 1234567890,
    "queue_length": 0,
    "build_number": "1.0.0"
}
```

## 5. Error Handling

- **Missing or invalid parameters**: If the request payload is missing required parameters or contains invalid values, the endpoint returns a 400 Bad Request error.
- **Authentication error**: If the provided `x-api-key` header is missing or invalid, the endpoint returns a 401 Unauthorized error.
- **Queue limit reached**: If the maximum queue length (`MAX_QUEUE_LENGTH`) is set and the queue size reaches that limit, the endpoint returns a 429 Too Many Requests error.
- **Other errors**: Any other exceptions raised during the image-to-video conversion process will result in a 500 Internal Server Error response, with the error message included in the response body.

## 6. Usage Notes

- The `image_url` parameter must be a valid URL pointing to an image file.
- The `length` parameter specifies the duration of the output video in seconds and must be between 1 and 60.
- The `frame_rate` parameter determines the frame rate of the output video and must be between 15 and 60 frames per second.
- The `zoom_speed` parameter controls the speed of the zoom effect applied to the image during the video conversion. It is a value between 0 and 100, where 0 means no zoom, and 100 is the maximum zoom speed.
- If the `webhook_url` parameter is provided, a webhook notification will be sent to the specified URL upon completion of the conversion process.
- The `id` parameter is an optional identifier that can be associated with the request for tracking purposes.

## 7. Common Issues

- Providing an invalid or inaccessible `image_url`.
- Setting the `length` parameter to an extremely high value, which may result in long processing times or resource exhaustion.
- Specifying an unsupported image format.
- Network or connectivity issues that may cause the image download or video upload to fail.

## 8. Best Practices

- Validate the `image_url` parameter before submitting the request to ensure it points to a valid and accessible image file.
- Set reasonable values for the `length` and `frame_rate` parameters based on your requirements and available resources.
- Consider using the `webhook_url` parameter to receive notifications about the conversion process, especially for long-running or asynchronous requests.
- Implement proper error handling and retry mechanisms in your client application to handle potential failures or network issues.
- Monitor the API logs for any errors or warnings related to the image-to-video conversion process.
- Use the `id` parameter to associate requests with specific users, sessions, or other identifiers for better tracking and debugging.