---
workflow: convert-media
purpose: Convert media files between formats using the NCA Toolkit API
---

# Convert Media

**Purpose:** Convert audio/video files between formats, or extract audio as MP3.

## Steps

### Step 1: Identify the media URL and target format

Extract the source URL and desired output format from the user's request.

### Step 2: Choose the right command

| Scenario | Command |
|----------|---------|
| Convert to any format (mp4, webm, avi, mkv, etc.) | `convert` |
| Convert specifically to MP3 | `convert-mp3` |

### Step 3: Run the command

**General conversion:**
```bash
python tools/nca.py convert \
  --media-url <URL> \
  --format <target_format> \
  [--video-codec <codec>] \
  [--audio-codec <codec>] \
  [--video-crf <0-51>]
```

**MP3 conversion:**
```bash
python tools/nca.py convert-mp3 \
  --media-url <URL> \
  [--bitrate 128k|192k|256k|320k] \
  [--sample-rate <rate>]
```

### Step 4: Return the result

The API returns a cloud URL to the converted file. Present this URL to the user.

## Examples

**Convert MP4 to WebM:**
```bash
python tools/nca.py convert --media-url https://example.com/video.mp4 --format webm
```

**Extract high-quality MP3 from video:**
```bash
python tools/nca.py convert-mp3 --media-url https://example.com/video.mp4 --bitrate 320k
```

**Convert with specific codecs:**
```bash
python tools/nca.py convert --media-url https://example.com/video.avi --format mp4 --video-codec libx265 --audio-codec aac --video-crf 18
```
