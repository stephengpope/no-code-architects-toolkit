---
workflow: metadata
purpose: Get media file metadata using the NCA Toolkit API
---

# Media Metadata

**Purpose:** Extract comprehensive metadata from media files including format, codecs, resolution, duration, and bitrates.

## Steps

### Step 1: Get the media source

The user provides either a URL or a local file path.

### Step 2: Run the command

```bash
python3 tools/nca.py metadata --file ~/videos/video.mp4
```

Or from URL:
```bash
python3 tools/nca.py metadata --media-url <URL>
```

`--file` accepts any path — the CLI uploads it automatically.

### Step 3: Present results

Returns file size, duration, codec info, resolution, bitrate, and other technical details printed as formatted JSON to stdout.
