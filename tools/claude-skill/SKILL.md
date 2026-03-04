---
name: NCAToolkit
description: NCA Toolkit API client. USE WHEN nca, toolkit, transcribe video, transcribe audio, convert media, caption video, screenshot webpage, video trim, video cut, video split, media metadata, download media, detect silence, ffmpeg compose, upload file, local file.
---

# NCA Toolkit Skill

Client for the No-Code Architects Toolkit API. Provides media processing capabilities including transcription, conversion, captioning, video editing, screenshots, and more. Supports both URL inputs and local file inputs.

## Prerequisites

Run setup to authenticate and save credentials:
```bash
python3 tools/nca.py connect
```

This saves credentials to `~/.nca-toolkit/config` (600 permissions, INI format).
Environment variables `NCA_API_URL` and `NCA_API_KEY` override the config file if set.

The CLI tool is located at the project root: `tools/nca.py` (zero dependencies beyond Python 3).

## Local File Support

The CLI supports local files via `--file` (or `-f`) in addition to `--media-url`/`--video-url`:

- **Local API** (`make up-local`): Files in `./local/input/` are volume-mounted into the container. The CLI translates `--file` to a `file://` URI.
- **Remote API** (Cloud Run): The CLI automatically uploads the file via `/v1/files/upload`, then passes the cloud URL to the processing endpoint.
- **Output**: Local API saves to `./local/output/`. Remote API returns a cloud storage URL.

```bash
# Local file (auto-detects local vs remote API)
python3 tools/nca.py transcribe --file ./local/input/video.mp4

# URL (works with any API)
python3 tools/nca.py transcribe --media-url https://example.com/video.mp4
```

## Voice Notification

```bash
curl -s -X POST http://localhost:8888/notify \
  -H "Content-Type: application/json" \
  -d '{"message": "Running the NCA Toolkit skill to process media"}' \
  > /dev/null 2>&1 &
```

## Workflow Routing

| Trigger | Workflow |
|---------|----------|
| transcribe, translate, transcription | `Workflows/Transcribe.md` |
| convert, format, mp3, encode | `Workflows/ConvertMedia.md` |
| caption, subtitle, captions | `Workflows/CaptionVideo.md` |
| trim, cut, split, concatenate, concat, thumbnail, video edit | `Workflows/VideoOps.md` |
| screenshot, webpage, capture page | `Workflows/Screenshot.md` |
| metadata, media info, file info | `Workflows/Metadata.md` |
| download, save media | `Workflows/Download.md` |
| silence, detect silence | `Workflows/Silence.md` |
| ffmpeg, compose, custom ffmpeg | `Workflows/FFmpeg.md` |
| upload, s3, gcp storage | `Workflows/Upload.md` |
| connect, configure, authenticate, setup | `Workflows/Setup.md` |
| test, status, check connection | `Workflows/TestConnect.md` |

## Quick Reference

| Command | What It Does |
|---------|-------------|
| `transcribe` | Transcribe/translate audio or video via Whisper |
| `convert` | Convert media between formats (mp4, webm, avi, etc.) |
| `convert-mp3` | Convert any media to MP3 |
| `caption` | Auto-generate and burn captions into video |
| `video-trim` | Keep only a portion of a video |
| `video-cut` | Remove segments from a video |
| `video-split` | Split video into multiple files |
| `video-concat` | Join multiple videos together |
| `thumbnail` | Extract a frame as an image |
| `screenshot` | Capture a webpage as an image |
| `metadata` | Get codec, resolution, duration, bitrate info |
| `download` | Download media from any URL (uses yt-dlp) |
| `silence` | Find silent intervals in audio/video |
| `ffmpeg` | Run arbitrary FFmpeg pipelines |
| `upload-s3` | Upload file to S3-compatible storage |
| `upload-gcp` | Upload file to Google Cloud Storage |
| `connect` | Connect CLI to a running API and save to ~/.nca-toolkit/config |
| `config` | Show current configuration (redacted keys) |
| `test` | Verify API connectivity |
| `status` | Check async job status |

## Input Options

All media commands accept either a URL or a local file:

| Flag | Description |
|------|-------------|
| `--media-url <URL>` / `--video-url <URL>` | Process media from a URL |
| `--file <path>` / `-f <path>` | Process a local file (auto-uploads if API is remote) |

These are mutually exclusive — use one or the other.

## Examples

**Transcribe a video (URL):**
```
User: "Transcribe this video: https://example.com/talk.mp4"
-> python3 tools/nca.py transcribe --media-url https://example.com/talk.mp4
```

**Transcribe a local file:**
```
User: "Transcribe this file: ./local/input/meeting.mp4"
-> python3 tools/nca.py transcribe --file ./local/input/meeting.mp4
```

**Caption a video with karaoke style:**
```
User: "Add captions to this video with karaoke highlighting"
-> python3 tools/nca.py caption --video-url https://example.com/video.mp4 --style karaoke
```

**Convert a local file to WebM:**
```
User: "Convert this video to WebM"
-> python3 tools/nca.py convert --file ./local/input/video.mp4 --format webm
```

**Screenshot a webpage:**
```
User: "Take a full-page screenshot of https://example.com"
-> python3 tools/nca.py screenshot --url https://example.com --full-page
```
