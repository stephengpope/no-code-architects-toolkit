
![Original Logo Symbol](https://github.com/user-attachments/assets/75173cf4-2502-4710-998b-6b81740ae1bd)

# No-Code Architects Toolkit

Are you tired of wasting thousands of dollars on API subscriptions to support all your automations?

What if there was a free alternative?

The No-Code Architects Toolkit is a robust media processing API built with Flask, providing services like audio conversion, video manipulation, transcriptions, translations, captioning, and cloud file management on Google Drive, S3, GCP Storage, Dropbox. This toolkit is designed for easy deployment via Docker, Google Run Platform (GCP), Digital Ocean or any Docker host.

Easily replace services like ChatGPT Whisper, Cloud Convert, Createomate, JSON2Video, PDF(dot)co, Placid and OCodeKit.

---

## Features of the No-Code Architects Toolkit API

### General
- Simplifies media and data processing tasks with a variety of endpoints.
- Supports secure authentication and seamless integration with Google Drive and cloud storage.
- Customizable FFmpeg-based media manipulation.

---

### Core Features
#### 1. **Authentication**
   - Endpoint: `/v1/toolkit/authenticate`
   - Verify API key access for authorized operations.

#### 2. **Testing Connectivity**
   - Endpoint: `/v1/toolkit/test`
   - Confirms API setup by creating and uploading a test file.

---

### Media Transformation
#### 3. **Convert Media to MP3**
   - Endpoint: `/v1/media/transform/mp3`
   - Converts audio and video files into MP3 format with optional bitrate customization.

#### 4. **Transcribe Media**
   - Endpoint: `/v1/media/transcribe`
   - Generates transcriptions or translations from media files.
   - Options for text, subtitles, and word-level timestamps.

---

### Video Processing
#### 5. **Combine Videos**
   - Endpoint: `/v1/video/concatenate`
   - Merges multiple video files into one output.

#### 6. **Add Captions**
   - Endpoint: `/v1/video/caption`
   - Adds customizable captions to videos with detailed formatting options.

---

### Image Processing
#### 7. **Convert Image to Video**
   - Endpoint: `/v1/image/transform/video`
   - Creates videos from images, with support for length, frame rate, and zoom effects.

---

### Advanced Media Manipulation
#### 8. **Flexible Media Composition**
   - Endpoint: `/v1/ffmpeg/compose`
   - Allows custom FFmpeg command structures for complex media tasks.

---

### Code Execution
#### 9. **Execute Python Code**
   - Endpoint: `/v1/code/execute/python`
   - Runs Python scripts securely with configurable timeouts.

---

Each feature is supported by robust payload validation and detailed API documentation to facilitate easy integration and usage.

---

## Environment Variables

The following environment variables are necessary for the application to function as intended:

- `API_KEY`: A secure API key for authenticating requests.
- `GCP_SA_CREDENTIALS`: Service account credentials in JSON format for Google Cloud Platform access.
- `GCP_BUCKET_NAME`: The name of the Google Cloud Storage bucket used for storage.

---

## Docker Build and Run

1. **Build the Docker Image**:

   ```bash
   docker build -t no-code-architects-toolkit .
   ```

2. **Run the Docker Container**:

   ```bash
   docker run -d -p 8080:8080 \
     -e API_KEY=your_api_key \
     -e GCP_SA_CREDENTIALS='{"your":"service_account_json"}' \
     -e GCP_BUCKET_NAME=your_gcs_bucket_name \
     no-code-architects-toolkit
   ```

---

## Installation Instructions

Follow these steps to set up the No-Code Architects Toolkit API. For a detailed walkthrough, watch the [video installation instructions](https://youtu.be/6bC93sek9v8).

---

### Resources

- **Docker Image**: stephengpope/no-code-architects-toolkit:latest
- **Postman Template**: [https://bit.ly/49Gkh61](https://bit.ly/49Gkh61)
- **NCA Toolkit API GPT**: [https://bit.ly/4feDDk4](https://bit.ly/4feDDk4)

---

## License

This project is licensed under the [MIT License](LICENSE).
