# /v1/video/youtube_transcript

Fetches the transcript for a given YouTube video.

**POST** `/v1/video/youtube_transcript`

## Payload

```
{
  "video_id": "string",         // Required. The YouTube video ID.
  "languages": ["en", "de"],    // Optional. List of language codes to try (default: ["en"])
  "format": "json"               // Optional. "json" (default), "plain", or "srt"
}
```

## Response

- **200 OK**
  - If `format` is `json` (default):
    ```json
    {
      "transcript": [
        {"text": "...", "start": 0.0, "duration": 1.5},
        ...
      ]
    }
    ```
  - If `format` is `plain`:
    ```json
    {
      "transcript": "Full transcript as plain text."
    }
    ```
  - If `format` is `srt`:
    ```json
    {
      "transcript": "1\n00:00:00,000 --> 00:00:01,500\nHello world\n..."
    }
    ```
- **400 Error**
    ```json
    {
      "error": "Error message"
    }
    ```

## Example

**Request:**
```bash
curl -X POST http://localhost:8080/v1/video/youtube_transcript \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"video_id": "dQw4w9WgXcQ", "languages": ["en"], "format": "srt"}'
```

**Response (SRT):**
```json
{
  "transcript": "1\n00:00:00,000 --> 00:00:01,500\nHello world\n..."
}
```

## Notes
- If `languages` is omitted, English (`["en"]`) is tried by default.
- If no transcript is available, an error message is returned.
- Supported formats: `json`, `plain`, `srt`. 