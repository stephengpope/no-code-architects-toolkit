---
workflow: caption-video
purpose: Add auto-generated captions to videos using the NCA Toolkit API
---

# Caption Video

**Purpose:** Automatically transcribe and burn captions/subtitles into a video with customizable styling.

## Steps

### Step 1: Identify the video source

The user provides either:
- A **URL** to a publicly accessible video file
- A **local file path** (e.g., `~/videos/video.mp4`)

### Step 2: Determine caption style and options

| Option | Flag | Values |
|--------|------|--------|
| Style | `--style` | `classic`, `karaoke`, `highlight`, `underline`, `word_by_word` |
| Position | `--position` | `bottom_center` (default), `top_center`, `middle_center`, etc. |
| Font size | `--font-size` | Integer (pixels) |
| Font family | `--font-family` | Font name string |
| Word color | `--word-color` | Color for active/highlighted word |
| Line color | `--line-color` | Color for caption text |
| Outline color | `--outline-color` | Color for text outline |
| All caps | `--all-caps` | Flag to uppercase all text |
| Words per line | `--max-words-per-line` | Integer |
| Language | `--language` | Language code or `auto` |

### Step 3: Run the command

```bash
python3 tools/nca.py caption \
  --file <path> \
  [--style karaoke] \
  [--position bottom_center] \
  [--font-size 24] \
  [--font-family "Arial"] \
  [--word-color "#FFD700"] \
  [--line-color "#FFFFFF"] \
  [--outline-color "#000000"] \
  [--all-caps] \
  [--max-words-per-line 5] \
  [--language auto] \
  [-o <output_dir>] [--json] [--bg]
```

`--file` accepts any path — the CLI uploads it automatically. Use `--video-url` instead for URLs.

### Step 4: Return the result

The captioned video is downloaded to the current directory (or `--output-dir` / `-o` path). The local file path is printed to stdout. Use `--json` for the full API response. Use `--bg` to run without blocking (captioning can be slow for long videos).

## Examples

**Caption a local file with karaoke style:**
```bash
python3 tools/nca.py caption --file ~/videos/video.mp4 --style karaoke --position bottom_center
```

**Caption from URL, bold all-caps at the top:**
```bash
python3 tools/nca.py caption --video-url https://example.com/video.mp4 --style classic --position top_center --all-caps --font-size 32
```

**Caption and save to specific directory:**
```bash
python3 tools/nca.py caption --file ~/videos/video.mp4 --style karaoke -o ~/Downloads
```
