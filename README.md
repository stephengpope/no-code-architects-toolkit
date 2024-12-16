
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

## Features of the No-Code Architects Toolkit API

Each feature is supported by robust payload validation and detailed API documentation to facilitate easy integration and usage.

### Advanced Media Manipulation

#### 1. `/v1/ffmpeg/compose`
- **Description**: Provides a flexible way to compose and manipulate media files using FFmpeg. Supports complex media operations like transcoding, concatenation, and filtering.
- **Documentation Link**: [FFmpeg Compose Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/ffmpeg/compose.md)

---

### Video Processing

#### 2. `/v1/video/caption`
- **Description**: Adds captions to a video file, including options for font, position, and styling. It also supports automated language detection and custom replacements in captions.
- **Documentation Link**: [Video Caption Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/video/caption_video.md)

#### 3. `/v1/video/concatenate`
- **Description**: Combines multiple video files into a single video file. The input files are concatenated in the specified order, and the final video is uploaded to cloud storage.
- **Documentation Link**: [Video Concatenate Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/video/concatenate.md)

---

### Code Execution

#### 4. `/v1/code/execute/python`
- **Description**: Executes Python code on the server in a controlled environment. Useful for scripting, prototyping, or dynamically running Python scripts with secure execution.
- **Documentation Link**: [Execute Python Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/code/execute/execute_python.md)

---

### Image Processing

#### 5. `/v1/image/transform/video`
- **Description**: Converts an image into a video file with configurable options like duration, frame rate, and zoom effects. Ideal for creating video slideshows or transitions.
- **Documentation Link**: [Image to Video Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/image/transform/image_to_video.md)

---

### Media Transformation

#### 6. `/v1/media/transform/mp3`
- **Description**: Transforms media files into MP3 format, supporting advanced options for encoding like bit rate and sample rate configuration.
- **Documentation Link**: [Media Transform to MP3 Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/media/transform/media_to_mp3.md)

#### 7. `/v1/media/transcribe`
- **Description**: Transcribes audio files to text using advanced speech-to-text processing. Supports various languages and audio formats.
- **Documentation Link**: [Audio Transcribe Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/media/transcribe.md)

---

### Core Features

#### 8. `/v1/test`
- **Description**: A basic endpoint to verify the availability and functionality of the API. Useful for initial setup and connection tests.
- **Documentation Link**: [Test Endpoint Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/toolkit/test.md)

#### 9. `/v1/authenticate`
- **Description**: Verifies the provided API key and authenticates the user. Returns a success message if the API key is valid.
- **Documentation Link**: [Authenticate Endpoint Documentation](https://github.com/stephengpope/no-code-architects-toolkit/blob/main/docs/toolkit/authenticate.md)

---

## Docker Build and Run

1. **Build the Docker Image**:

   ```bash
   docker build -t no-code-architects-toolkit .
   ```

The following environment variables are necessary for the application to function as intended:

- `API_KEY`: A secure API key for authenticating requests.
- `GCP_SA_CREDENTIALS`: Service account credentials in JSON format for Google Cloud Platform access.
- `GCP_BUCKET_NAME`: The name of the Google Cloud Storage bucket used for storage.

2. **Run the Docker Container**:

   ```bash
   docker run -d -p 8080:8080 \
     -e API_KEY=your_api_key \
     -e GCP_SA_CREDENTIALS='{"your":"service_account_json"}' \
     -e GCP_BUCKET_NAME=your_gcs_bucket_name \
     no-code-architects-toolkit
   ```

---

# **Installing on the Google Cloud Platform (GCP)**

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
- A Google Cloud account. [Sign up here](https://cloud.google.com/) if you don’t already have one.
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
