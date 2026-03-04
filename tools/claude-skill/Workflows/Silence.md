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

```bash
python3 tools/nca.py silence \
  --file ~/recordings/audio.mp3 \
  --duration <seconds> \
  [--noise "-30dB"] \
  [--start <time>] \
  [--end <time>]
```

Or from URL:
```bash
python3 tools/nca.py silence \
  --media-url <URL> \
  --duration <seconds> \
  [--noise "-30dB"] \
  [--start <time>] \
  [--end <time>]
```

`--file` accepts any path — the CLI uploads it automatically.

### Step 3: Present results

Returns an array of silence intervals with start/end times printed as JSON to stdout. Useful for finding natural cut points or detecting dead air.
