---
workflow: upload
purpose: Upload files to cloud storage via the NCA Toolkit API
---

# Upload to Cloud Storage

**Purpose:** Upload files to S3-compatible or GCP storage.

## Steps

### Step 1: Identify the file URL and target storage

| Target | Command |
|--------|---------|
| S3-compatible storage | `upload-s3` |
| Google Cloud Storage | `upload-gcp` |

### Step 2: Run the command

```bash
python tools/nca.py upload-s3 --file-url <URL> [--filename <name>] [--public]
python tools/nca.py upload-gcp --file-url <URL> [--filename <name>] [--public]
```

### Step 3: Present results

Returns the upload details including the public URL if `--public` was set.
