![Original Logo Symbol](https://github.com/user-attachments/assets/75173cf4-2502-4710-998b-6b81740ae1bd)

# No-Code Architects Toolkit

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

## API Documentation

This repository contains documentation for each API endpoint. Below is a list of endpoints with links to detailed documentation files located in the `docs` folder.

## Endpoints

1. [Authenticate](docs/authenticate.md) - Verifies API key for access authorization.
2. [Media to MP3](docs/media-to-mp3.md) - Converts media files to MP3 format.
3. [Transcribe Media](docs/transcribe-media.md) - Transcribes audio from media files.
4. [Transcribe Media (v1)](docs/v1/transcribe-media.md) - Provides transcription with additional options.
5. [FFmpeg Compose](docs/v1/ffmpeg-compose.md) - Flexible media composition with FFmpeg.
6. [Image to Video](docs/image-to-video.md) - Converts images into video with customizable animation.
7. [Caption Video](docs/caption-video.md) - Adds captions to videos using SRT or ASS files.
8. [Combine Videos](docs/combine-videos.md) - Merges multiple video files into one.
9. [Audio Mixing](docs/audio-mixing.md) - Mixes audio with video, with adjustable volume.
10. [Google Drive Upload](docs/gdrive-upload.md) - Uploads files to Google Drive with chunk support.
11. [Extract Keyframes](docs/extract-keyframes.md) - Extracts keyframes from video files.

Refer to each linked file for detailed usage, examples, and response structures.

## License

[MIT License](LICENSE)
