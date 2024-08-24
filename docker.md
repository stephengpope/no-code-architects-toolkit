# Deploying and Running the Project on Google Cloud Platform (GCP)

This guide will walk you through setting up and deploying the project using the Google Cloud Platform (GCP). It includes instructions for creating a service account, enabling the necessary APIs, configuring environment variables, and deploying the project using Google Cloud Storage.

## Prerequisites

1. **Google Cloud Account**: Ensure you have a Google Cloud account. If you don't have one, you can sign up at [Google Cloud](https://cloud.google.com/).

2. **Google Cloud SDK**: Install the Google Cloud SDK on your local machine. You can download it from [Google Cloud SDK](https://cloud.google.com/sdk).

3. **Docker Installed**: Ensure Docker is installed on your machine. You can download it from [Docker](https://www.docker.com/products/docker-desktop).

## Step 1: Create a Google Cloud Project

1. **Log in to Google Cloud Console**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/).
   - Log in with your Google account.

2. **Create a New Project**:
   - Click on the project dropdown in the top navigation bar and select **New Project**.
   - Enter a name for your project (e.g., `MediaConverterProject`) and click **Create**.
   - Make sure the project is selected after creation.

## Step 2: Enable Required APIs

1. **Enable Google Cloud Storage API**:
   - Go to the **APIs & Services** > **Library**.
   - Search for "Google Cloud Storage" and click on it.
   - Click **Enable**.

2. **Enable Google Drive API** (if you plan to use Google Drive for file storage):
   - Go to the **APIs & Services** > **Library**.
   - Search for "Google Drive API" and click on it.
   - Click **Enable**.

3. **Enable Cloud Run (Optional)**:
   - If you plan to deploy the app using Cloud Run, you must enable this service.
   - Search for "Cloud Run API" in the **API Library** and click **Enable**.

## Step 3: Create a Service Account

1. **Navigate to IAM & Admin**:
   - Go to the **IAM & Admin** section from the left sidebar.
   - Click on **Service Accounts**.

2. **Create a New Service Account**:
   - Click on **Create Service Account**.
   - Provide a name (e.g., `media-converter-sa`) and a description.
   - Click **Create and Continue**.

3. **Assign Roles**:
   - Add the following roles:
     - **Storage Admin**: This role is required for accessing Google Cloud Storage.
     - **Viewer**: This role allows viewing resources in the project.
   - Click **Continue** and then **Done**.

4. **Create and Download Service Account Key**:
   - Click on the created service account.
   - Go to the **Keys** tab.
   - Click **Add Key** > **Create New Key**.
   - Choose **JSON** and click **Create**.
   - The JSON key file will be downloaded to your local machine. **Keep this file secure**.

## Step 4: Set Up Google Cloud Storage (GCS)

1. **Create a Storage Bucket**:
   - Navigate to **Storage** > **Browser**.
   - Click **Create Bucket**.
   - Provide a unique name for your bucket (e.g., `media-converter-bucket`).
   - Choose a location and storage class based on your requirements.
   - Click **Create**.

## Step 5: Configure Environment Variables

1. **Environment Variables**:
   - **GCP_SA_CREDENTIALS**: Set this to the content of your service account key file.
   - **GDRIVE_USER**: Set this to the email address associated with your Google Drive account.
   - **API_KEY**: Set this to any secret key you want to use for API authentication.


## Step 6: Deploying the Application


### Option 1: Run Locally with Docker to connect to GCP Storage Drive

1. **Run the Docker Container Locally**:
   - Build the Docker image:
     ```bash
     docker build -t no-code-architects-toolkit .
     ```
   - Run the Docker container:
     ```bash
     docker run -p 8080:8080 \
        -e STORAGE_PATH=GCP \
        -e API_KEY=<set-to-any-value> \
        -e GCP_BUCKET_NAME='<name-of-gcp-storage></name-of-gcp-storage> \
        -e GCP_SA_CREDENTIALS=<contents-of-json-file-downloaded> \
        no-code-architects-toolkit
     ```
### Option 2: Run Locally with Docker to connect to Google Drive

2. **Run the Docker Container Locally**:
   - Build the Docker image:
     ```bash
     docker build -t no-code-architects-toolkit .
     ```
   - Run the Docker container:
     ```bash
     docker run -p 8080:8080 \
        -e STORAGE_PATH=DRIVE \
        -e GDRIVE_USER='<email address>' \
        -e GDRIVE_FOLDER_ID=<Folder-ID>
        -e API_KEY=<set-to-any-value> \
        -e GCP_SA_CREDENTIALS=<contents-of-json-file-downloaded> \
        no-code-architects-toolkit
     ```

## Step 7: Testing the Application

1. **Authenticate**:
   - Make a POST request to the `/authenticate` endpoint:
     ```bash
     curl -X POST http://localhost:8080/authenticate \
     -H "X-API-Key: testkkey"
     ```

2. **Convert Media to MP3**:
   - Make a POST request to the `/convert-media-to-mp3` endpoint:
     ```bash
     curl -X POST http://localhost:8080/media-to-mp3 \
     -H "X-API-Key: testkkey" \
     -H "Content-Type: application/json" \
     -d '{
       "media_url": "https://example.com/mediafile.mp4",
       "webhook_url": "https://your-webhook-url.com/webhook"
     }'
     ```

## Step 8: Monitor and Manage Your Application

1. **View Logs**:
   - View application logs via Google Cloud Console or by attaching to the running Docker container:
     ```bash
     docker logs -f <container_id>
     ```

2. **Cleanup**:
   - Ensure to delete resources you no longer need to avoid unnecessary costs:
     - Delete the service account key file.
     - Delete the GCS bucket if not required.
     - Remove the Docker container and image when no longer needed.
