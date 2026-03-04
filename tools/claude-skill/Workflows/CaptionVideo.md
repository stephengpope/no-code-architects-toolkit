---
workflow: caption-video
purpose: Add auto-generated captions to videos using the NCA Toolkit API
---

# Caption Video

**Purpose:** Automatically transcribe and burn captions/subtitles into a video with customizable styling.

## Steps

### Step 1: Identify the video URL

Extract the video URL from the user's request. Must be publicly accessible.

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
python tools/nca.py caption \
  --video-url <URL> \
  [--style karaoke] \
  [--position bottom_center] \
  [--font-size 24] \
  [--font-family "Arial"] \
  [--word-color "#FFD700"] \
  [--line-color "#FFFFFF"] \
  [--outline-color "#000000"] \
  [--all-caps] \
  [--max-words-per-line 5] \
  [--language auto]
```

### Step 4: Return the result

The API returns a cloud URL to the captioned video. Present this to the user.

## Examples

**Karaoke-style captions:**
```bash
python tools/nca.py caption --video-url https://example.com/video.mp4 --style karaoke --position bottom_center
```

**Bold all-caps captions at the top:**
```bash
python tools/nca.py caption --video-url https://example.com/video.mp4 --style classic --position top_center --all-caps --font-size 32
```
