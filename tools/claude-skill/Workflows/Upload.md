---
workflow: upload
purpose: Upload files to cloud storage via the NCA Toolkit API
---

# Upload to Cloud Storage

**Purpose:** Upload files to S3-compatible or GCP storage.

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

Returns the upload details including the public URL if `--public` was set. Use `--json` for the full API response. Use `--bg` to run without blocking.

## Note on File Upload for Processing

When using `--file` on any command (e.g., `transcribe --file ~/audio.mp3`), the CLI automatically uploads the file to the API before processing. No manual upload step is needed.

Cloud Run has a 32 MB request body limit for uploads. For larger files, use Docker volume mounts (`make up-local`) as an alternative.
