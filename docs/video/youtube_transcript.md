# /v1/video/youtube/transcript

Fetches the transcript for a given YouTube video.

**POST** `/v1/video/youtube/transcript`

## Payload

```
{
  "youtube_url": "string",         // Required. YouTube video URL or video ID
  "languages": ["en", "de"],       // Optional. List of language codes to try (default: ["en"])
  "format": "json",                // Optional. "json" (default), "plain", or "srt"
  "response_type": "direct"        // Optional. "direct" (default) or "cloud"
}
```

### Supported youtube_url formats:
- Full YouTube URLs: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- Short URLs: `https://youtu.be/dQw4w9WgXcQ`
- Embed URLs: `https://www.youtube.com/embed/dQw4w9WgXcQ`
- Video IDs: `dQw4w9WgXcQ`
- **YouTube Shorts**: `https://www.youtube.com/shorts/dQw4w9WgXcQ`

### Response Types:
- **direct** (default): Returns the transcript directly in the response body
- **cloud**: Uploads the transcript to cloud storage and returns a downloadable URL

## Response

### Direct Response (response_type: "direct")
- **200 OK**
  - If `format` is `json` (default):
    ```json
    {
      "transcript": [
        {"text": "...", "start": 0.0, "duration": 1.5},
        ...
      ],
      "response_type": "direct"
    }
    ```
  - If `format` is `plain`:
    ```json
    {
      "transcript": "Full transcript as plain text.",
      "response_type": "direct"
    }
    ```
  - If `format` is `srt`:
    ```json
    {
      "transcript": "1\n00:00:00,000 --> 00:00:01,500\nHello world\n...",
      "response_type": "direct"
    }
    ```

### Cloud Response (response_type: "cloud")
- **200 OK**
    ```json
    {
      "transcript_url": "https://cloud-storage.example.com/transcripts/abc123.json",
      "response_type": "cloud"
    }
    ```

### Error Response
- **400 Error**
    ```json
    {
      "error": "Error message"
    }
    ```

## Examples

### Direct Response Example
**Request:**
```bash
curl -X POST http://localhost:8080/v1/video/youtube/transcript \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "languages": ["en"], "format": "srt"}'
```

**Response:**
```json
{
  "transcript": "1\n00:00:00,000 --> 00:00:01,500\nHello world\n...",
  "response_type": "direct"
}
```

### Cloud Response Example
**Request:**
```bash
curl -X POST http://localhost:8080/v1/video/youtube/transcript \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://www.youtube.com/shorts/dQw4w9WgXcQ", "languages": ["en"], "format": "json", "response_type": "cloud"}'
```

**Response:**
```json
{
  "transcript_url": "https://cloud-storage.example.com/transcripts/abc123.json",
  "response_type": "cloud"
}
```

## Notes
- If `languages` is omitted, English (`["en"]`) is tried by default.
- If no transcript is available, an error message is returned.
- Supported formats: `json`, `plain`, `srt`.
- The endpoint accepts both full YouTube URLs and video IDs for convenience.
- **YouTube Shorts URLs** are now supported and refer to the same videos as regular YouTube URLs.
- When using `response_type: "cloud"`, the transcript is uploaded to cloud storage and a downloadable URL is returned.
- Cloud storage files are automatically cleaned up from local storage after upload.