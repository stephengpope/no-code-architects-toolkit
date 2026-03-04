---
workflow: video-ops
purpose: Video editing operations - trim, cut, split, concatenate, and thumbnail extraction
---

# Video Operations

**Purpose:** Perform video editing tasks including trimming, cutting, splitting, concatenating, and thumbnail extraction.

## Command Reference

### Trim (keep a portion)

Keep only the content between start and end times:

```bash
python tools/nca.py video-trim \
  --video-url <URL> \
  [--start 00:00:10] \
  [--end 00:01:30]
```

### Cut (remove segments)

Remove specified time ranges from the video:

```bash
python tools/nca.py video-cut \
  --video-url <URL> \
  --cuts "00:00:10-00:00:20" "00:01:00-00:01:15"
```

Each cut is a `start-end` range. Multiple cuts can be specified.

### Split (divide into parts)

Split a video into multiple files at specified boundaries:

```bash
python tools/nca.py video-split \
  --video-url <URL> \
  --splits "00:00:00-00:01:00" "00:01:00-00:02:00" "00:02:00-00:03:00"
```

### Concatenate (join videos)

Combine multiple videos into one:

```bash
python tools/nca.py video-concat \
  --video-urls https://example.com/part1.mp4 https://example.com/part2.mp4
```

### Thumbnail (extract frame)

Extract a single frame as an image:

```bash
python tools/nca.py thumbnail \
  --video-url <URL> \
  [--second 5.0]
```

## Steps

### Step 1: Identify the operation

Match the user's intent to the right command:

| Intent | Command |
|--------|---------|
| "Keep only 0:10 to 1:30" | `video-trim` |
| "Remove the intro" | `video-cut` |
| "Split into 3 parts" | `video-split` |
| "Join these videos" | `video-concat` |
| "Get a thumbnail at 5s" | `thumbnail` |

### Step 2: Extract parameters

Get video URL(s) and time ranges from the user's request.

### Step 3: Run the command and return result

All commands return a cloud URL to the processed video (or array of URLs for split).
