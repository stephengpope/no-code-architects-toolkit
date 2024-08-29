
# No-Code Architects Toolkit

This Docker build helps you reduce or eliminate monthly subscription costs for various APIs used in your automations.

It's built with Flask, utilizes FFmpeg for media conversion, and leverages the Whisper model for transcription.

### Features in the v1.0 Build:

- Convert media files to MP3 format.
- Transcribe video/audio files without the 25 MB Whisper limit.

### Upcoming Features:

- Merge videos and add audio for faceless video automations.
- Automate podcast editing, intros, outros, music, etc.
- Translate text to other languages.
- Automatically add video subtitles.
- Upload large videos to Google Drive.

## Installation with Docker

1. Clone this repository:
   ```bash
   git clone git@github.com:stephengpope/no-code-architects-toolkit.git
   cd <repository-directory>
   ```

2. Build the Docker image:
   ```bash
   docker build -t no-code-architects-toolkit .
   ```

3. Run the Docker container with the necessary environment variables:

   ```bash
   docker run -p 8080:8080 \
   -e API_KEY=your_secret_api_key_here \
   -e STORAGE_PATH=local \ # Can be 'local', 'gcp', or 'drive'
   -e GCP_SA_CREDENTIALS='{"type": "service_account", ...}' \ # Required if using GCP
   -e GCP_BUCKET_NAME=your_gcp_bucket_name \ # Required if using GCP
   -e GDRIVE_USER=your_google_drive_user_id \ # Required if using Google Drive
   no-code-architects-toolkit
   ```

   Replace the environment variables with your actual values.

The API will now be accessible at `http://localhost:8080`.

## API Endpoints

### Authentication

All endpoints require authentication using the `X-API-Key` header.

#### Test Authentication

```bash
curl -X POST http://localhost:8080/authenticate \
  -H "X-API-Key: your_api_key_here"
```

### Convert Media to MP3

Convert a media file to MP3 format.

```bash
curl -X POST http://localhost:8080/media-to-mp3 \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "https://example.com/path/to/media/file",
    "webhook_url": "https://your-webhook-url.com/endpoint"
  }'
```

This endpoint supports different storage methods for the converted MP3 file:

- **Local Storage** (`STORAGE_PATH=local`): The file is saved locally.
- **Google Cloud Storage** (`STORAGE_PATH=gcp`): The file is uploaded to a Google Cloud Storage bucket.
- **Google Drive** (`STORAGE_PATH=drive`): The file is uploaded to Google Drive.

### Transcribe Media

Transcribe a media file to text or SRT format.

```bash
curl -X POST http://localhost:8080/transcribe \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "https://example.com/path/to/media/file",
    "output": "transcript",
    "webhook_url": "https://your-webhook-url.com/endpoint"
  }'
```

- **Output Options**:
  - `"transcript"`: Transcribes the media file to plain text.
  - `"srt"`: Generates a subtitle file in SRT format.

### Environment Variables

- **`API_KEY`**: The secret API key required for authenticating API requests.
- **`STORAGE_PATH`**: Specifies where to store processed files. Can be one of the following:
  - `"local"`: Stores files locally.
  - `"gcp"`: Uploads files to Google Cloud Storage (requires `GCP_SA_CREDENTIALS` and `GCP_BUCKET_NAME`).
  - `"drive"`: Uploads files to Google Drive (requires `GDRIVE_USER` and `GCP_SA_CREDENTIALS`).
- **`GCP_SA_CREDENTIALS`**: Google Cloud service account credentials in JSON format (required for `gcp` or `drive` storage).
- **`GCP_BUCKET_NAME`**: The name of the Google Cloud Storage bucket (required for `gcp` storage).
- **`GDRIVE_USER`**: The Google Drive user ID or email to specify the target drive (required for `drive` storage).

### Notes

- The API uses webhooks for asynchronous processing. Provide a `webhook_url` in your requests to receive results upon completion.
- Processed files are stored temporarily according to the selected storage method.
- The transcription feature uses the Whisper AI model for accurate results.

For more details on the API implementation, please refer to the source code.
