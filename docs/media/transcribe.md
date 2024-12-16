# Media Transcription Endpoint

## 1. Overview

The `/v1/media/transcribe` endpoint is part of the version 1 API and is responsible for transcribing or translating media files (audio or video) into text format. It supports various output formats, including plain text, SRT subtitles, and segmented transcripts with word-level timestamps. The endpoint integrates with the main application context by utilizing the `queue_task_wrapper` decorator, which allows for efficient task queueing and processing.

## 2. Endpoint

```
POST /v1/media/transcribe
```

## 3. Request

### Headers

- `x-api-key` (required): The API key for authentication.

### Body Parameters

The request body should be a JSON object with the following parameters:

| Parameter       | Type    | Required | Description                                                  |
|-----------------|---------|----------|--------------------------------------------------------------|
| `media_url`     | string  | Yes      | The URL of the media file to be transcribed or translated.  |
| `task`          | string  | No       | The task to perform, either "transcribe" or "translate". Default is "transcribe". |
| `include_text`  | boolean | No       | Whether to include the plain text transcript in the response. Default is `true`. |
| `include_srt`   | boolean | No       | Whether to include the SRT subtitle file in the response. Default is `false`. |
| `include_segments` | boolean | No    | Whether to include the segmented transcript with word-level timestamps in the response. Default is `false`. |
| `word_timestamps` | boolean | No     | Whether to include word-level timestamps in the segmented transcript. Default is `false`. |
| `response_type` | string  | No       | The type of response, either "direct" (return data directly) or "cloud" (return cloud storage URLs). Default is "direct". |
| `language`      | string  | No       | The language code for translation (if `task` is "translate"). |
| `webhook_url`   | string  | No       | The URL to receive a webhook notification upon completion. |
| `id`            | string  | No       | A unique identifier for the request. |

### Example Request

```json
{
  "media_url": "https://example.com/media/audio.mp3",
  "task": "transcribe",
  "include_text": true,
  "include_srt": true,
  "include_segments": false,
  "word_timestamps": false,
  "response_type": "direct",
  "webhook_url": "https://example.com/webhook"
}
```

```bash
curl -X POST \
  https://api.example.com/v1/media/transcribe \
  -H 'x-api-key: YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "media_url": "https://example.com/media/audio.mp3",
    "task": "transcribe",
    "include_text": true,
    "include_srt": true,
    "include_segments": false,
    "word_timestamps": false,
    "response_type": "direct",
    "webhook_url": "https://example.com/webhook"
  }'
```

## 4. Response

### Success Response

**Status Code:** 200 OK

**Response Body (direct):**

```json
{
  "text": "This is the transcribed text.",
  "srt": "This is the SRT subtitle file content.",
  "segments": null
}
```

**Response Body (cloud):**

```json
{
  "text": "https://cloud.example.com/transcripts/text.txt",
  "srt": "https://cloud.example.com/transcripts/subtitles.srt",
  "segments": null
}
```

### Error Responses

**Status Code:** 400 Bad Request

```json
{
  "message": "Invalid request payload"
}
```

**Status Code:** 401 Unauthorized

```json
{
  "message": "Missing or invalid API key"
}
```

**Status Code:** 500 Internal Server Error

```json
{
  "message": "An error occurred during transcription process"
}
```

## 5. Error Handling

- **Missing or invalid parameters**: If any required parameters are missing or invalid, the endpoint will return a 400 Bad Request error with an appropriate error message.
- **Authentication error**: If the provided API key is missing or invalid, the endpoint will return a 401 Unauthorized error.
- **Processing error**: If an error occurs during the transcription or translation process, the endpoint will return a 500 Internal Server Error with the error message.
- **Queue overflow**: If the task queue reaches the maximum length specified by the `MAX_QUEUE_LENGTH` environment variable, the endpoint will return a 429 Too Many Requests error.

## 6. Usage Notes

- The `media_url` parameter should point to a valid media file (audio or video) that can be accessed by the server.
- If the `response_type` is set to "cloud", the endpoint will return URLs to the transcribed files stored in cloud storage, instead of the actual file contents.
- The `webhook_url` parameter is optional and can be used to receive a notification when the transcription process is complete.
- The `id` parameter is optional and can be used to uniquely identify the request.

## 7. Common Issues

- Providing an invalid or inaccessible `media_url`.
- Attempting to transcribe or translate unsupported media formats.
- Exceeding the maximum queue length, resulting in a 429 Too Many Requests error.

## 8. Best Practices

- Validate the `media_url` parameter before submitting the request to ensure it points to a valid and accessible media file.
- Use the `response_type` parameter wisely, considering the trade-off between response size and cloud storage costs.
- Implement proper error handling and retry mechanisms in your client application to handle potential errors and retries.
- Monitor the queue length and adjust the `MAX_QUEUE_LENGTH` environment variable as needed to prevent queue overflow.