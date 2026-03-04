---
workflow: download
purpose: Download media from URLs using the NCA Toolkit API (yt-dlp backend)
---

# Download Media

**Purpose:** Download media content from various online sources using yt-dlp.

## Steps

### Step 1: Get the media URL
### Step 2: Run the command

```bash
python tools/nca.py download --media-url <URL> [--webhook-url <WEBHOOK>]
```

### Step 3: Present results

Returns a cloud storage URL where the downloaded media has been saved. This is the BETA endpoint and supports many video/audio platforms.
