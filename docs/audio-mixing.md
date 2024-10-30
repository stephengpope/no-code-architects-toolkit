# `/audio-mixing` API Documentation

## Overview
The `/audio-mixing` endpoint allows you to combine an audio file with a video, with adjustable volume levels for each, providing a flexible way to add background music or sound effects.

## Endpoint
- **URL**: `/audio-mixing`
- **Method**: `POST`

## Request

### Headers
- **X-API-Key** (string, required): The API key used for authentication.

### Body Parameters
- **video_url** (string, required): URL of the video to mix with the audio.
- **audio_url** (string, required): URL of the audio to be combined with the video.
- **video_vol** (float, optional): Volume level for the video’s audio track (1.0 is default).
- **audio_vol** (float, optional): Volume level for the added audio track (1.0 is default).
- **output_length** (integer, optional): Desired length of the output video in seconds. Defaults to the shorter of the two input files if not specified.
- **webhook_url** (string, optional): URL to receive the resulting video URL upon completion.
- **id** (string, optional): Unique identifier for tracking the job.

### Example Request
```json
{
  "video_url": "https://example.com/video.mp4",
  "audio_url": "https://example.com/audio.mp3",
  "video_vol": 0.8,
  "audio_vol": 1.2,
  "output_length": 60,
  "webhook_url": "https://your-webhook-url.com/notify",
  "id": "mix123"
}
```

### Example using `curl`
```bash
curl -X POST "https://your-api-domain.com/audio-mixing" \
-H "X-API-Key: your_api_key" \
-H "Content-Type: application/json" \
-d '{
      "video_url": "https://example.com/video.mp4",
      "audio_url": "https://example.com/audio.mp3",
      "video_vol": 0.8,
      "audio_vol": 1.2,
      "output_length": 60,
      "webhook_url": "https://your-webhook-url.com/notify",
      "id": "mix123"
    }'
```

## Response

### Success Response (200 OK)
If the audio mixing is successful and no `webhook_url` is provided:
- **Status Code**: `200 OK`
- **Body**:
    ```json
    {
      "job_id": "mix123",
      "mixed_video_url": "https://cloud-storage-url.com/output_with_audio.mp4",
      "message": "success"
    }
    ```

### Accepted Response (202 Accepted)
If a `webhook_url` is provided, the request is queued, and this response is returned:
- **Status Code**: `202 Accepted`
- **Body**:
    ```json
    {
      "job_id": "mix123",
      "message": "processing"
    }
    ```

### Error Responses
- **400 Bad Request**: Missing or invalid parameters (`video_url` or `audio_url`).
  ```json
  {
    "error": "Missing required video_url or audio_url"
  }
  ```
- **500 Internal Server Error**: Mixing process failed.
  ```json
  {
    "error": "Error during audio mixing"
  }
  ```

## Error Handling
- **400 Bad Request**: Returned if `video_url` or `audio_url` is missing or malformed.
- **500 Internal Server Error**: Returned if there’s an error during audio mixing.

## Usage Notes
- Adjust `video_vol` and `audio_vol` for desired balance; values over `1.0` increase volume, while values under `1.0` decrease it.
- The `output_length` parameter can be set to the desired length, but defaults to the shorter duration between video and audio if not specified.

## Common Issues
1. **Invalid URLs**: Ensure `video_url` and `audio_url` are accessible and point directly to the media files.
2. **Format Compatibility**: Check that the video and audio formats are compatible for merging.

## Best Practices
- **Use Webhook for Large Files**: For lengthy files, use `webhook_url` to receive the result asynchronously.
- **Volume Adjustment**: Fine-tune `video_vol` and `audio_vol` to get the desired sound mix without distortion.
