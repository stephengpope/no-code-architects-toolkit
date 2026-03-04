---
workflow: transcribe
purpose: Transcribe or translate audio/video content using the NCA Toolkit API
---

# Transcribe Media

**Purpose:** Transcribe audio/video to text, or translate to English, using OpenAI Whisper via the NCA Toolkit.

## Steps

### Step 1: Identify the media source

The user provides either:
- A **URL** to a publicly accessible media file
- A **local file path** (e.g., `~/recordings/meeting.mp3`)

### Step 2: Determine options

| Option | Flag | When to use |
|--------|------|-------------|
| Translate | `--task translate` | User wants translation to English |
| Language | `--language XX` | User specifies source language |
| SRT output | `--srt` | User wants subtitles/SRT format |
| Segments | `--segments` | User wants timestamped segments |
| Word timestamps | `--word-timestamps` | User wants per-word timing |
| Words per line | `--words-per-line N` | Control subtitle line length |
| Output file | `--output-file <path>` | Write transcription to a file instead of stdout |
| JSON output | `--json` | Get full API response as JSON |
| Background | `--bg` | Run without blocking (returns job ID) |

### Step 3: Run the command

```bash
python3 tools/nca.py transcribe \
  --file <path> \
  [--task transcribe|translate] \
  [--language <code>] \
  [--srt] \
  [--segments] \
  [--word-timestamps] \
  [--words-per-line <N>] \
  [--output-file <path>] \
  [--json] \
  [--bg]
```

Or with a URL:
```bash
python3 tools/nca.py transcribe \
  --media-url <URL> \
  [options...]
```

`--media-url` and `--file` are mutually exclusive. `--file` accepts any path — the CLI uploads it automatically.

### Step 4: Present results

The transcription text is printed directly to stdout. If `--srt` was requested, SRT content is also printed. Use `--json` for the full API response. Use `--output-file` to write results to a file (writes JSON when combined with `--json`).

## Examples

**Transcribe a local file:**
```bash
python3 tools/nca.py transcribe --file ~/recordings/meeting.mp3
```

**Transcribe and save to a file:**
```bash
python3 tools/nca.py transcribe --file ~/recordings/meeting.mp3 --output-file transcript.txt
```

**Transcribe and save full JSON to a file:**
```bash
python3 tools/nca.py transcribe --file ~/recordings/meeting.mp3 --json --output-file result.json
```

**Transcribe from URL:**
```bash
python3 tools/nca.py transcribe --media-url https://example.com/podcast.mp3
```

**Translate to English with SRT:**
```bash
python3 tools/nca.py transcribe --file ~/videos/spanish-video.mp4 --task translate --srt
```

**Transcribe with word-level timestamps (JSON output):**
```bash
python3 tools/nca.py transcribe --file ~/recordings/interview.wav --word-timestamps --segments --json
```

**Run in background for long files:**
```bash
python3 tools/nca.py transcribe --file ~/recordings/long-meeting.mp3 --bg
# Returns job ID, then:
python3 tools/nca.py wait <job_id>
```
