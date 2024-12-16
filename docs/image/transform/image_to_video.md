# Image to Video Endpoint

## 1. Overview

The `/v1/image/transform/video` endpoint is a part of the Flask API application and is responsible for converting an image into a video file. This endpoint is registered in the `app.py` file under the `v1_image_transform_video_bp` blueprint.

## 2. Endpoint

**URL Path:** `/v1/image/transform/video`
**HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body must be a JSON object with the following properties:

- `image_url` (required, string): The URL of the image to be converted into a video.
- `length` (optional, number): The desired length of the video in seconds. Default is 5 seconds. Minimum value is 1, and maximum value is 60.
- `frame_rate` (optional, integer): The frame rate of the output video. Default is 30 frames per second. Minimum value is 15, and maximum value is 60.
- `zoom_speed` (optional, number): The speed at which the image should zoom in or out during the video. Default is 3%. Minimum value is 0, and maximum value is 100.
- `webhook_url` (optional, string): The URL to which a webhook notification should be sent upon completion of the video conversion.
- `id` (optional, string): A unique identifier for the request.

### Example Request

```json
{
    "image_url": "https://example.com/image.jpg",
    "length": 10,
    "frame_rate": 24,
    "zoom_speed": 5,
    "webhook_url": "https://example.com/webhook",
    "id": "unique-request-id"
}
```

```bash
curl -X POST \
     -H "x-api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"image_url": "https://example.com/image.jpg", "length": 10, "frame_rate": 24, "zoom_speed": 5, "webhook_url": "https://example.com/webhook", "id": "unique-request-id"}' \
     http://your-api-url/v1/image/transform/video
```

## 4. Response

### Success Response

**Status Code:** `200 OK`

```json
{
    "response": "https://cloud-storage.example.com/converted-video.mp4",
    "endpoint": "/v1/image/transform/video",
    "code": 200
}
```

### Error Responses

**Status Code:** `400 Bad Request`

```json
{
    "message": "Invalid request payload",
    "endpoint": "/v1/image/transform/video",
    "code": 400
}
```

**Status Code:** `401 Unauthorized`

```json
{
    "message": "Missing or invalid API key",
    "endpoint": "/v1/image/transform/video",
    "code": 401
}
```

**Status Code:** `500 Internal Server Error`

```json
{
    "message": "An error occurred while processing the request",
    "endpoint": "/v1/image/transform/video",
    "code": 500
}
```

## 5. Error Handling

The endpoint uses the `validate_payload` decorator to validate the request payload against a JSON schema. If the payload is invalid, a `400 Bad Request` error is returned.

The `authenticate` decorator is used to verify the `x-api-key` header. If the API key is missing or invalid, a `401 Unauthorized` error is returned.

If an exception occurs during the image-to-video conversion process, a `500 Internal Server Error` is returned, and the error is logged with the `logger.error` function.

The main application context (`app.py`) includes error handling for the task queue. If the maximum queue length is reached, a `429 Too Many Requests` error is returned.

## 6. Usage Notes

- The `image_url` parameter must be a valid URL pointing to an image file.
- The `length` parameter specifies the duration of the output video in seconds.
- The `frame_rate` parameter determines the number of frames per second in the output video.
- The `zoom_speed` parameter controls the speed at which the image zooms in or out during the video. A value of 0 means no zooming, and a value of 100 means the image will zoom in or out at the maximum speed.
- The `webhook_url` parameter is optional and can be used to receive a notification when the video conversion is complete.
- The `id` parameter is optional and can be used to uniquely identify the request.

## 7. Common Issues

- Providing an invalid or inaccessible `image_url`.
- Specifying invalid or out-of-range values for `length`, `frame_rate`, or `zoom_speed`.
- Reaching the maximum queue length, which will result in a `429 Too Many Requests` error.

## 8. Best Practices

- Validate the `image_url` parameter before sending the request to ensure it points to a valid and accessible image file.
- Use appropriate values for `length`, `frame_rate`, and `zoom_speed` based on your requirements and the capabilities of your system.
- Consider implementing rate limiting or queue management strategies to prevent overloading the server with too many requests.
- Monitor the application logs for any errors or issues that may occur during the image-to-video conversion process.