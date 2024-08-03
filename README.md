# No-Code Architects Toolkit

This Docker build let's you reduce/eliminate monthly subscription costs for various APIs you may use in your automations. 

It's built with Flask and uses FFmpeg for media conversion and the Whisper model for transcription.

In the current v1.0 build:

- Transcribe video/audio (without the 25 MB Whisper limit)

Next up:

- Merge videos and add audio for faceless video automations
- Automate podcast editing, intros, outros, music, etc
- Translate text to other languages
- Automatically add video subtitles
- Upload large videos to GDrive


## Installation with Docker

1. Clone this repository:
   ```
   git clone git@github.com:stephengpope/no-code-architects-toolkit.git
   cd <repository-directory>
   ```

2. Create a `.env` file in the root directory and add your API key:
   ```
   API_KEY=your_secret_api_key_here
   ```

3. Build the Docker image:
   ```
   docker build -t no-code-architects-toolkit .
   ```

4. Run the Docker container:
   ```
   docker run -p 8080:8080 --env-file .env no-code-architects-toolkit
   ```

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
curl -X POST http://localhost:8080/convert-media-to-mp3 \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "https://example.com/path/to/media/file",
    "webhook_url": "https://your-webhook-url.com/endpoint"
  }'
```

### Transcribe Media

Transcribe a media file to text or SRT format.

```bash
curl -X POST http://localhost:8080/transcribe-media \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "https://example.com/path/to/media/file",
    "output": "transcript",
    "webhook_url": "https://your-webhook-url.com/endpoint"
  }'
```

Note: For `output`, you can use either `"transcript"` or `"srt"`.

### Get Processed File

Retrieve a processed file by filename.

```bash
curl -X POST http://localhost:8080/get-file \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "processed_file.mp3"
  }' \
  --output downloaded_file.mp3
```

## Notes

- The API uses webhooks for asynchronous processing. Provide a `webhook_url` in your requests to receive the results.
- Processed files are temporarily stored and automatically deleted after 1 hour.
- The transcription feature uses the Whisper AI model for accurate results.

For more details on the API implementation, please refer to the source code.
