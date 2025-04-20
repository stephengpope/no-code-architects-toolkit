
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

- **`/v1/audio/concatenate`**
  - Combines multiple audio files into a single audio file.
  - [Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/audio/concatenate.md)

### Code

- **`/v1/code/execute/python`**
  - Executes Python code remotely and returns the execution results.
  - [Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/code/execute/execute_python.md)

### FFmpeg

- **`/v1/ffmpeg/compose`**
  - Provides a flexible interface to FFmpeg for complex media processing operations.
  - [Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/ffmpeg/ffmpeg_compose.md)

### Image

- **`/v1/image/convert/video`**
  - Transforms a static image into a video with custom duration and zoom effects.
  - [Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/image/convert/image_to_video.md)

### Media

- **`/v1/media/convert`**
  - Converts media files from one format to another with customizable codec options.
  - [Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/media_convert.md)

- **`/v1/media/convert/media`**
  - Advanced media conversion with customizable video and audio codec options.
  - [Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/media/convert/media_convert.md)

- **`/v1/media/convert/mp3`**
  - Converts various media formats specifically to MP3 audio.
  - [Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/media/convert/media_to_mp3.md)

- **`/v1/media/download`**
  - Downloads media content from various online sources using yt-dlp.
  - [Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/media/download.md)

- **`/v1/media/feedback`**
  - Provides a web interface for collecting and displaying feedback on media content.
  - [Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/media/feedback.md)

- **`/v1/media/transcribe`**
  - Transcribes or translates audio/video content from a provided media URL.
  - [Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/media/media_transcribe.md)

### S3

- **`/v1/s3/upload`**
  - Uploads files to Amazon S3 storage by streaming directly from a URL.
  - [Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/s3/upload.md)

### Toolkit

- **`/v1/toolkit/authenticate`**
  - Provides a simple authentication mechanism to validate API keys.
  - [Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/toolkit/authenticate.md)

- **`/v1/toolkit/test`**
  - Verifies that the NCA Toolkit API is properly installed and functioning.
  - [Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/toolkit/test.md)

### Video

- **`/v1/video/caption`**
  - Adds customizable captions to videos with various styling options.
  - [Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/video/caption_video.md)

- **`/v1/video/concatenate`**
  - Combines multiple videos into a single continuous video file.
  - [Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/video/concatenate.md)

- **`/v1/video/thumbnail`**
  - Extracts a thumbnail image from a specific timestamp in a video.
  - [Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/video/thumbnail.md)

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

### Google Cloud Platform (GCP) Environment Variables

#### `GCP_SA_CREDENTIALS`
- **Purpose**: The JSON credentials for the GCP Service Account.
- **Requirement**: Mandatory if using GCP storage.

#### `GCP_BUCKET_NAME`
- **Purpose**: The name of the GCP storage bucket.
- **Requirement**: Mandatory if using GCP storage.

---

### S3-Compatible Storage Environment Variable

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

### Notes
- Ensure all required environment variables are set based on the storage provider in use (GCP or S3-compatible). 
- Missing any required variables will result in errors during runtime.

### Run the Docker Container:

   ```bash
   docker run -d -p 8080:8080 \
     -e API_KEY=your_api_key \
     -e GCP_SA_CREDENTIALS='{"your":"service_account_json"}' \
     -e GCP_BUCKET_NAME=your_gcs_bucket_name \
     no-code-architects-toolkit
   ```

---

# Installing on the Google Cloud Platform (GCP)

## 🎥 Video Instructions

Watch **[Detailed Video Instructions](https://youtu.be/6bC93sek9v8)** to set up the No-Code Architects Toolkit API.

- Use the **Docker Image** below:

  ```
  stephengpope/no-code-architects-toolkit:latest
  ```

### Video Resources

- **[Postman Template](https://bit.ly/49Gkh61)**
- **[NCA Toolkit API GPT](https://bit.ly/4feDDk4)** 

Or use the guide below walks you through the steps to install the NCA Toolkit API on GCP.

---

## **Prerequisites**
- A Google Cloud account. [Sign up here](https://cloud.google.com/) if you don't already have one.
  - New users receive $300 in free credits.
- Basic knowledge of GCP services such as Cloud Run and Cloud Storage.
- A terminal or code editor for managing files.

---

## **Step 1: Create a Google Cloud Project**
1. Log into the [GCP Console](https://console.cloud.google.com/).
2. Click on the **Project Selector** in the top navigation bar and select **New Project**.
3. Enter a project name, such as `NCA Toolkit Project`.
4. Click **Create**.

---

## **Step 2: Enable Required APIs**
Enable the following APIs:
- **Cloud Storage API**
- **Cloud Storage JSON API**
- **Cloud Run API**

### **How to Enable APIs:**
1. In the GCP Console, navigate to **APIs & Services** > **Enable APIs and Services**.
2. Search for each API, click on it, and enable it.

---

## **Step 3: Create a Service Account**
1. Navigate to **IAM & Admin** > **Service Accounts** in the GCP Console.
2. Click **+ Create Service Account**.
   - Enter a name (e.g., `NCA Toolkit Service Account`).
3. Assign the following roles to the service account:
   - **Storage Admin**
   - **Viewer**
4. Click **Done** to create the service account.
5. Open the service account details and navigate to the **Keys** tab.
   - Click **Add Key** > **Create New Key**.
   - Choose **JSON** format, download the file, and store it securely.

---

## **Step 4: Create a Cloud Storage Bucket**
1. Navigate to **Storage** > **Buckets** in the GCP Console.
2. Click **+ Create Bucket**.
   - Choose a unique bucket name (e.g., `nca-toolkit-bucket`).
   - Leave default settings, but:
     - Uncheck **Enforce public access prevention**.
     - Set **Access Control** to **Uniform**.
3. Click **Create** to finish.
4. Go to the bucket permissions, and add **allUsers** as a principal with the role:
   - **Storage Object Viewer**.
5. Save changes.

---

## **Step 5: Deploy on Google Cloud Run**

### 1. Navigate to Cloud Run
- Open the **Cloud Run** service in the **Google Cloud Console**.

### 2. Create a New Service
- Click **Create Service**.
- Then **Deploy one revision from Docker Hub using the image below**:

  ```
  stephengpope/no-code-architects-toolkit:latest
  ```

### 3. Allow Unauthenticated Invocations
- Check the box to **allow unauthenticated invocations**.

### 4. Configure Resource Allocation
- Set **Memory**: `16 GB`.
- Set **CPU**: `4 CPUs`.
- Set **CPU Allocation**: **Always Allocated**.

### 5. Adjust Scaling Settings
- **Minimum Instances**: `0` (to minimize cost during idle times).
- **Maximum Instances**: `5` (adjustable based on expected load).

### 6. Use Second-Generation Servers
- Scroll to **Platform Version** and select **Second Generation**.
- Second-generation servers offer better performance and feature support for advanced use cases.

### 7. Add Environment Variables
- Add the following environment variables:
- `API_KEY`: Your API key (e.g., `Test123`).
- `GCP_BUCKET_NAME`: The name of your Cloud Storage bucket.
- `GCP_SA_CREDENTIALS`: The JSON key of your service account.
  - Paste the **entire contents** of the downloaded JSON key file into this field.
  - Ensure:
    - Proper JSON formatting.
    - No leading or trailing spaces.

### 8. Configure Advanced Settings
- Set the **Container Port**: Default to `8080`.
- **Request Timeout**: `300 seconds` (to handle long-running requests).
- Enable **Startup Boost** to improve performance for the first request after a cold start.

### 9. Deploy the Service
- Verify all settings and click **Create**.
- The deployment process might take a few minutes. Once completed, a green checkmark should appear in the Cloud Run dashboard.

By following these steps, the NCA Toolkit will be successfully deployed and accessible via Google Cloud Run with second-generation servers for optimal performance.

---

## **Step 6: Test the Deployment**

1. Install **[Postman Template](https://bit.ly/49Gkh61)** on your computer.
2. Import the API example requests from the NCA Toolkit GitHub repository.
3. Configure two environment variables in Postman:
   - `base_url`: Your deployed Cloud Run service URL.
   - `x-api-key`: The API key you configured in **Step 5**.
4. Use the example requests to validate that the API is functioning correctly.
5. Use the **[NCA Toolkit API GPT](https://bit.ly/4feDDk4)** to learn more.

By following these steps, your NCA Toolkit API should be successfully deployed on Google Cloud Platform.

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

This project is licensed under the [MIT License](LICENSE).
