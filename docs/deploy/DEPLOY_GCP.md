# Deploying to Google Cloud Platform (Cloud Run)

This guide walks you through deploying the NCA Toolkit API to **Google Cloud Run** using the provided Makefile. Cloud Run is a cost-effective option — you only pay while requests are being processed.

---

## Prerequisites

- **Google Cloud account** — [Sign up here](https://cloud.google.com/) (new users get $300 free credits)
- **gcloud CLI** installed — [Install guide](https://cloud.google.com/sdk/docs/install)
- **Docker** installed and running
- **make** available (pre-installed on macOS/Linux)

### Authenticate with GCP

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

---

## Step 1: Create a GCP Project

1. Go to the [GCP Console](https://console.cloud.google.com/)
2. Click **Project Selector** → **New Project**
3. Name it (e.g., `nca-toolkit`) and click **Create**
4. Set it as your active project:

```bash
gcloud config set project YOUR_PROJECT_ID
```

---

## Step 2: Enable Required APIs

```bash
gcloud services enable \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  storage.googleapis.com \
  storage-api.googleapis.com
```

---

## Step 3: Create a Service Account

1. Navigate to **IAM & Admin** → **Service Accounts** in the GCP Console
2. Click **+ Create Service Account**
   - Name: `nca-toolkit-sa`
3. Assign roles:
   - **Storage Admin**
   - **Viewer**
4. Click **Done**
5. Open the service account → **Keys** tab → **Add Key** → **Create New Key** → **JSON**
6. Download and store the JSON key securely

---

## Step 4: Create a Cloud Storage Bucket

```bash
# Create the bucket
gcloud storage buckets create gs://YOUR_BUCKET_NAME --location=us-central1

# Make objects publicly readable
gcloud storage buckets add-iam-policy-binding gs://YOUR_BUCKET_NAME \
  --member=allUsers \
  --role=roles/storage.objectViewer
```

Or via the Console:

1. Go to **Storage** → **Buckets** → **+ Create Bucket**
2. Choose a unique name (e.g., `nca-toolkit-bucket`)
3. Uncheck **Enforce public access prevention**
4. Set **Access Control** to **Uniform**
5. Add `allUsers` with role **Storage Object Viewer**

---

## Step 5: Set Up Artifact Registry

First-time setup — create a Docker repository to store your images:

```bash
make repo
```

Then authenticate Docker with the registry:

```bash
make auth
```

---

## Step 6: Configure Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and set your values:

```bash
API_KEY=your_secure_api_key

# GCP Storage
GCP_SA_CREDENTIALS='{"type":"service_account","project_id":"..."}'
GCP_BUCKET_NAME=your-bucket-name

# Performance (optional)
GUNICORN_WORKERS=2
GUNICORN_TIMEOUT=300
```

> **Important:** For `GCP_SA_CREDENTIALS`, paste the **entire contents** of your downloaded service account JSON key file.

---

## Step 7: Build and Deploy

### Option A: One-command deploy

```bash
make deploy
```

This will:
1. Build the Docker image locally
2. Tag and push it to Artifact Registry
3. Deploy to Cloud Run with recommended settings (16 GB RAM, 4 CPUs, gen2)

### Option B: Step by step

```bash
# Build locally
make build

# Push to Artifact Registry
make push

# Deploy to Cloud Run
make deploy
```

### Override defaults

```bash
# Use a different region
make deploy GCP_REGION=europe-west1

# Use a different service name
make deploy CLOUD_RUN_SERVICE=my-nca-api
```

---

## Step 8: Set Environment Variables on Cloud Run

After the initial deploy, set your environment variables on the service:

```bash
gcloud run services update nca-toolkit \
  --region us-central1 \
  --set-env-vars "API_KEY=your_api_key" \
  --set-env-vars "GCP_BUCKET_NAME=your-bucket-name" \
  --set-env-vars "GCP_SA_CREDENTIALS=$(cat path/to/service-account-key.json)" \
  --set-env-vars "GUNICORN_WORKERS=2" \
  --set-env-vars "GUNICORN_TIMEOUT=300"
```

Or set them in the [Cloud Run Console](https://console.cloud.google.com/run) under your service → **Edit & Deploy New Revision** → **Variables & Secrets**.

---

## Step 9: Test the Deployment

Get your service URL:

```bash
make describe
```

Test it:

```bash
curl -X POST https://YOUR_SERVICE_URL/v1/toolkit/test \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json"
```

Or test locally before deploying:

```bash
make run
make test
```

---

## Cloud Run Settings Reference

The Makefile deploys with these defaults:

| Setting | Value | Notes |
|---------|-------|-------|
| Memory | 16 GB | Required for FFmpeg/media processing |
| CPU | 4 | Recommended for parallel encoding |
| Timeout | 300s | Increase for large files |
| Min instances | 0 | Scale to zero when idle (saves cost) |
| Max instances | 5 | Adjust based on expected load |
| Execution env | gen2 | Better performance, required for media workloads |
| Port | 8080 | Default application port |

---

## Optional: Cloud Run Jobs for Long-Running Tasks

For tasks exceeding the 5-minute practical limit (large video processing, batch operations), configure Cloud Run Jobs.

### Create the Job

```bash
gcloud run jobs create nca-toolkit-job \
  --image $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/nca-toolkit/no-code-architects-toolkit:latest \
  --region us-central1 \
  --memory 16Gi \
  --cpu 4 \
  --task-timeout 3600 \
  --max-retries 0 \
  --set-env-vars "API_KEY=your_api_key,GCP_BUCKET_NAME=your-bucket,GCP_SA_CREDENTIALS=..."
```

### Enable Job Triggering

Add these env vars to your Cloud Run **service**:

```bash
gcloud run services update nca-toolkit \
  --region us-central1 \
  --set-env-vars "GCP_JOB_NAME=nca-toolkit-job,GCP_JOB_LOCATION=us-central1"
```

### Grant Permissions

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:nca-toolkit-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.developer"
```

### How It Works

When you send a request with `webhook_url`, the service triggers a Cloud Run Job instead of processing locally. The job runs to completion (up to 24 hours) and sends results to your webhook.

```json
{
  "media_url": "https://example.com/large-video.mp4",
  "webhook_url": "https://your-webhook.com/callback"
}
```

---

## Monitoring

```bash
# Tail live logs
make logs

# View service details
make describe

# View in Console
# https://console.cloud.google.com/run
```

---

## Cost Optimization

- **Min instances = 0**: No charges when idle
- **CPU allocation**: Set to "only during request processing" for lowest cost
- **Right-size resources**: Start with 4 CPU / 16 GB, reduce if your workloads are lighter
- **Cloud Run Jobs**: Use for long-running tasks to avoid keeping services active

---

## Troubleshooting

**Build fails locally**
- Ensure Docker is running and has sufficient resources (8+ GB RAM for build)
- The image compiles FFmpeg from source — initial build takes 15-30 minutes

**Push fails**
- Run `make auth` to re-authenticate with Artifact Registry
- Verify the repository exists: `make repo`
- Check project ID: `gcloud config get-value project`

**Deploy fails**
- Verify APIs are enabled (Step 2)
- Check quotas: Cloud Run has default limits on CPU/memory per region

**Service returns errors**
- Check logs: `make logs`
- Verify env vars are set: `make describe`
- Ensure `GCP_SA_CREDENTIALS` is valid JSON with no extra whitespace

**Requests timing out**
- Increase `GUNICORN_TIMEOUT` env var
- For tasks > 5 min, use `webhook_url` parameter or configure Cloud Run Jobs
- Consider increasing Cloud Run timeout: add `--timeout 600` to deploy command

---

## Makefile Quick Reference

| Command | What it does |
|---------|-------------|
| `make build` | Build Docker image locally |
| `make run` | Run container locally with `.env` |
| `make stop` | Stop local container |
| `make clean` | Stop container and remove image |
| `make test` | Test the running API |
| `make auth` | Authenticate Docker with GCP |
| `make repo` | Create Artifact Registry repo |
| `make push` | Build and push to Artifact Registry |
| `make deploy` | Build, push, deploy to Cloud Run |
| `make logs` | Tail Cloud Run logs |
| `make describe` | Show service details |
| `make help` | Show all targets and config |
