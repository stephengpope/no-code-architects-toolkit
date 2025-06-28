# Media Download API Endpoint Documentation

## Overview

The `/v1/BETA/media/download` endpoint provides a powerful interface for downloading media content from various online sources using the yt-dlp library. This endpoint is part of the v1 media services in the API structure, allowing users to download videos, extract audio, and retrieve thumbnails and subtitles from supported platforms. The endpoint handles authentication, request validation, and queues tasks for processing, making it suitable for handling resource-intensive media downloads without blocking the main application thread.

## Endpoint

- **URL**: `/v1/BETA/media/download`
- **Method**: `POST`
- **Blueprint**: `v1_media_download_bp`

## Request

### Headers

- `x-api-key`: Required for authentication (handled by the `@authenticate` decorator)

### Body Parameters

#### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `media_url` | string (URI format) | The URL of the media to download |

#### Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `webhook_url` | string (URI format) | URL to receive the result when processing is complete |
| `id` | string | Custom identifier for tracking the request |
| `cookie` | string | Path to cookie file, URL to cookie file, or cookie string in Netscape format |
| `cloud_upload` | boolean | When true (default), the downloaded media will be uploaded to cloud storage and a cloud URL will be returned. When false, the direct download URL of the media will be returned instead. |

#### Format Options (Optional)

```json
"format": {
  "quality": "string",     // Quality specification (e.g., "best")
  "format_id": "string",   // Specific format ID
  "resolution": "string",  // Resolution specification (e.g., "720p")
  "video_codec": "string", // Video codec preference
  "audio_codec": "string"  // Audio codec preference
}
```

#### Audio Options (Optional)

```json
"audio": {
  "extract": boolean,      // Whether to extract audio
  "format": "string",      // Audio format (e.g., "mp3", "m4a")
  "quality": "string"      // Audio quality specification
}
```

#### Thumbnail Options (Optional)

```json
"thumbnails": {
  "download": boolean,     // Whether to download thumbnails
  "download_all": boolean, // Whether to download all available thumbnails
  "formats": ["string"],   // Array of thumbnail formats to download
  "convert": boolean,      // Whether to convert thumbnails
  "embed_in_audio": boolean // Whether to embed thumbnails in audio files
}
```

#### Subtitle Options (Optional)

```json
"subtitles": {
  "download": boolean,     // Whether to download subtitles
  "languages": ["string"], // Array of language codes for subtitles
  "format": "string",      // Subtitle format to download (e.g., 'srt', 'vtt', 'json3')
  "cloud_upload": boolean  // Whether to upload subtitles to cloud storage (defaults to true)
}
```

#### Download Options (Optional)

```json
"download": {
  "max_filesize": integer, // Maximum file size in bytes
  "rate_limit": "string",  // Download rate limit (e.g., "50K")
  "retries": integer       // Number of download retry attempts
}
```

### Example Request

```json
{
  "media_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "webhook_url": "https://example.com/webhook",
  "id": "custom-request-123",
  "cookie": "# Netscape HTTP Cookie File\n.youtube.com\tTRUE\t/\tFALSE\t0\tCONSENT\tYES+cb",
  "cloud_upload": true,
  "format": {
    "quality": "best",
    "resolution": "720p"
  },
  "audio": {
    "extract": true,
    "format": "mp3"
  },
  "thumbnails": {
    "download": true
  },
  "subtitles": {
    "download": true,
    "languages": ["en", "es-419"],
    "format": "srt",
    "cloud_upload": true
  }
}
```

### Example cURL Command

```bash
curl -X POST \
  https://api.example.com/v1/BETA/media/download \
  -H 'Content-Type: application/json' \
  -H 'x-api-key: your-api-key-here' \
  -d '{
    "media_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "webhook_url": "https://example.com/webhook",
    "id": "custom-request-123",
    "cookie": "# Netscape HTTP Cookie File\n.youtube.com\tTRUE\t/\tFALSE\t0\tCONSENT\tYES+cb",
    "cloud_upload": true,
    "format": {
      "quality": "best",
      "resolution": "720p"
    },
    "audio": {
      "extract": true,
      "format": "mp3"
    },
    "thumbnails": {
      "download": true
    },
    "subtitles": {
      "download": true,
      "languages": ["en", "es-419"],
      "format": "srt",
      "cloud_upload": true
    }
  }'
```

## Response

### Immediate Response (When Using Webhook)

When a webhook URL is provided, the API will queue the task and return an immediate response with a 202 status code:

```json
{
  "code": 202,
  "id": "custom-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "processing",
  "pid": 12345,
  "queue_id": 67890,
  "max_queue_length": "unlimited",
  "queue_length": 3,
  "build_number": "1.0.123"
}
```

### Success Response (When Not Using Webhook or When Webhook Is Called)

```json
{
  "code": 200,
  "id": "custom-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": {
    "media": {
      "media_url": "https://storage.example.com/media/video-123.mp4",
      "title": "Never Gonna Give You Up",
      "format_id": "22",
      "ext": "mp4",
      "resolution": "720p",
      "filesize": 12345678,
      "width": 1280,
      "height": 720,
      "fps": 30,
      "video_codec": "avc1.4d401f",
      "audio_codec": "mp4a.40.2",
      "upload_date": "20090325",
      "duration": 212,
      "view_count": 1234567890,
      "uploader": "Rick Astley",
      "uploader_id": "RickAstleyVEVO",
      "description": "Official music video for Rick Astley - Never Gonna Give You Up"
    },
    "thumbnails": [
      {
        "id": "default",
        "image_url": "https://storage.example.com/media/thumbnail-123.jpg",
        "width": 1280,
        "height": 720,
        "original_format": "jpg",
        "converted": false
      }
    ]
  },
  "message": "success",
  "pid": 12345,
  "queue_id": 67890,
  "run_time": 5.123,
  "queue_time": 0.456,
  "total_time": 5.579,
  "queue_length": 2,
  "build_number": "1.0.123"
}
```

### Error Responses

#### Invalid Request (400)

```json
{
  "code": 400,
  "id": "custom-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Invalid request: 'media_url' is a required property",
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 2,
  "build_number": "1.0.123"
}
```

#### Authentication Error (401)

```json
{
  "code": 401,
  "message": "Invalid API key",
  "build_number": "1.0.123"
}
```

#### Queue Full (429)

```json
{
  "code": 429,
  "id": "custom-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "MAX_QUEUE_LENGTH (100) reached",
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 100,
  "build_number": "1.0.123"
}
```

#### Server Error (500)

```json
{
  "code": 500,
  "id": "custom-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Error during download process - HTTP Error 403: Forbidden",
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 2,
  "build_number": "1.0.123"
}
```

## Error Handling

The endpoint handles various error scenarios:

- **Missing Required Parameters**: Returns a 400 status code with details about the missing parameter
- **Invalid Parameter Format**: Returns a 400 status code if parameters don't match the expected format
- **Authentication Failures**: Returns a 401 status code if the API key is invalid or missing
- **Queue Limits**: Returns a 429 status code if the task queue is full (when MAX_QUEUE_LENGTH is set)
- **Download Failures**: Returns a 500 status code with details about the download failure
- **Media Source Errors**: Returns a 500 status code if the media source is unavailable or restricted

## Usage Notes

1. **Webhook Handling**: 
   - When providing a `webhook_url`, the request will be queued and processed asynchronously
   - Without a `webhook_url`, the request will be processed synchronously, which may lead to longer response times

2. **Format Selection**:
   - The `format` options allow fine-grained control over the downloaded media quality
   - When multiple format options are specified, they are combined with a '+' separator

3. **Audio Extraction**:
   - Setting `audio.extract` to `true` will extract audio from the media
   - Specify `audio.format` to control the output audio format (e.g., "mp3", "m4a")

4. **Thumbnail Handling**:
   - When `thumbnails.download` is `true`, the API will download and provide URLs for thumbnails
   - Use `thumbnails.download_all` to retrieve all available thumbnails

5. **Rate Limiting**:
   - Use `download.rate_limit` to control download speed (e.g., "50K" for 50 KB/s)
   - This can help prevent IP blocking from some media sources

## Common Issues

1. **Geo-restricted Content**: Some media may be unavailable in certain regions
2. **Rate Limiting**: Media sources may rate-limit or block frequent downloads
3. **Large File Downloads**: Very large files may time out during download
4. **Format Availability**: Not all requested formats may be available for all media sources
5. **Webhook Failures**: If the webhook URL is unreachable, you won't receive the final result
6. **Queue Overflow**: Requests may be rejected if the processing queue is full

## Best Practices

1. **Use Webhooks for Large Downloads**: Always use webhooks for potentially large or slow downloads to avoid timeout issues
2. **Specify Format Constraints**: Be specific about format requirements to avoid unnecessarily large downloads
3. **Handle Thumbnails Separately**: For efficiency, only request thumbnails when needed
4. **Implement Retry Logic**: Implement client-side retry logic for handling temporary failures
5. **Monitor Queue Length**: Check the `queue_length` in responses to gauge system load
6. **Use Reasonable Rate Limits**: Set appropriate `download.rate_limit` values to avoid being blocked by media sources
7. **Validate Media URLs**: Ensure media URLs are valid and accessible before submitting
8. **Store Downloaded Media**: The cloud URLs provided in responses may have expiration times, so download and store important media promptly