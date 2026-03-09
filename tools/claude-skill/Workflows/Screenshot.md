---
workflow: screenshot
purpose: Capture screenshots of webpages using the NCA Toolkit API
---

# Screenshot Webpage

**Purpose:** Take screenshots of web pages with configurable viewport, full-page capture, and format options.

## Steps

### Step 1: Get the URL or HTML

The user provides either a URL to screenshot or raw HTML content to render.

### Step 2: Determine options

| Option | Flag | Default |
|--------|------|---------|
| Viewport width | `--viewport-width` | Browser default |
| Viewport height | `--viewport-height` | Browser default |
| Full page | `--full-page` | False |
| Format | `--format` | png |
| Delay (ms) | `--delay` | 0 |

### Step 3: Run the command

```bash
python tools/nca.py screenshot \
  --url <URL> \
  [--full-page] \
  [--viewport-width 1920] \
  [--viewport-height 1080] \
  [--format png|jpeg] \
  [--delay 2000]
```

Or with raw HTML:
```bash
python tools/nca.py screenshot \
  --html "<html><body><h1>Hello</h1></body></html>"
```

### Step 4: Return the result

The screenshot image is downloaded to the current directory (or `-o` path). The local file path is printed to stdout. Use `--json` for the full API response. Use `--bg` to run without blocking.

## Examples

**Full-page screenshot:**
```bash
python tools/nca.py screenshot --url https://example.com --full-page
```

**Mobile viewport:**
```bash
python tools/nca.py screenshot --url https://example.com --viewport-width 375 --viewport-height 812
```
