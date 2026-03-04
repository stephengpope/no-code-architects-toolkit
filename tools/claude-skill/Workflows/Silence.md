---
workflow: silence
purpose: Detect silence intervals in media using the NCA Toolkit API
---

# Detect Silence

**Purpose:** Find silent intervals in audio/video files.

## Steps

### Step 1: Get the media URL and minimum silence duration
### Step 2: Run the command

```bash
python tools/nca.py silence \
  --media-url <URL> \
  --duration <seconds> \
  [--noise "-30dB"] \
  [--start <time>] \
  [--end <time>]
```

### Step 3: Present results

Returns an array of silence intervals with start/end times. Useful for finding natural cut points or detecting dead air.
