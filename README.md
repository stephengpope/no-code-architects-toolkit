![Original Logo Symbol](https://github.com/user-attachments/assets/75173cf4-2502-4710-998b-6b81740ae1bd)

# No-Code Architects Toolkit API 

Tired of wasting thousands of dollars on API subscriptions to support all your automations? What if there was a free alternative?

The 100% FREE No-Code Architects Toolkit API processes different types of media. It is built in Python using Flask.

## What Can It Do?

The API can convert audio files. It creates transcriptions of content. It translates content between languages. It adds captions to videos. It can do very complicated media processing for content creation. The API can also manage files across multiple cloud services like Google Drive, Amazon S3, Google Cloud Storage, and Dropbox.

You can deploy this toolkit in several ways. It works with Docker. It runs on Google Cloud Platform. It functions on Digital Ocean. You can use it with any system that hosts Docker.

Easily replace services like ChatGPT Whisper, Cloud Convert, Createomate, JSON2Video, PDF(dot)co, Placid and OCodeKit.

## 👥 No-Code Architects Community

Want help? Join a supportive community and get dedicated tech support.

Join the ONLY community where you learn to leverage AI automation and content to grow your business (and streamline your biz).

Who's this for?
- Coaches and consultants
- AI Automation agencies
- SMMA & Content agencies
- SaaS Startup Founders

Get courses, community, support, daily calls and more.

Join the **[No-Code Architects Community](https://www.skool.com/no-code-architects)** today!

---

## API Endpoints

Each endpoint is supported by robust payload validation and detailed API documentation to facilitate easy integration and usage.

### Audio

- **[`/v1/audio/concatenate`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/audio/concatenate.md)**
  - Combines multiple audio files into a single audio file.
  - Example Payload:
    ```json
    {
      "audio_urls": [
        { "audio_url": "https://example.com/audio1.mp3" },
        { "audio_url": "https://example.com/audio2.mp3" }
      ],
      "webhook_url": "https://your-webhook-endpoint.com/callback",
      "id": "custom-request-id-123"
    }
    ```

### Code

- **[`/v1/code/execute/python`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/code/execute/execute_python.md)**
  - Executes Python code remotely and returns the execution results.
  - Example Payload:
    ```json
    {
        "code": "print('Hello, World!')",
        "timeout": 10,
        "webhook_url": "https://example.com/webhook",
        "id": "unique-request-id"
    }
    ```

### FFmpeg

- **[`/v1/ffmpeg/compose`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/ffmpeg/ffmpeg_compose.md)**
  - Provides a flexible interface to FFmpeg for complex media processing operations.
  - Example Payload (Note: See documentation for details on filter structure):
    ```json
    {
      "inputs": [
        { "file_url": "https://example.com/video1.mp4" }
      ],
      "filters": [
        { "filter": "hflip" } 
      ],
      "outputs": [
        {
          "options": [
            { "option": "-c:v", "argument": "libx264" },
            { "option": "-crf", "argument": 23 }
          ]
        }
      ],
      "webhook_url": "https://example.com/webhook",
      "id": "unique-request-id"
    }
    ```

### Image

- **[`/v1/image/convert/video`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/image/convert/image_to_video.md)**
  - Transforms a static image into a video with custom duration and zoom effects.
  - Example Payload:
    ```json
    {
        "image_url": "https://example.com/image.jpg",
        "length": 10,
        "frame_rate": 24,
        "zoom_speed": 5,
        "orientation": "landscape",
        "webhook_url": "https://example.com/webhook",
        "id": "request-123"
    }
    ```

- **[`/v1/image/effects/video`](https://github.com/fahimanwer/no-code-architects-toolkit/blob/main/docs/image/effects/image_effects_video.md)**
  - Creates a video from an image with dynamic effects like zoom-in-out or panning.
  - Example Payload (Zoom In/Out):
    ```json
    {
        "image_url": "https://example.com/image.jpg",
        "effect_type": "zoom_in_out",
        "length": 10,
        "orientation": "landscape",
        "id": "request-zoom"
    }
    ```

### Media

- **[`/v1/media/convert`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/media/convert/media_convert.md)**
  - Converts media files from one format to another with customizable codec options.
  - Example Payload:
    ```json
    {
      "media_url": "https://example.com/video.mp4",
      "format": "avi",
      "video_codec": "libx264",
      "audio_codec": "aac",
      "webhook_url": "https://example.com/webhook",
      "id": "unique-request-id"
    }
    ```

- **[`/v1/media/convert/mp3`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/media/convert/media_to_mp3.md)**
  - Converts various media formats specifically to MP3 audio.
  - Example Payload:
    ```json
    {
        "media_url": "https://example.com/video.mp4",
        "webhook_url": "https://example.com/webhook",
        "id": "unique-request-id",
        "bitrate": "192k"
    }
    ```

- **[`/v1/BETA/media/download`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/media/download.md)**
  - Downloads media content from various online sources using yt-dlp.
  - Example Payload:
    ```json
    {
      "media_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "webhook_url": "https://example.com/webhook",
      "id": "custom-request-123",
      "format": {
        "quality": "best",
        "resolution": "720p"
      },
      "audio": {
        "extract": true,
        "format": "mp3"
      }
    }
    ```

- **[`/v1/media/feedback`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/media/feedback.md)**
  - Provides a web interface for collecting and displaying feedback on media content. (GET endpoint, no JSON payload)

- **[`/v1/media/transcribe`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/media/media_transcribe.md)**
  - Transcribes or translates audio/video content from a provided media URL.
  - Example Payload:
    ```json
    {
      "media_url": "https://example.com/media/file.mp3",
      "task": "transcribe",
      "include_text": true,
      "include_srt": true,
      "response_type": "cloud",
      "webhook_url": "https://your-webhook.com/callback",
      "id": "custom-job-123"
    }
    ```

- **[`/v1/media/silence`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/media/silence.md)**
  - Detects silence intervals in a given media file.
  - Example Payload:
    ```json
    {
        "media_url": "https://example.com/audio.mp3",
        "start": "00:00:10.0",
        "end": "00:01:00.0",
        "duration": 0.5,
        "webhook_url": "https://example.com/webhook",
        "id": "unique-request-id"
    }
    ```

- **[`/v1/media/metadata`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/media/metadata.md)**
  - Extracts comprehensive metadata from media files including format, codecs, resolution, and bitrates.
  - Example Payload:
    ```json
    {
      "media_url": "https://example.com/media.mp4",
      "webhook_url": "https://example.com/webhook",
      "id": "custom-id"
    }
    ```

### S3

- **[`/v1/s3/upload`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/s3/upload.md)**
  - Uploads files to Amazon S3 storage by streaming directly from a URL.
  - Example Payload:
    ```json
    {
      "file_url": "https://example.com/path/to/file.mp4",
      "filename": "custom-name.mp4",
      "public": true
    }
    ```

### Toolkit

- **[`/v1/toolkit/authenticate`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/toolkit/authenticate.md)**
  - Provides a simple authentication mechanism to validate API keys. (GET endpoint, uses `X-API-Key` header, no JSON payload)

- **[`/v1/toolkit/test`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/toolkit/test.md)**
  - Verifies that the NCA Toolkit API is properly installed and functioning. (GET endpoint, uses `X-API-Key` header, no JSON payload)

- **[`/v1/toolkit/job/status`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/toolkit/job_status.md)**
  - Retrieves the status of a specific job by its ID.
  - Example Payload:
    ```json
    {
        "job_id": "e6d7f3c0-9c9f-4b8a-b7c3-f0e3c9f6b9d7"
    }
    ```

- **[`/v1/toolkit/jobs/status`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/toolkit/jobs_status.md)**
  - Retrieves the status of all jobs within a specified time range.
  - Example Payload (Optional):
    ```json
    {
        "since_seconds": 3600 
    }
    ```

### Video

- **[`/v1/video/caption`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/video/caption_video.md)**
  - Adds customizable captions to videos with various styling options.
  - Example Payload (Auto-transcribe):
    ```json
    {
        "video_url": "https://example.com/video.mp4",
        "settings": {
            "style": "karaoke",
            "line_color": "#FFFFFF",
            "word_color": "#FFFF00"
        },
        "webhook_url": "https://example.com/webhook"
    }
    ```

- **[`/v1/video/concatenate`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/video/concatenate.md)**
  - Combines multiple videos into a single continuous video file.
  - Example Payload:
    ```json
    {
        "video_urls": [
            {"video_url": "https://example.com/video1.mp4"},
            {"video_url": "https://example.com/video2.mp4"}
        ],
        "webhook_url": "https://example.com/webhook",
        "id": "request-123"
    }
    ```

- **[`/v1/video/thumbnail`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/video/thumbnail.md)**
  - Extracts a thumbnail image from a specific timestamp in a video.
  - Example Payload:
    ```json
    {
      "video_url": "https://example.com/video.mp4",
      "second": 30,
      "webhook_url": "https://your-service.com/webhook",
      "id": "custom-request-123"
    }
    ```

- **[`/v1/video/cut`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/video/cut.md)**
  - Cuts specified segments from a video file with optional encoding settings.
  - Example Payload:
    ```json
    {
      "video_url": "https://example.com/video.mp4",
      "cuts": [
        {
          "start": "00:00:10.000",
          "end": "00:00:20.000"
        },
        {
          "start": "00:00:30.000",
          "end": "00:00:40.000"
        }
      ],
      "webhook_url": "https://example.com/webhook",
      "id": "unique-request-id"
    }
    ```

- **[`/v1/video/split`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/video/split.md)**
  - Splits a video into multiple segments based on specified start and end times.
  - Example Payload:
    ```json
    {
      "video_url": "https://example.com/video.mp4",
      "splits": [
        {
          "start": "00:00:10.000",
          "end": "00:00:20.000"
        },
        {
          "start": "00:00:30.000",
          "end": "00:00:40.000"
        }
      ],
      "webhook_url": "https://example.com/webhook",
      "id": "unique-request-id"
    }
    ```

- **[`/v1/video/trim`](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/video/trim.md)**
  - Trims a video by keeping only the content between specified start and end times.
  - Example Payload:
    ```json
    {
      "video_url": "https://example.com/video.mp4",
      "start": "00:01:00",
      "end": "00:03:00",
      "webhook_url": "https://example.com/webhook",
      "id": "unique-request-id"
    }
    ```

- **[`/v1/video/get-scenes`](https://github.com/fahimanwer/no-code-architects-toolkit/blob/main/docs/video/get_scenes.md)**
  - Extracts frames (thumbnails) from multiple specified timestamps in a video.
  - Example Payload:
    ```json
    {
        "video_url": "https://example.com/my_video.mp4",
        "timestamps": [5, 15.5, 25],
        "id": "local-video-scenes",
        "webhook_url": "https://example.com/webhook"
    }
    ```

---

## Docker Build and Run

### Build the Docker Image

   ```bash
   docker build -t no-code-architects-toolkit .
   ```

### General Environment Variables

#### `API_KEY`
- **Purpose**: Used for API authentication.
- **Requirement**: Mandatory.

---

### S3-Compatible Storage Environment Variables

#### `S3_ENDPOINT_URL`
- **Purpose**: Endpoint URL for the S3-compatible service.
- **Requirement**: Mandatory if using S3-compatible storage.

#### `S3_ACCESS_KEY`
- **Purpose**: The access key for the S3-compatible storage service.
- **Requirement**: Mandatory if using S3-compatible storage.

#### `S3_SECRET_KEY`
- **Purpose**: The secret key for the S3-compatible storage service.
- **Requirement**: Mandatory if using S3-compatible storage.

#### `S3_BUCKET_NAME`
- **Purpose**: The bucket name for the S3-compatible storage service.
- **Requirement**: Mandatory if using S3-compatible storage.

#### `S3_REGION`
- **Purpose**: The region for the S3-compatible storage service.
- **Requirement**: Mandatory if using S3-compatible storage, "None" is acceptible for some s3 providers.

---

### Google Cloud Storage (GCP) Environment Variables

#### `GCP_SA_CREDENTIALS`
- **Purpose**: The JSON credentials for the GCP Service Account.
- **Requirement**: Mandatory if using GCP storage.

#### `GCP_BUCKET_NAME`
- **Purpose**: The name of the GCP storage bucket.
- **Requirement**: Mandatory if using GCP storage.

---

### Performance Tuning Variables

#### `MAX_QUEUE_LENGTH`
- **Purpose**: Limits the maximum number of concurrent tasks in the queue.
- **Default**: 0 (unlimited)
- **Recommendation**: Set to a value based on your server resources, e.g., 10-20 for smaller instances.

#### `GUNICORN_WORKERS`
- **Purpose**: Number of worker processes for handling requests.
- **Default**: Number of CPU cores + 1
- **Recommendation**: 2-4× number of CPU cores for CPU-bound workloads.

#### `GUNICORN_TIMEOUT`
- **Purpose**: Timeout (in seconds) for worker processes.
- **Default**: 30
- **Recommendation**: Increase for processing large media files (e.g., 300-600).

---

### Storage Configuration

#### `LOCAL_STORAGE_PATH`
- **Purpose**: Directory for temporary file storage during processing.
- **Default**: /tmp
- **Recommendation**: Set to a path with sufficient disk space for your expected workloads.

### Notes
- Ensure all required environment variables are set based on the storage provider in use (GCP or S3-compatible). 
- Missing any required variables will result in errors during runtime.
- Performance variables can be tuned based on your workload and available resources.

### Run the Docker Container:

   ```bash
   docker run -d -p 8080:8080 \
     # Authentication (required)
     -e API_KEY=your_api_key \
     
     # Cloud storage provider (choose one)

     # s3
     #
     #-e S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com \
     #-e S3_ACCESS_KEY=your_access_key \
     #-e S3_SECRET_KEY=your_secret_key \
     #-e S3_BUCKET_NAME=your_bucket_name \
     #-e S3_REGION=nyc3 \

     # Or

     # GCP Storage
     #
     #-e GCP_SA_CREDENTIALS='{"your":"service_account_json"}' \
     #-e GCP_BUCKET_NAME=your_gcs_bucket_name \
     
     # Local storage configuration (optional)
     -e LOCAL_STORAGE_PATH=/tmp \
     
     # Performance tuning (optional)
     -e MAX_QUEUE_LENGTH=10 \
     -e GUNICORN_WORKERS=4 \
     -e GUNICORN_TIMEOUT=300 \
     
     no-code-architects-toolkit
   ```

---

## Installation Guides

This API can be deployed to various cloud platforms:

### Digital Ocean

The Digital Ocean App platform is pretty easy to set up and get going, but it can cost more then other cloud providers.

#### Important: Long running processes

You need to use the "webhook_url" (for any request that exceeds 1 min) in your API payload to avoid timeouts due to CloudFlair proxy timeout.

If you use the webhook_url, there is no limit to the processing length.

- [Digital Ocean App Platform Installation Guide](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/cloud-installation/do.md) - Deploy the API on Digital Ocean App Platform

### Google Cloud RUN Platform

Sometimes difficult for people to install (especially on Google Business Workspaces), lots of detailed security exceptions.

However this is one of the cheapest options with great performance because you're only charged when the NCA Toolkit is processesing a request.

Outside of that you are not charged.

#### Imporatnt: Requests exceeding 5+ minutes can be problemactic 

GCP Run will terminate long rununing processes, which can happen when processing larger files (whether you use the webhook_url or not).

However, when your processing times are consistant lower than 5 minutes (e.g. you're only process smaller files), it works great! The performance is also great and as soon as you stop making requests you stop paying.

They also have a GPU option that might be usable for better performance (untested).

- [Google Cloud RUN Platform (GCP) Installation Guide](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/cloud-installation/gcp.md) - Deploy the API on Google Cloud Run

### General Docker Instructions

You can use these instructions to deploy the NCA Toolkit to any linux server (on any platform)

You can more easily control performance and cost this way, but requires more technical skill to get up and running (not much though).

- [General Docker Compose Installation Guide](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docker-compose.md)

## Testing the API

1. Install the **[Postman Template](https://bit.ly/49Gkhl)** on your computer
2. Import the API example requests from the template
3. Configure your environment variables in Postman:
   - `base_url`: Your deployed API URL
   - `x-api-key`: Your API key configured during installation
4. Use the example requests to validate that the API is functioning correctly
5. Use the **[NCA Toolkit API GPT](https://bit.ly/4feDDk4)** to explore additional features

---

## Development Workflow & Disk Space Management

Developing new features or fixing bugs typically involves building and testing Docker images. Over time, this can lead to an accumulation of old images and build cache, consuming significant disk space. Here's a recommended workflow and tips for managing disk usage:

### Managing Docker Disk Space

It's good practice to periodically clean up unused Docker resources:

*   **Prune unused images, containers, and networks:**
    ```bash
    docker system prune -a
    ```
    (Use with caution: this will remove all stopped containers, all networks not used by at least one container, all dangling images, and all dangling build cache.)

*   **List images to identify old/large ones:**
    ```bash
    docker images
    ```

*   **Remove specific images by ID or tag:**
    ```bash
    docker rmi <IMAGE_ID_OR_TAG>
    ```

*   **Prune build cache:**
    ```bash
    docker builder prune
    ```

### Feature Development Workflow

1.  **Create a new branch:** Start by creating a new branch in your local Git repository for the feature or fix (e.g., `git checkout -b feature/my-new-endpoint`).
2.  **Implement changes:** Make your code changes (e.g., add new service logic, routes, update `app.py`).
3.  **Update Documentation:** Create or update any relevant documentation files in the `/docs` directory and ensure the main `README.md` is updated to reflect new endpoints or significant changes in behavior, including example payloads.
4.  **Local Testing:**
    *   **Build a local Docker image:**
        ```bash
        docker build -t nca-toolkit-dev . 
        ```
        (Use a temporary tag like `nca-toolkit-dev` to avoid conflicting with official tags).
    *   **Run the local image:**
        ```bash
        docker run -d -p 8080:8080 --name nca-toolkit-test -e API_KEY=your_test_key [other_env_vars_as_needed] nca-toolkit-dev
        ```
    *   Thoroughly test the new feature using Postman or cURL. Check container logs (`docker logs nca-toolkit-test -f`) for errors.
    *   Stop and remove the test container: `docker stop nca-toolkit-test && docker rm nca-toolkit-test`.
5.  **Commit Changes:** Once satisfied, commit your changes to your feature branch with clear commit messages.
6.  **Push to GitHub:**
    *   Push your feature branch to your fork on GitHub.
    *   Create a Pull Request against the `main` branch of the `fahimanwer/no-code-architects-toolkit` repository (or the appropriate upstream repository if contributing to `stephengpope/no-code-architects-toolkit`).
7.  **Update Docker Hub (After PR Merge - Optional for Personal Use):**
    *   Once your changes are merged into the `main` branch of your primary repository (e.g., `fahimanwer/no-code-architects-toolkit`), you can build the official image and push it to your Docker Hub.
    *   Ensure your local `main` branch is up to date: `git checkout main && git pull origin main`.
    *   **Build the image:**
        ```bash
        docker build -t yourdockerhubusername/repositoryname:latest -t yourdockerhubusername/repositoryname:version_tag .
        # Example:
        # docker build -t fahimanwer18/nca-toolkit-fahim:latest -t fahimanwer18/nca-toolkit-fahim:0.2.0 .
        ```
    *   **Log in to Docker Hub:**
        ```bash
        docker login
        ```
    *   **Push the image:**
        ```bash
        docker push yourdockerhubusername/repositoryname:latest
        docker push yourdockerhubusername/repositoryname:version_tag
        # Example:
        # docker push fahimanwer18/nca-toolkit-fahim:latest
        # docker push fahimanwer18/nca-toolkit-fahim:0.2.0
        ```

By following these steps, you can keep your development environment clean and ensure that your GitHub and Docker Hub repositories stay synchronized with tested features.

---

## Contributing To the NCA Toolkit API

We welcome contributions from the public! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Submit a pull request to the "build" branch

### Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2. Update the README.md with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations and container parameters.

Thank you for your contributions!

---

## How To Get Support

Get courses, community, support daily calls and more.

Join the **[No-Code Architects Community](https://www.skool.com/no-code-architects)** today!

## License

This project is licensed under the [GNU General Public License v2.0 (GPL-2.0)](LICENSE).
