---
workflow: upload
purpose: Upload files to cloud storage via the NCA Toolkit API
---

# Upload to Cloud Storage

**Purpose:** Upload files to S3-compatible or GCP storage, or upload a local file to the API for processing.

## File Upload (for processing)

Upload a local file to the API so it can be used with any processing endpoint. This is handled automatically by `--file` on all commands, but can also be done manually:

```bash
python3 tools/nca.py upload --file ./local/input/video.mp4
```

Returns a cloud URL that can be passed to any `--media-url` or `--video-url` parameter.

**Note:** Cloud Run has a 32 MB request body limit. For larger files, use Docker volume mounts (`make up-local`) instead.

## Cloud Storage Upload

### Step 1: Identify the file URL and target storage

| Target | Command |
|--------|---------|
| S3-compatible storage | `upload-s3` |
| Google Cloud Storage | `upload-gcp` |

### Step 2: Run the command

```bash
python3 tools/nca.py upload-s3 --file-url <URL> [--filename <name>] [--public]
python3 tools/nca.py upload-gcp --file-url <URL> [--filename <name>] [--public]
```

### Step 3: Present results

Returns the upload details including the public URL if `--public` was set.
