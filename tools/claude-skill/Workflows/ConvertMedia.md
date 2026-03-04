---
workflow: convert-media
purpose: Convert media files between formats using the NCA Toolkit API
---

# Convert Media

**Purpose:** Convert audio/video files between formats, or extract audio as MP3.

## Steps

### Step 1: Identify the media source and target format

The user provides either:
- A **URL** to a publicly accessible media file
- A **local file path** (e.g., `./local/input/video.mp4`)

### Step 2: Choose the right command

| Scenario | Command |
|----------|---------|
| Convert to any format (mp4, webm, avi, mkv, etc.) | `convert` |
| Convert specifically to MP3 | `convert-mp3` |

### Step 3: Run the command

**General conversion (from URL):**
```bash
python3 tools/nca.py convert \
  --media-url <URL> \
  --format <target_format> \
  [--video-codec <codec>] \
  [--audio-codec <codec>] \
  [--video-crf <0-51>]
```

**General conversion (from local file):**
```bash
python3 tools/nca.py convert \
  --file <path> \
  --format <target_format> \
  [--video-codec <codec>] \
  [--audio-codec <codec>] \
  [--video-crf <0-51>]
```

**MP3 conversion (from URL):**
```bash
python3 tools/nca.py convert-mp3 \
  --media-url <URL> \
  [--bitrate 128k|192k|256k|320k] \
  [--sample-rate <rate>]
```

**MP3 conversion (from local file):**
```bash
python3 tools/nca.py convert-mp3 \
  --file <path> \
  [--bitrate 128k|192k|256k|320k] \
  [--sample-rate <rate>]
```

`--media-url` and `--file` are mutually exclusive. When using `--file` with a remote API, the CLI automatically uploads the file first.

### Step 4: Return the result

The API returns a cloud URL to the converted file. Present this URL to the user.

## Examples

**Convert MP4 to WebM (URL):**
```bash
python3 tools/nca.py convert --media-url https://example.com/video.mp4 --format webm
```

**Convert local file to WebM:**
```bash
python3 tools/nca.py convert --file ./local/input/video.mp4 --format webm
```

**Extract high-quality MP3 from video:**
```bash
python3 tools/nca.py convert-mp3 --media-url https://example.com/video.mp4 --bitrate 320k
```

**Extract MP3 from local file:**
```bash
python3 tools/nca.py convert-mp3 --file ./local/input/video.mp4 --bitrate 320k
```

**Convert with specific codecs:**
```bash
python3 tools/nca.py convert --media-url https://example.com/video.avi --format mp4 --video-codec libx265 --audio-codec aac --video-crf 18
```
