# Media Convert Endpoint Documentation

## 1. Overview

The `/v1/media/convert` endpoint is part of the Flask API application and is responsible for converting media files (audio or video) from one format to another. This endpoint fits into the overall API structure as a part of the `v1` blueprint, which contains various media-related functionalities.

## 2. Endpoint

**URL Path:** `/v1/media/convert`
**HTTP Method:** `POST`

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body must be a JSON object with the following properties:

- `media_url` (required, string): The URL of the media file to be converted.
- `format` (required, string): The desired output format for the converted media file.
- `video_codec` (optional, string): The video codec to be used for the conversion. Default is `libx264`.
- `video_preset` (optional, string): The video preset to be used for the conversion. Default is `medium`.
- `video_crf` (optional, number): The Constant Rate Factor (CRF) value for video encoding. Must be between 0 and 51. Default is 23.
- `audio_codec` (optional, string): The audio codec to be used for the conversion. Default is `aac`.
- `audio_bitrate` (optional, string): The audio bitrate to be used for the conversion. Default is `128k`.
- `webhook_url` (optional, string): The URL to receive a webhook notification upon completion of the conversion process.
- `id` (optional, string): An optional identifier for the conversion request.

### Example Request

```json
{
  "media_url": "https://example.com/video.mp4",
  "format": "avi",
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
  https://api.example.com/v1/media/convert \
  -H 'x-api-key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "media_url": "https://example.com/video.mp4",
    "format": "avi",
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

The success response will be a JSON object containing the URL of the converted media file uploaded to cloud storage, the endpoint path, and a status code of 200.

```json
{
  "code": 200,
  "id": "unique-request-id",
  "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "response": "https://cloud.example.com/converted-video.avi",
  "message": "success",
  "pid": 12345,
  "queue_id": 1234567890,
  "run_time": 10.234,
  "queue_time": 0.123,
  "total_time": 10.357,
  "queue_length": 0,
  "build_number": "1.0.0"
}
```

### Error Responses

- **400 Bad Request**: Returned when the request payload is missing or invalid.
- **401 Unauthorized**: Returned when the `x-api-key` header is missing or invalid.
- **500 Internal Server Error**: Returned when an unexpected error occurs during the conversion process.

Example error response:

```json
{
  "code": 400,
  "id": "unique-request-id",
  "job_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "message": "Invalid request payload",
  "pid": 12345,
  "queue_id": 1234567890,
  "queue_length": 0,
  "build_number": "1.0.0"
}
```

## 5. Error Handling

The endpoint uses the `validate_payload` decorator to validate the request payload against a JSON schema. If the payload is missing or invalid, a 400 Bad Request error is returned.

The `authenticate` decorator is used to ensure that the request includes a valid `x-api-key` header. If the header is missing or invalid, a 401 Unauthorized error is returned.

If an unexpected error occurs during the conversion process, a 500 Internal Server Error is returned, and the error is logged.

## 6. Usage Notes

- The `media_url` parameter must be a valid URL pointing to the media file to be converted.
- The `format` parameter must be a valid media format supported by the conversion process.
- The optional parameters (`video_codec`, `video_preset`, `video_crf`, `audio_codec`, `audio_bitrate`) allow you to customize the conversion settings.
- If the `webhook_url` parameter is provided, a webhook notification will be sent to the specified URL upon completion of the conversion process.
- The `id` parameter is optional and can be used to identify the conversion request.

## 7. Common Issues

- Providing an invalid or inaccessible `media_url`.
- Specifying an unsupported `format`.
- Providing invalid values for the optional parameters (e.g., `video_crf` outside the valid range).

## 8. Best Practices

- Always validate the input parameters on the client-side before sending the request.
- Use the `id` parameter to track and identify conversion requests.
- Provide a `webhook_url` to receive notifications about the conversion process completion.
- Monitor the API logs for any errors or issues during the conversion process.
- Consider implementing rate limiting or queue management to handle high volumes of requests.