# `/v1/media/transform/mp3` API Documentation

## Overview
This endpoint allows you to convert media files (such as video or audio) to MP3 format. The conversion process is handled asynchronously, and the converted MP3 file is uploaded to cloud storage. The endpoint returns the cloud storage URL of the converted file upon successful completion.

## Endpoint
**URL Path:** `/v1/media/transform/mp3`
**HTTP Method:** `POST`

## Request

### Headers
- `Authorization` (required): Bearer token for authentication.

### Body Parameters
- `media_url` (required, string): The URL of the media file to be converted.
- `webhook_url` (optional, string): The URL to receive a webhook notification upon completion of the conversion process.
- `id` (optional, string): An identifier for the conversion job.
- `bitrate` (optional, string): The desired bitrate for the converted MP3 file, specified in the format `[bitrate]k` (e.g., `128k`). If not provided, the default bitrate of `128k` will be used.

### Example Request

```json
{
    "media_url": "https://example.com/video.mp4",
    "webhook_url": "https://example.com/webhook",
    "id": "job123",
    "bitrate": "192k"
}
```

```bash
curl -X POST \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"media_url": "https://example.com/video.mp4", "webhook_url": "https://example.com/webhook", "id": "job123", "bitrate": "192k"}' \
     https://api.example.com/v1/media/transform/mp3
```

## Response

### Success Response
**Status Code:** `200 OK`

```json
{
    "data": "https://cloud.example.com/converted_file.mp3",
    "endpoint": "/v1/media/transform/mp3"
}
```

### Error Responses
**Status Code:** `500 Internal Server Error`

```json
{
    "error": "Error message",
    "endpoint": "/v1/media/transform/mp3"
}
```

## Error Handling
- **Missing or invalid parameters**: If required parameters are missing or invalid, a `400 Bad Request` error will be returned.
- **Authentication error**: If the provided authentication token is invalid or missing, a `401 Unauthorized` error will be returned.
- **Internal server error**: If an unexpected error occurs during the conversion process, a `500 Internal Server Error` will be returned, along with an error message.

## Usage Notes
- The conversion process is handled asynchronously, and the endpoint will return immediately with a `200 OK` response upon successful submission of the conversion job.
- The converted MP3 file will be uploaded to cloud storage, and the cloud storage URL will be returned in the response.
- If a `webhook_url` is provided, a notification will be sent to that URL upon completion of the conversion process.

## Common Issues
- Ensure that the provided `media_url` is accessible and points to a valid media file.
- Check that the provided `bitrate` value is in the correct format (`[bitrate]k`).

## Best Practices
- Provide a unique `id` for each conversion job to facilitate tracking and monitoring.
- Consider implementing retry mechanisms or error handling in case of temporary failures during the conversion process.
- Monitor the logs for any errors or issues during the conversion process.