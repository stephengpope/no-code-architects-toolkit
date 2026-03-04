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

**From URL:**
```bash
python3 tools/nca.py metadata --media-url <URL>
```

**From local file:**
```bash
python3 tools/nca.py metadata --file ./local/input/video.mp4
```

`--media-url` and `--file` are mutually exclusive. When using `--file` with a remote API, the CLI automatically uploads the file first.

### Step 3: Present results

Returns file size, duration, codec info, resolution, bitrate, and other technical details. Format the results clearly for the user.
