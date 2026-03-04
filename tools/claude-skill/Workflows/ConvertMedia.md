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
- A **local file path** (e.g., `~/videos/clip.mp4`)

### Step 2: Choose the right command

| Scenario | Command |
|----------|---------|
| Convert to any format (mp4, webm, avi, mkv, etc.) | `convert` |
| Convert specifically to MP3 | `convert-mp3` |

### Step 3: Run the command

**General conversion:**
```bash
python3 tools/nca.py convert \
  --file <path> \
  --format <target_format> \
  [--video-codec <codec>] \
  [--audio-codec <codec>] \
  [--video-crf <0-51>]
```

**MP3 conversion:**
```bash
python3 tools/nca.py convert-mp3 \
  --file <path> \
  [--bitrate 128k|192k|256k|320k] \
  [--sample-rate <rate>]
```

`--file` accepts any path — the CLI uploads it automatically. Use `--media-url` instead for URLs.

### Step 4: Return the result

The output file is downloaded to the current directory (or `--output-dir` / `-o` path). The local file path is printed to stdout.

## Examples

**Convert local file to WebM:**
```bash
python3 tools/nca.py convert --file ~/videos/video.mp4 --format webm
```

**Convert and save to Downloads:**
```bash
python3 tools/nca.py convert --file ~/videos/video.mp4 --format webm -o ~/Downloads
```

**Extract high-quality MP3 from video:**
```bash
python3 tools/nca.py convert-mp3 --file ~/videos/video.mp4 --bitrate 320k
```

**Convert from URL with specific codecs:**
```bash
python3 tools/nca.py convert --media-url https://example.com/video.avi --format mp4 --video-codec libx265 --audio-codec aac --video-crf 18
```
