---
workflow: metadata
purpose: Get media file metadata using the NCA Toolkit API
---

# Media Metadata

**Purpose:** Extract comprehensive metadata from media files including format, codecs, resolution, duration, and bitrates.

## Steps

### Step 1: Get the media URL
### Step 2: Run the command

```bash
python tools/nca.py metadata --media-url <URL>
```

### Step 3: Present results

Returns file size, duration, codec info, resolution, bitrate, and other technical details. Format the results clearly for the user.
