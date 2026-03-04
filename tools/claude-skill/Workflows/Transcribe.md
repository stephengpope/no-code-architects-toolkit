---
workflow: transcribe
purpose: Transcribe or translate audio/video content using the NCA Toolkit API
---

# Transcribe Media

**Purpose:** Transcribe audio/video to text, or translate to English, using OpenAI Whisper via the NCA Toolkit.

## Steps

### Step 1: Identify the media URL

Extract the media URL from the user's request. The URL must be publicly accessible.

### Step 2: Determine options

| Option | Flag | When to use |
|--------|------|-------------|
| Translate | `--task translate` | User wants translation to English |
| Language | `--language XX` | User specifies source language |
| SRT output | `--srt` | User wants subtitles/SRT format |
| Segments | `--segments` | User wants timestamped segments |
| Word timestamps | `--word-timestamps` | User wants per-word timing |
| Words per line | `--words-per-line N` | Control subtitle line length |

### Step 3: Run the command

```bash
python tools/nca.py transcribe \
  --media-url <URL> \
  [--task transcribe|translate] \
  [--language <code>] \
  [--srt] \
  [--segments] \
  [--word-timestamps] \
  [--words-per-line <N>]
```

### Step 4: Present results

The API returns JSON with:
- `response.text` - Full transcription text
- `response.srt` - SRT subtitle content (if requested)
- `response.segments` - Timestamped segments (if requested)

Present the transcription text to the user. If SRT was requested, show or save the SRT content.

## Examples

**Basic transcription:**
```bash
python tools/nca.py transcribe --media-url https://example.com/podcast.mp3
```

**Translate to English with SRT:**
```bash
python tools/nca.py transcribe --media-url https://example.com/spanish-video.mp4 --task translate --srt
```

**Transcribe with word-level timestamps:**
```bash
python tools/nca.py transcribe --media-url https://example.com/interview.wav --word-timestamps --segments
```
