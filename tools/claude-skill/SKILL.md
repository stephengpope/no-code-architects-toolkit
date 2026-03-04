---
name: NCAToolkit
description: NCA Toolkit API client. USE WHEN nca, toolkit, transcribe video, transcribe audio, convert media, caption video, screenshot webpage, video trim, video cut, video split, media metadata, download media, detect silence, ffmpeg compose.
---

# NCA Toolkit Skill

Client for the No-Code Architects Toolkit API. Provides media processing capabilities including transcription, conversion, captioning, video editing, screenshots, and more.

## Prerequisites

Set these environment variables before using:
```bash
export NCA_API_URL=https://your-nca-instance.run.app
export NCA_API_KEY=your_api_key
```

The CLI tool is located at the project root: `tools/nca.py` (zero dependencies beyond Python 3).

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
| test, connect, authenticate, status | `Workflows/TestConnect.md` |

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
| `test` | Verify API connectivity |
| `status` | Check async job status |

## Examples

**Transcribe a video:**
```
User: "Transcribe this video: https://example.com/talk.mp4"
-> python tools/nca.py transcribe --media-url https://example.com/talk.mp4
```

**Caption a video with karaoke style:**
```
User: "Add captions to this video with karaoke highlighting"
-> python tools/nca.py caption --video-url https://example.com/video.mp4 --style karaoke
```

**Convert video to WebM:**
```
User: "Convert this MP4 to WebM format"
-> python tools/nca.py convert --media-url https://example.com/video.mp4 --format webm
```

**Screenshot a webpage:**
```
User: "Take a full-page screenshot of https://example.com"
-> python tools/nca.py screenshot --url https://example.com --full-page
```
