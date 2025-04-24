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