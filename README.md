
![Original Logo Symbol](https://github.com/user-attachments/assets/75173cf4-2502-4710-998b-6b81740ae1bd)

# No-Code Architects Toolkit by Stephen G. Pope

Tired of wasting thousands of dollars on API subscriptions to support all your automations? What if there was a free alternative?

The No-Code Architects Toolkit API processes different types of media. It is built in Python using Flask.

The API can convert audio files. It can manipulate video files. It creates transcriptions of content. It translates content between languages. It adds captions to videos.

The API manages files across multiple cloud services like Google Drive, Amazon S3, Google Cloud Storage, and Dropbox. You can deploy this toolkit in several ways. It works with Docker. It runs on Google Cloud Platform. It functions on Digital Ocean. You can use it with any system that hosts Docker.

Easily replace services like ChatGPT Whisper, Cloud Convert, Createomate, JSON2Video, PDF(dot)co, Placid and OCodeKit.

## 👥 No-Code Architects Community

Want help? Join a supportive community and get dedicated tech support inside the **[No-Code Architects Community](https://www.skool.com/no-code-architects)**.

The ONLY community where you learn to leverage AI automation and content to grow your business (and streamline your biz).

Who's this for?
- Coaches and consultants
- AI Automation agencies
- SMMA & Content agencies
- SaaS Startup Founders

Get courses, community, support daily calls and more.

Join the **[No-Code Architects Community](https://www.skool.com/no-code-architects)** today!

---

## Features of the No-Code Architects Toolkit API

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

# **Installing the NCA Toolkit API on Google Cloud Platform (GCP)**

## 🎥 Video Installation Instructions

Watch these **[Detailed Video Instructions](https://youtu.be/6bC93sek9v8)** to set up the No-Code Architects Toolkit API.

- **Docker Image**: stephengpope/no-code-architects-toolkit:latest

### Mentioned Resources

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

## **Step 5: Deploy the Toolkit on Cloud Run**
1. Navigate to **Cloud Run** in the GCP Console.
2. Click **Create Service** and configure the deployment:
   - **Container Image URL**: Use the toolkit's Docker Hub image URL (refer to the GitHub repository).
   - **Allow unauthenticated invocations**.
   - **CPU Allocation**: Set to **Always Allocated**.
   - **Memory and CPU**: Allocate **16 GB memory** and **4 CPUs**.

3. Under **Variables & Secrets**, set the following environment variables:
   - `API_KEY`: Set a secure key (e.g., `Test123`).
   - `GCP_BUCKET_NAME`: Your Cloud Storage bucket name (e.g., `nca-toolkit-bucket`).
   - `GCP_SA_CREDENTIALS`: Paste the contents of the JSON file downloaded in **Step 3**.

4. Save the settings and deploy the service.

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

## License

This project is licensed under the [MIT License](LICENSE).
