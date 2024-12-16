# `/v1/media/transcribe` API Documentation

## Overview
This endpoint is used to initiate a media transcription or translation task. It accepts a media URL and various options for the transcription process, such as whether to include text, SRT subtitles, word-level timestamps, and the desired response format (direct or cloud-based). The endpoint returns the transcription results based on the specified options.

## Endpoint
**URL Path:** `/v1/media/transcribe`
**HTTP Method:** `POST`

## Request

### Headers
- `Authorization` (required): Bearer token for authentication.

### Body Parameters
- `media_url` (string, required): The URL of the media file to be transcribed or translated.
- `task` (string, optional): The task to perform, either "transcribe" or "translate". Default is "transcribe".
- `include_text` (boolean, optional): Whether to include the transcribed text in the response. Default is `true`.
- `include_srt` (boolean, optional): Whether to include SRT subtitles in the response. Default is `false`.
- `include_segments` (boolean, optional): Whether to include segmented transcription results in the response. Default is `false`.
- `word_timestamps` (boolean, optional): Whether to include word-level timestamps in the response. Default is `false`.
- `response_type` (string, optional): The type of response, either "direct" (return results directly) or "cloud" (return cloud storage URLs). Default is "direct".
- `language` (string, optional): The language code for the media file.
- `webhook_url` (string, optional): The URL to receive a webhook notification when the task is completed.
- `id` (string, optional): A unique identifier for the transcription task.

### Example Request

```json
{
  "media_url": "https://example.com/media/file.mp3",
  "task": "transcribe",
  "include_text": true,
  "include_srt": true,
  "include_segments": false,
  "word_timestamps": false,
  "response_type": "direct",
  "language": "en-US"
}
```

```bash
curl -X POST \
  https://api.example.com/v1/media/transcribe \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "media_url": "https://example.com/media/file.mp3",
    "task": "transcribe",
    "include_text": true,
    "include_srt": true,
    "include_segments": false,
    "word_timestamps": false,
    "response_type": "direct",
    "language": "en-US"
  }'
```

## Response

### Success Response

**Status Code:** `200 OK`

**Response Body (direct):**
```json
{
  "text": "Transcribed text content...",
  "srt": "SRT subtitle content...",
  "segments": null
}
```

**Response Body (cloud):**
```json
{
  "text": "https://cloud.example.com/transcripts/file1.txt",
  "srt": "https://cloud.example.com/subtitles/file1.srt",
  "segments": null
}
```

### Error Responses

**Status Code:** `400 Bad Request`

```json
{
  "error": "Invalid request payload"
}
```

**Status Code:** `401 Unauthorized`

```json
{
  "error": "Authentication failed"
}
```

**Status Code:** `500 Internal Server Error`

```json
{
  "error": "An error occurred during transcription process"
}
```

## Error Handling
- Missing or invalid request parameters will result in a `400 Bad Request` error.
- Authentication failures will result in a `401 Unauthorized` error.
- Any other exceptions or errors during the transcription process will result in a `500 Internal Server Error`.

## Usage Notes
- The `media_url` parameter is required for all requests.
- The `response_type` parameter determines whether the transcription results are returned directly or as cloud storage URLs.
- If the `response_type` is set to "cloud", the temporary files created during the transcription process will be automatically deleted after uploading to cloud storage.

## Common Issues
- Ensure that the provided `media_url` is accessible and valid.
- Check that the authentication token is valid and has the necessary permissions.
- Large media files may take longer to process, resulting in increased response times.

## Best Practices
- Use the `include_text`, `include_srt`, `include_segments`, and `word_timestamps` parameters judiciously to optimize response size and processing time.
- Consider using the "cloud" `response_type` for large media files to avoid potential timeouts or memory issues.
- Provide the `language` parameter for better transcription accuracy, if known.
- Implement error handling and retries in your client application to handle potential failures or timeouts.