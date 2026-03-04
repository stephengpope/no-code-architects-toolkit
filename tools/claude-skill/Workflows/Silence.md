---
workflow: silence
purpose: Detect silence intervals in media using the NCA Toolkit API
---

# Detect Silence

**Purpose:** Find silent intervals in audio/video files.

## Steps

### Step 1: Get the media source and minimum silence duration

The user provides either a URL or a local file path.

### Step 2: Run the command

**From URL:**
```bash
python3 tools/nca.py silence \
  --media-url <URL> \
  --duration <seconds> \
  [--noise "-30dB"] \
  [--start <time>] \
  [--end <time>]
```

**From local file:**
```bash
python3 tools/nca.py silence \
  --file ./local/input/audio.mp3 \
  --duration <seconds> \
  [--noise "-30dB"] \
  [--start <time>] \
  [--end <time>]
```

`--media-url` and `--file` are mutually exclusive. When using `--file` with a remote API, the CLI automatically uploads the file first.

### Step 3: Present results

Returns an array of silence intervals with start/end times. Useful for finding natural cut points or detecting dead air.
