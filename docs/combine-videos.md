
# `/combine-videos` API Documentation

## Overview
The `/combine-videos` endpoint merges multiple video files into a single video file, making it convenient for concatenating various clips.

## Endpoint
- **URL**: `/combine-videos`
- **Method**: `POST`

## Request

### Headers
- **X-API-Key** (string, required): The API key used for authentication.

### Body Parameters
- **video_urls** (array of strings, required): An array of URLs for each video to be combined. Videos will be merged in the order provided.
- **webhook_url** (string, optional): URL to receive the resulting video URL upon completion.
- **id** (string, optional): Unique identifier for tracking the job.

### Example Request
```json
{
  "video_urls": [
    "https://example.com/video1.mp4",
    "https://example.com/video2.mp4"
  ],
  "webhook_url": "https://your-webhook-url.com/notify",
  "id": "combine123"
}
```

### Example using `curl`
```bash
curl -X POST "https://your-api-domain.com/combine-videos" \
-H "X-API-Key: your_api_key" \
-H "Content-Type: application/json" \
-d '{
      "video_urls": [
        "https://example.com/video1.mp4",
        "https://example.com/video2.mp4"
      ],
      "webhook_url": "https://your-webhook-url.com/notify",
      "id": "combine123"
    }'
```

## Response

### Success Response (200 OK)
If the video combination is successful and no `webhook_url` is provided:
- **Status Code**: `200 OK`
- **Body**:
    ```json
    {
      "job_id": "combine123",
      "combined_video_url": "https://cloud-storage-url.com/combined_output.mp4",
      "message": "success"
    }
    ```

### Accepted Response (202 Accepted)
If a `webhook_url` is provided, the request is queued, and this response is returned:
- **Status Code**: `202 Accepted`
- **Body**:
    ```json
    {
      "job_id": "combine123",
      "message": "processing"
    }
    ```

### Error Responses
- **400 Bad Request**: Missing or invalid `video_urls`.
  ```json
  {
    "error": "Missing or invalid video_urls parameter"
  }
  ```
- **500 Internal Server Error**: Combination process failed.
  ```json
  {
    "error": "Error during video combination"
  }
  ```

## Error Handling
- **400 Bad Request**: Returned if `video_urls` is missing or not a valid array.
- **500 Internal Server Error**: Returned for errors encountered during the combination process.

## Usage Notes
- Ensure that all videos in `video_urls` are in a compatible format (e.g., same resolution, codec) for seamless merging.
- Videos will be combined in the sequence provided in the `video_urls` array.

## Common Issues
1. **Invalid Video URLs**: Ensure that each URL in `video_urls` is valid and accessible.
2. **Resolution/Format Mismatch**: Combining videos with different resolutions or formats may cause errors or unexpected output.

## Best Practices
- **Asynchronous Processing**: For large video files or numerous videos, use `webhook_url` for asynchronous notification.
- **Verify Input Format Consistency**: To avoid playback issues, ensure all videos have the same resolution and codec.
