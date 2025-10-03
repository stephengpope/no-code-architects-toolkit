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

## **Optional: Enable Cloud Run Jobs for Long-Running Tasks**

For tasks that may exceed Cloud Run's request timeout or require dedicated resources, you can optionally configure Cloud Run Jobs to offload long-running operations.

### **What are Cloud Run Jobs?**

Cloud Run Jobs execute tasks that run to completion and then shut down, making them ideal for:
- Video processing
- Large file downloads
- Batch operations
- Any task that may take longer than the request timeout

### **Benefits:**
- **No timeout limits**: Jobs can run as long as needed (up to 24 hours)
- **Cost-effective**: Only pay for the time the job is running
- **Automatic scaling**: Each job gets dedicated resources
- **Better reliability**: Jobs won't be interrupted by request timeouts

---

### **Setup Instructions**

#### **1. Create a Cloud Run Job**

1. Navigate to **Cloud Run** > **Jobs** in the GCP Console
2. Click **Create Job**
3. Configure the job:
   - **Container image**: `stephengpope/no-code-architects-toolkit:latest`
   - **Job name**: `nca-toolkit-job` (or your preferred name)
   - **Region**: Same as your Cloud Run service (e.g., `us-central1`)
   - **Memory**: `16 GB`
   - **CPU**: `4 CPUs`
   - **Task timeout**: `3600 seconds` (1 hour, adjust as needed)
   - **Maximum retries**: `0` (jobs will handle their own error reporting)

#### **2. Configure Environment Variables**

Add the same environment variables as your Cloud Run service:
- `API_KEY`: Your API key
- `GCP_BUCKET_NAME`: Your Cloud Storage bucket name
- `GCP_SA_CREDENTIALS`: Your service account JSON key (entire contents)

#### **3. Add Job Configuration to Cloud Run Service**

Update your Cloud Run **service** environment variables to enable job triggering:

- `GCP_JOB_NAME`: The name of your Cloud Run Job (e.g., `nca-toolkit-job`)
- `GCP_JOB_LOCATION`: The region where your job is deployed (e.g., `us-central1`)

#### **4. Grant Permissions**

Your service account needs permission to trigger jobs:

1. Navigate to **IAM & Admin** > **IAM**
2. Find your service account (e.g., `NCA Toolkit Service Account`)
3. Click **Edit** and add the following role:
   - **Cloud Run Invoker**
4. Save changes

---

### **How It Works**

When you make a request with a `webhook_url` parameter:

1. **Cloud Run service** receives the request
2. If `GCP_JOB_NAME` is configured, it triggers a **Cloud Run Job** instead of processing locally
3. The job starts, processes the task, and sends results to your webhook
4. The job automatically shuts down after completion

**Example request:**
```json
{
  "media_url": "https://example.com/large-video.mp4",
  "webhook_url": "https://your-webhook.com/callback"
}
```

The service will:
- Return immediately with a job submission confirmation
- Trigger the Cloud Run Job
- Job processes the video and sends results to your webhook when complete

---

### **Monitoring Jobs**

- View job executions in **Cloud Run** > **Jobs** > **[Your Job Name]** > **Executions**
- Each execution shows:
  - Execution ID (used for tracking in logs)
  - Start time
  - Duration
  - Status (Running, Succeeded, Failed)
  - Logs

---

### **Cost Considerations**

Cloud Run Jobs pricing:
- Billed per second of CPU and memory usage
- Only charged while the job is actively running
- No charges when idle

**Example:** A 10-minute video processing job using 4 CPU / 16 GB would cost approximately $0.20-0.30 per execution.

---

### **Troubleshooting**

**Jobs not triggering?**
- Verify `GCP_JOB_NAME` and `GCP_JOB_LOCATION` are set correctly in your Cloud Run service
- Check that your service account has **Cloud Run Invoker** role
- Ensure the job exists in the specified region

**Jobs failing?**
- Check job execution logs in Cloud Run console
- Verify all environment variables are properly set on the job
- Ensure task timeout is sufficient for your workload

**Not receiving webhooks?**
- Verify your webhook URL is accessible from GCP
- Check job execution logs for webhook delivery errors
- Ensure your webhook endpoint can handle POST requests

---

**Note:** Cloud Run Jobs are completely optional. If not configured, all requests will be processed by the Cloud Run service normally.