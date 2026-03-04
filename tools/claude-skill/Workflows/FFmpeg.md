---
workflow: ffmpeg
purpose: Run custom FFmpeg compose commands via the NCA Toolkit API
---

# FFmpeg Compose

**Purpose:** Execute arbitrary FFmpeg pipelines for advanced media processing.

## Steps

### Step 1: Build the FFmpeg compose payload

The payload is a JSON object with:
- `inputs` - Array of input files with options (use `file_url` for URLs)
- `filters` - Array of FFmpeg filter strings
- `outputs` - Array of output configurations
- `global_options` - Global FFmpeg options

### Step 2: Run the command

```bash
python3 tools/nca.py ffmpeg --payload '{
  "inputs": [{"file_url": "https://example.com/video.mp4"}],
  "outputs": [{"options": [{"option": "-c:v", "argument": "libx264"}, {"option": "-crf", "argument": "23"}]}]
}'
```

For local files, upload the file first using the upload endpoint, then use the returned URL in the payload.

### Step 3: Present results

Output files are downloaded to the current directory (or `--output-dir` / `-o` path). The local file path(s) are printed to stdout. Use `--json` for the full API response. Use `--bg` to run without blocking.

## Notes

This is the most flexible endpoint. Use it for operations not covered by other commands (e.g., overlay, speed changes, complex filter graphs).
