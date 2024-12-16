# `/v1/media/transcribe` API Documentation

## Overview
This endpoint is used to initiate a media transcription or translation task. It accepts a media URL and various configuration options, and returns the transcribed or translated text, along with optional subtitles (SRT) and segment information.

## Endpoint
- URL Path: `/v1/media/transcribe`
- HTTP Method: `POST`

## Request

### Headers
- `Authorization` (required): Bearer token for authentication.

### Body Parameters
- `media_url` (required, string): The URL of the media file to be transcribed or translated.
- `task` (optional, string): The task to perform. Allowed values: `"transcribe"` (default) or `"translate"`.
- `include_text` (optional, boolean): Whether to include the transcribed or translated text in the response. Default is `true`.
- `include_srt` (optional, boolean): Whether to include subtitles (SRT format) in the response. Default is `false`.
- `include_segments` (optional, boolean): Whether to include segment information in the response. Default is `false`.
- `word_timestamps` (optional, boolean): Whether to include word-level timestamps in the response. Default is `false`.
- `response_type` (optional, string): The type of response. Allowed values: `"direct"` (default) or `"cloud"`.
- `language` (optional, string): The language code for translation (if `task` is `"translate"`).
- `webhook_url` (optional, string): The URL to receive a webhook notification when the task is completed.
- `id` (optional, string): A unique identifier for the request.

### Example Request

```json
{
  "media_url": "https://example.com/video.mp4",
  "task": "transcribe",
  "include_text": true,
  "include_srt": true,
  "include_segments": false,
  "word_timestamps": false,
  "response_type": "direct",
  "language": null,
  "webhook_url": null,
  "id": "unique-request-id"
}
```

```bash
curl -X POST \
  https://api.example.com/v1/media/transcribe \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "media_url": "https://example.com/video.mp4",
    "task": "transcribe",
    "include_text": true,
    "include_srt": true,
    "include_segments": false,
    "word_timestamps": false,
    "response_type": "direct",
    "language": null,
    "webhook_url": null,
    "id": "unique-request-id"
  }'
```

## Response

### Success Response
- Status Code: `200 OK`

#### Response Type: `direct`
```json
{
  "text": "Transcribed text content...",
  "srt": "Subtitle content in SRT format...",
  "segments": null
}
```

#### Response Type: `cloud`
```json
{
  "text": "https://cloud.example.com/transcribed-text.txt",
  "srt": "https://cloud.example.com/subtitles.srt",
  "segments": null
}
```

### Error Responses
- Status Code: `400 Bad Request`
  - Example Response: `{"error": "Invalid request payload"}`
- Status Code: `401 Unauthorized`
  - Example Response: `{"error": "Authentication failed"}`
- Status Code: `500 Internal Server Error`
  - Example Response: `{"error": "An error occurred during transcription"}`

## Error Handling
- Missing or invalid request parameters will result in a `400 Bad Request` error.
- Authentication failures will result in a `401 Unauthorized` error.
- Any other exceptions or errors during the transcription process will result in a `500 Internal Server Error`.

## Usage Notes
- The `response_type` parameter determines whether the transcribed content is returned directly in the response (`direct`) or as URLs to cloud-hosted files (`cloud`).
- If `response_type` is `cloud`, the temporary files created during the transcription process are automatically deleted after uploading to cloud storage.
- The `webhook_url` parameter can be used to receive a notification when the transcription task is completed.

## Common Issues
- Providing an invalid or inaccessible `media_url`.
- Attempting to translate without specifying a `language`.
- Requesting unsupported features (e.g., `include_segments` with `task` set to `translate`).

## Best Practices
- Use the `id` parameter to uniquely identify each request for better tracking and debugging.
- Prefer the `cloud` response type for large media files to avoid potential issues with response size limits.
- Consider enabling `word_timestamps` for applications that require precise timing information.
- Implement error handling and retries for potential `500 Internal Server Error` responses.