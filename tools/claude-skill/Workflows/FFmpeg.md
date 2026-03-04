---
workflow: ffmpeg
purpose: Run custom FFmpeg compose commands via the NCA Toolkit API
---

# FFmpeg Compose

**Purpose:** Execute arbitrary FFmpeg pipelines for advanced media processing.

## Steps

### Step 1: Build the FFmpeg compose payload

The payload is a JSON object with:
- `inputs` - Array of input files with options
- `filters` - Array of FFmpeg filter strings
- `outputs` - Array of output configurations
- `global_options` - Global FFmpeg options

### Step 2: Run the command

```bash
python tools/nca.py ffmpeg --payload '{
  "inputs": [{"file_url": "https://example.com/video.mp4"}],
  "outputs": [{"options": [{"option": "-c:v", "argument": "libx264"}, {"option": "-crf", "argument": "23"}]}]
}'
```

### Step 3: Present results

Returns an array of output objects with cloud URLs to the processed files.

## Notes

This is the most flexible endpoint. Use it for operations not covered by other commands (e.g., overlay, speed changes, complex filter graphs).
