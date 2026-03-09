# What's New: Makefile, Cloud Deployment, CLI, and Local File Upload

This document summarizes the features added on top of the upstream NCA Toolkit.

---

## Makefile Build System

A complete Makefile replaces manual Docker and gcloud commands with simple one-liners.

### Setup & Config

| Command | Description |
|---------|-------------|
| `make setup` | Generate `.env` file with an auto-generated API key |
| `make connect` | Connect the CLI to a running API instance |
| `make help` | Show all available commands and current configuration |

### Local Development

| Command | Description |
|---------|-------------|
| `make build` | Build Docker image (targets `linux/amd64` for Cloud Run compatibility) |
| `make up` | Build and start container with cloud storage |
| `make up-local` | Build and start with local file I/O via volume mounts |
| `make down` | Stop and remove the container |
| `make clean` | Stop container and remove the Docker image |
| `make test` | Test local API health |
| `make test URL=https://...` | Test a remote deployment |

### GCP Cloud Deployment

| Command | Description |
|---------|-------------|
| `make cloud-setup` | **One-time** GCP project bootstrap — enables APIs, creates Artifact Registry, configures IAM and Docker auth |
| `make cloud-deploy` | Build on Cloud Build (native amd64) and deploy to Cloud Run **(recommended)** |
| `make cloud-build` | Build image remotely on Cloud Build only |
| `make deploy` | Build locally, push, and deploy to Cloud Run (cross-compiles on Apple Silicon) |
| `make logs` | Tail Cloud Run service logs |
| `make describe` | Show Cloud Run service details |

### Configuration Variables

All can be overridden on the command line (e.g., `make deploy GCP_REGION=europe-west1`):

| Variable | Default | Description |
|----------|---------|-------------|
| `GCP_PROJECT_ID` | Current `gcloud` project | GCP project ID |
| `GCP_REGION` | `us-central1` | Deployment region |
| `GCP_REPO` | `nca-toolkit` | Artifact Registry repository name |
| `IMAGE_NAME` | `no-code-architects-toolkit` | Docker image name |
| `CLOUD_RUN_SERVICE` | `nca-toolkit` | Cloud Run service name |

---

## Cloud Deployment Workflow

### First-Time Setup (New GCP Project)

```bash
# 1. Authenticate with GCP
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Generate .env with API key and configure storage credentials
make setup
# Edit .env to add S3 or GCP storage credentials

# 3. One-time GCP project bootstrap
make cloud-setup

# 4. Build and deploy
make cloud-deploy

# 5. Verify
make test URL=https://your-service-url.run.app
```

### What `make cloud-setup` Does

1. Enables required GCP APIs: Cloud Build, Cloud Run, Artifact Registry, Container Registry
2. Creates the Artifact Registry Docker repository
3. Grants IAM permissions to the Cloud Build and Compute service accounts
4. Configures Docker authentication for pushing images

### What `make cloud-deploy` Does

1. Uploads source to Cloud Build (builds natively on amd64 — no cross-compilation)
2. Pushes the built image to Artifact Registry
3. Converts `.env` to YAML and passes all variables to Cloud Run via `--env-vars-file`
4. Deploys to Cloud Run with production settings (16Gi memory, 4 CPUs, gen2 execution)

### Subsequent Deploys

After initial setup, redeployment is a single command:

```bash
make cloud-deploy
```

### Local Build Alternative

If you prefer building locally (slower on Apple Silicon due to cross-compilation):

```bash
make deploy
```

---

## Local File Upload and Processing

Two new endpoints enable uploading local files and retrieving processed output without cloud storage.

### `POST /v1/files/upload`

Upload a local file via multipart form data. Returns a cloud storage URL that can be passed to any processing endpoint.

```bash
curl -X POST http://localhost:8080/v1/files/upload \
  -H "X-API-Key: YOUR_KEY" \
  -F "file=@/path/to/video.mp4"
```

**Response:**
```json
{
  "url": "https://storage.googleapis.com/bucket/uuid.mp4",
  "filename": "video.mp4"
}
```

### `GET /v1/files/content`

Download a processed file from the container's local output directory.

```bash
curl -X GET "http://localhost:8080/v1/files/content?path=/data/output/result.mp4" \
  -H "X-API-Key: YOUR_KEY" \
  --output result.mp4
```

Security: Only serves files from `/data/output` and `LOCAL_STORAGE_PATH`. Path traversal is blocked.

### Local File I/O Mode (No Cloud Storage)

Run with volume mounts to process files entirely locally:

```bash
make up-local
```

This mounts:
- `./local/input/` → `/data/input` (read-only) — place input files here
- `./local/output/` → `/data/output` (writable) — processed files appear here

Reference input files as `file:///data/input/yourfile.mp4` in API requests.

---

## CLI Tool (`tools/nca.py`)

A Python CLI client for interacting with the API from the command line.

### Setup

```bash
# Connect to a running API instance (interactive)
make connect
# — or —
python3 tools/nca.py connect
```

### Key Commands

```bash
# Test connectivity
python3 tools/nca.py test

# Transcribe a media file (local or URL)
python3 tools/nca.py transcribe --file ./video.mp4
python3 tools/nca.py transcribe --url https://example.com/video.mp4

# Run in background with webhook-style polling
python3 tools/nca.py transcribe --file ./video.mp4 --bg

# Output as JSON
python3 tools/nca.py transcribe --file ./video.mp4 --json

# Save output to file
python3 tools/nca.py transcribe --file ./video.mp4 --output-file result.txt
```

The CLI auto-detects local files vs URLs. When given a local file, it uploads via `/v1/files/upload` first, then passes the resulting URL to the processing endpoint.
