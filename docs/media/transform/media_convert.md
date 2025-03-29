# Media Format Conversion

Convert media from one format to another using FFmpeg.

## Endpoint

`POST /v1/media/convert`

## Authentication

Requires API key authentication.

## Request Body

```json
{
  "media_url": "https://example.com/path/to/video.mp4",
  "output_format": "webm",
  "video_codec": "vp9",
  "audio_codec": "opus",
  "webhook_url": "https://your-webhook-endpoint.com/callback"
}
```

### Parameters

- `media_url` (required): URL of the media file to convert
- `output_format` (required): Target format for conversion (e.g., "mp4", "webm", "mkv", "mov")
- `video_codec` (optional): Video codec to use (defaults to "copy" which preserves the original codec)
- `audio_codec` (optional): Audio codec to use (defaults to "copy" which preserves the original codec)
- `webhook_url` (optional): URL to receive the conversion result

## Response

### Synchronous Response

```json
{
  "code": 202,
  "id": "your-optional-id",
  "job_id": "generated-job-id",
  "message": "processing",
  "queue_length": 0,
  "build_number": "current-build-number"
}
```

### Webhook Response (when completed)

```json
{
  "endpoint": "/v1/media/convert",
  "code": 200,
  "id": "your-optional-id",
  "job_id": "generated-job-id",
  "response": {
    "file_url": "https://storage-url.com/path/to/converted/file.webm"
  },
  "message": "success",
  "run_time": 10.5,
  "queue_time": 0.2,
  "total_time": 10.7,
  "queue_length": 0,
  "build_number": "current-build-number"
}
```

## Examples

### Convert MP4 to WebM with VP9 and Opus codecs

```json
{
  "media_url": "https://example.com/video.mp4",
  "output_format": "webm",
  "video_codec": "vp9",
  "audio_codec": "opus"
}
```

### Convert MP4 to MKV without re-encoding

```json
{
  "media_url": "https://example.com/video.mp4",
  "output_format": "mkv"
}
```

## Notes

- Using `"video_codec": "copy"` and `"audio_codec": "copy"` (or omitting these parameters) will preserve the original codecs when possible, which is faster but may not be compatible with all output formats.
- When converting to audio-only formats (mp3, aac, wav, flac, ogg, opus), the service will automatically:
  - Select an appropriate audio codec if "copy" is specified
  - Remove the video stream entirely
- For audio-only formats, these codecs are used when "copy" is specified:
  - mp3: libmp3lame
  - aac: aac
  - opus: libopus
  - flac: flac
  - ogg: libvorbis
  - wav: pcm_s16le
- Some codec and format combinations might not be compatible. For example, VP9 video codec is typically used with WebM format.
- Common video codecs include: "h264", "h265", "vp8", "vp9", "av1"
- Common audio codecs include: "aac", "mp3", "opus", "vorbis"