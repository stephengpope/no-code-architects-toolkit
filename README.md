# ![Original Logo Symbol](https://github.com/user-attachments/assets/75173cf4-2502-4710-998b-6b81740ae1bd)
No-Code Architects Toolkit

This project is a Flask-based API that provides various media processing services, including audio conversion, video combination, transcription, captioning, and Google Drive upload capabilities.

## Features

- Convert media files to MP3
- Combine multiple videos
- Transcribe media files
- Add captions to videos
- Upload files to Google Drive
- Adding audio to video file

## Prerequisites

- Docker
- Google Cloud Platform account (for GCS and Google Drive integration)

## Environment Variables

The following environment variables are required:

- `API_KEY`: Your API key for authentication
- `GCP_SA_CREDENTIALS`: Google Cloud Platform service account credentials (JSON format)
- `GDRIVE_USER`: Google Drive user email for impersonation
- `GCP_BUCKET_NAME`: Google Cloud Storage bucket name

## Docker Build and Run

1. Build the Docker image:

```bash
docker build -t media-processing-api .
```

2. Run the Docker container:

```bash
docker run -d -p 8080:8080 \
  -e API_KEY=your_api_key \
  -e GCP_SA_CREDENTIALS='{"your":"service_account_json"}' \
  -e GDRIVE_USER=your_gdrive_user@example.com \
  -e GCP_BUCKET_NAME=your_gcs_bucket_name \
  media-processing-api
```

## API Endpoints

### Authentication

All endpoints require an `X-API-Key` header for authentication.

### 1. Convert Media to MP3

**Endpoint:** `/media-to-mp3`

**Method:** POST

**Payload:**
```json
{
  "media_url": "https://example.com/media.mp4",
  "webhook_url": "https://your-webhook.com/callback",
  "id": "unique_request_id"
}
```

### 2. Combine Videos

**Endpoint:** `/combine-videos`

**Method:** POST

**Payload:**
```json
{
  "video_urls": [
    {"video_url": "https://example.com/video1.mp4"},
    {"video_url": "https://example.com/video2.mp4"}
  ],
  "webhook_url": "https://your-webhook.com/callback",
  "id": "unique_request_id"
}
```

### 3. Transcribe Media

**Endpoint:** `/transcribe-media`

**Method:** POST

**Payload:**
```json
{
  "media_url": "https://example.com/media.mp4",
  "output": "transcript",
  "webhook_url": "https://your-webhook.com/callback",
  "id": "unique_request_id"
}
```

### 4. Caption Video

**Endpoint:** `/caption-video`

**Method:** POST

**Payload:**
```json
{
  "video_url": "https://example.com/video.mp4",
  "srt": "1\n00:00:01,000 --> 00:00:04,000\nThis is a caption",
  "options": {},
  "webhook_url": "https://your-webhook.com/callback",
  "id": "unique_request_id"
}
```

### 5. Upload to Google Drive

**Endpoint:** `/gdrive-upload`

**Method:** POST

**Payload:**
```json
{
  "file_url": "https://example.com/file.pdf",
  "filename": "uploaded_file.pdf",
  "folder_id": "google_drive_folder_id",
  "webhook_url": "https://your-webhook.com/callback",
  "id": "unique_request_id"
}
```

### 6. Audio Mixing

**Endpoint:** `/audio-mixing`

**Method:** POST

**Payload:**
```json
{
  "video_url": "https://example.com/video.mp4",
  "audio_url": "https://example.com/audio.mp3",
  "video_vol": 100,
  "audio_vol": 100,
  "output_length": "video",
  "webhook_url": "https://your-webhook.com/callback",
  "id": "unique_request_id"
}
```

## Response Format

For asynchronous processing (when `webhook_url` is provided):

```json
{
  "code": 202,
  "id": "unique_request_id",
  "job_id": "generated_job_id",
  "message": "processing"
}
```

For synchronous processing:

```json
{
  "code": 200,
  "response": "result_or_file_url",
  "message": "success"
}
```

## Webhook Callback Format

```json
{
  "endpoint": "/endpoint-name",
  "code": 200,
  "id": "unique_request_id",
  "job_id": "generated_job_id",
  "response": "result_or_file_url",
  "message": "success"
}
```

## Error Handling

In case of errors, the API will return appropriate HTTP status codes along with error messages in the response body.

## Notes

- All endpoints support both synchronous and asynchronous processing.
- For asynchronous processing, provide a `webhook_url` in the request payload.
- The API uses Google Cloud Storage for storing processed files when `GCP_BUCKET_NAME` is set.
- Google Drive integration requires proper setup of service account credentials and user impersonation.

## License

[MIT License](LICENSE)
