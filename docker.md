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
        -e GCP_BUCKET_NAME='<name-of-gcp-storage>' \
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
        -e GDRIVE_FOLDER_ID='<Folder-ID>'
        -e API_KEY='<set-to-any-value>' \
        -e GCP_SA_CREDENTIALS=<contents-of-json-file-downloaded> \
        no-code-architects-toolkit
     ```
    - Using Google Drive, you have to prepare the shared folder for the Service Account to use. When configuring the Service Account, it produces an email address. Use it to share your Google Drive folder. ![](/images/service-account-email-address.png)
    ![](/images/shared-goodle-drive-image.png)
    - The GDRIVE_FOLDER_ID is the trailing subfolder in the shared folder URL.
        ![](/images/sahred-google-drive-url.png)

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


### Step 9: Deploy the Docker Image to Google Cloud Run

1. **Log in to Google Cloud Console**:
   - Open [Google Cloud Console](https://console.cloud.google.com/).

2. **Navigate to Cloud Run**:
   - In the left-hand menu, click on **Cloud Run** under the **Serverless** section.

3. **Create a New Service**:
   - Click on the **Create Service** button.
   - Select the project you created earlier (e.g., `MediaConverterProject`).

4. **Configure the Service**:
   - **Service Name**: Enter a name for your service (e.g., `no-code-architects-toolkit`).
   - **Region**: Choose the region where you want your service to run (e.g., `us-central1`).

5. **Deploy the Docker Image**:
   - **Container Image URL**: Enter the following Docker Hub image URL: `stephengpope/no-code-architects-toolkit:v1.0.1`.
   - Click on **Show advanced settings** to configure additional settings.

6. **Set Environment Variables**:
   - Scroll down to the **Environment variables** section.
   - Add the following environment variables:
     - `API_KEY`: Set this to your desired API key.
     - `STORAGE_PATH`: Set this to either `GCP` or `DRIVE` depending on your setup.
     - `GCP_BUCKET_NAME`: If using Google Cloud Storage, set this to the name of your GCS bucket.
     - `GDRIVE_USER`: If using Google Drive, set this to the email address associated with your Google Drive account.
     - `GDRIVE_FOLDER_ID`: If using Google Drive, set this to the folder ID of your Google Drive folder.
     - `GCP_SA_CREDENTIALS`: Paste the contents of your service account JSON key file.

7. **Set Port Configuration**:
   - Under the **Container** section, ensure that the **Port** is set to `8080`, as this is the port on which the Gunicorn server is listening.

8. **Set Resources and Concurrency**:
   - Adjust the memory and CPU limits as needed. By default, you can start with 256 MiB of memory and 1 vCPU.
   - Set the **Maximum requests per container** (concurrency) based on your application's expected load.

9. **Authentication**:
   - Under the **Authentication** section, you can choose whether the service requires authentication. For public access, choose **Allow unauthenticated invocations**.

10. **Deploy the Service**:
    - Review your configurations and click **Create** or **Deploy**.
    - Wait for the deployment to complete. Once it's done, Google Cloud Run will provide you with a URL to access your service.

### Step 10: Access and Test the Service

1. **Access the Service**:
   - Once the service is deployed, you’ll see a URL in the Google Cloud Console under your service’s details. This URL is where your service is running.

2. **Test the Endpoints**:
   - Use the provided URL to make requests to your endpoints. For example, to test the `/authenticate` endpoint, use the following command:
     ```bash
     curl -X POST https://your-service-url/authenticate \
     -H "X-API-Key: your-api-key"
     ```

3. **Monitor Logs and Performance**:
   - Use the Google Cloud Console to monitor logs and view the performance of your deployed service. Navigate to **Cloud Run > Logs** to view real-time logs.

### Step 11: Cleanup Resources

1. **Delete the Service**:
   - If you no longer need the service, you can delete it by going to **Cloud Run**, selecting the service, and clicking **Delete**.

2. **Remove Unnecessary Resources**:
   - Delete the GCS bucket or Google Drive folder if no longer required.
   - Remove any remaining Docker images or containers on your local machine.

### Summary

These steps will help you extend the provided instructions to deploy and run the Docker Hub container `stephengpope/no-code-architects-toolkit:v1.0.1` on Google Cloud Run using the GCP Website console. Make sure to test your deployment thoroughly and monitor the service using the tools provided by Google Cloud.