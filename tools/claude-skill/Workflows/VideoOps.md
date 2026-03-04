---
workflow: video-ops
purpose: Video editing operations - trim, cut, split, concatenate, and thumbnail extraction
---

# Video Operations

**Purpose:** Perform video editing tasks including trimming, cutting, splitting, concatenating, and thumbnail extraction.

All video commands accept `--file <path>` (any local path, uploaded automatically) or `--video-url <URL>`. Output files are downloaded to the current directory (use `-o` to change). All commands also support `--json` for full JSON output and `--bg` to run without blocking.

## Command Reference

### Trim (keep a portion)

Keep only the content between start and end times:

```bash
python3 tools/nca.py video-trim \
  --file ~/videos/video.mp4 \
  [--start 00:00:10] \
  [--end 00:01:30]
```

### Cut (remove segments)

Remove specified time ranges from the video:

```bash
python3 tools/nca.py video-cut \
  --file ~/videos/video.mp4 \
  --cuts "00:00:10-00:00:20" "00:01:00-00:01:15"
```

Each cut is a `start-end` range. Multiple cuts can be specified.

### Split (divide into parts)

Split a video into multiple files at specified boundaries:

```bash
python3 tools/nca.py video-split \
  --file ~/videos/video.mp4 \
  --splits "00:00:00-00:01:00" "00:01:00-00:02:00" "00:02:00-00:03:00"
```

### Concatenate (join videos)

Combine multiple videos into one:

```bash
python3 tools/nca.py video-concat \
  --files ~/videos/part1.mp4 ~/videos/part2.mp4

python3 tools/nca.py video-concat \
  --video-urls https://example.com/part1.mp4 https://example.com/part2.mp4
```

For concatenation, use `--files` (plural) for local files and `--video-urls` for URLs.

### Thumbnail (extract frame)

Extract a single frame as an image:

```bash
python3 tools/nca.py thumbnail \
  --file ~/videos/video.mp4 \
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

Get video file path (or URL) and time ranges from the user's request.

### Step 3: Run the command and return result

Output files are downloaded to the current directory. For split, multiple files are downloaded. The local file path(s) are printed to stdout.
