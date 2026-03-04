#!/usr/bin/env python3
"""
NCA Toolkit CLI - Command-line client for the No-Code Architects Toolkit API.

Configuration (checked in this order):
  1. Environment variables: NCA_API_URL, NCA_API_KEY
  2. Config file: ~/.nca-toolkit/config

Usage:
  python nca.py <command> [options]

  python nca.py connect              Interactive setup — prompts for URL & key, validates, saves config
  python nca.py test               Test API connectivity
  python nca.py transcribe ...     Transcribe or translate media
  python nca.py config             Show current configuration (redacted key)
"""

import argparse
import configparser
import json
import os
import stat
import sys
import urllib.request
import urllib.error

# ─── Config File System ───────────────────────────────────────────────────────

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".nca-toolkit")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config")


def read_config_file():
    """Read config from ~/.nca-toolkit/config (INI format)."""
    if not os.path.isfile(CONFIG_FILE):
        return {}, {}

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    result = {}
    profiles = {}

    # Read [default] section
    if config.has_section("default"):
        for key in config["default"]:
            result[key] = config["default"][key].strip('"').strip("'")

    # Read any additional profile sections
    for section in config.sections():
        if section != "default":
            profiles[section] = {}
            for key in config[section]:
                profiles[section][key] = config[section][key].strip('"').strip("'")

    return result, profiles


def write_config_file(api_url, api_key, profile="default"):
    """Write config to ~/.nca-toolkit/config with secure permissions."""
    os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)

    config = configparser.ConfigParser()

    # Preserve existing config
    if os.path.isfile(CONFIG_FILE):
        config.read(CONFIG_FILE)

    if not config.has_section(profile):
        config.add_section(profile)

    config.set(profile, "api_url", f'"{api_url}"')
    config.set(profile, "api_key", f'"{api_key}"')

    with open(CONFIG_FILE, "w") as f:
        f.write("# NCA Toolkit Configuration\n")
        f.write(f"# Last updated: {__import__('datetime').datetime.now().isoformat()}\n")
        f.write("# Docs: https://github.com/stephengpope/no-code-architects-toolkit\n\n")
        config.write(f)

    # Secure permissions: owner read/write only
    os.chmod(CONFIG_FILE, stat.S_IRUSR | stat.S_IWUSR)
    os.chmod(CONFIG_DIR, stat.S_IRWXU)


def get_config(profile="default"):
    """Load API config. Priority: env vars > config file."""
    url = os.environ.get("NCA_API_URL", "").rstrip("/")
    key = os.environ.get("NCA_API_KEY", "")

    # Fall back to config file
    if not url or not key:
        file_config, profiles = read_config_file()

        # Check requested profile, fall back to default
        if profile != "default" and profile in profiles:
            source = profiles[profile]
        else:
            source = file_config

        if not url:
            url = source.get("api_url", "").rstrip("/")
        if not key:
            key = source.get("api_key", "")

    if not url:
        print("Error: API URL not configured.", file=sys.stderr)
        print("  Run: python nca.py connect", file=sys.stderr)
        print("  Or:  export NCA_API_URL=https://your-nca-instance.run.app", file=sys.stderr)
        sys.exit(1)
    if not key:
        print("Error: API key not configured.", file=sys.stderr)
        print("  Run: python nca.py connect", file=sys.stderr)
        print("  Or:  export NCA_API_KEY=your_api_key", file=sys.stderr)
        sys.exit(1)

    return url, key


def api_request(endpoint, payload=None, method="POST"):
    """Make an authenticated request to the NCA Toolkit API."""
    url, key = get_config()
    full_url = f"{url}{endpoint}"

    headers = {
        "X-API-Key": key,
    }

    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode()

    req = urllib.request.Request(full_url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            body = json.loads(resp.read().decode())
            return body
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            error_json = json.loads(error_body)
            print(json.dumps(error_json, indent=2), file=sys.stderr)
        except json.JSONDecodeError:
            print(f"HTTP {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def file_to_uri(local_path):
    """Convert a local file path to a file:// URI for the container's /data/input mount."""
    basename = os.path.basename(local_path)
    return f"file:///data/input/{basename}"


def translate_output_paths(obj):
    """Translate file:///data/output/... paths to ./local/output/... for display."""
    if isinstance(obj, str) and obj.startswith("file:///data/output/"):
        return "./local/output/" + obj[len("file:///data/output/"):]
    if isinstance(obj, dict):
        return {k: translate_output_paths(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [translate_output_paths(v) for v in obj]
    return obj


def print_result(result):
    """Print API result as formatted JSON, translating file:// paths for readability."""
    result = translate_output_paths(result)
    print(json.dumps(result, indent=2))


# ─── Command Handlers ─────────────────────────────────────────────────────────


def cmd_connect(args):
    """Connect to a running NCA Toolkit API — validate and save to ~/.nca-toolkit/config."""
    profile = getattr(args, "profile", "default")

    print("")
    print("  NCA Toolkit — Connect to API")
    print("  " + "─" * 50)
    print("")
    print("  This connects your CLI to a running NCA Toolkit API.")
    print("  You need the URL where it's running and the API key")
    print("  you configured when deploying it (the API_KEY env var).")
    print("")

    # Get URL — default to localhost for local development
    default_url = os.environ.get("NCA_API_URL", "")
    if not default_url:
        file_config, _ = read_config_file()
        default_url = file_config.get("api_url", "")
    if not default_url:
        default_url = "http://localhost:8080"

    print("  Where is your NCA Toolkit API running?")
    print("    Local Docker:  http://localhost:8080")
    print("    Cloud Run:     https://your-service-xxxxx.run.app")
    print("")
    prompt = f"  API URL [{default_url}]: "
    api_url = input(prompt).strip() or default_url

    api_url = api_url.rstrip("/")

    # Get API key
    default_key = os.environ.get("NCA_API_KEY", "")
    if not default_key:
        file_config, _ = read_config_file()
        default_key = file_config.get("api_key", "")

    print("")
    print("  Enter the API key you set as the API_KEY environment")
    print("  variable when deploying. If you haven't set one yet,")
    print("  generate one with:")
    print("")
    print("    python3 -c \"import secrets; print(secrets.token_urlsafe(32))\"")
    print("")
    print("  Then add it as API_KEY in your .env file or Cloud Run config.")
    print("")

    prompt = "  API Key"
    if default_key:
        prompt += f" [{default_key[:8]}...]"
    prompt += ": "
    api_key = input(prompt).strip() or default_key

    if not api_key:
        print("  Error: API key is required.", file=sys.stderr)
        sys.exit(1)

    # Validate by calling the test endpoint
    print("")
    print("  Validating credentials...")

    headers = {
        "X-API-Key": api_key,
    }
    req = urllib.request.Request(
        f"{api_url}/v1/toolkit/test", headers=headers, method="GET"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp.read()
            print("  Authentication successful!")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("  Error: Authentication failed — invalid API key.", file=sys.stderr)
            sys.exit(1)
        elif e.code == 403:
            print("  Error: Access forbidden — check your API key.", file=sys.stderr)
            sys.exit(1)
        else:
            # Non-auth error means the server is reachable, key may be fine
            print(f"  Warning: Server returned HTTP {e.code}, but connection works.")
    except urllib.error.URLError as e:
        print(f"  Error: Cannot reach {api_url} — {e.reason}", file=sys.stderr)
        sys.exit(1)

    # Save to config file
    write_config_file(api_url, api_key, profile=profile)

    print("")
    print(f"  Config saved to {CONFIG_FILE}")
    print(f"  Profile: [{profile}]")
    print(f"  Permissions: 600 (owner read/write only)")
    print("")
    print("  You're all set! Try: python3 tools/nca.py test")
    print("")


def cmd_config(args):
    """Show current configuration."""
    file_config, profiles = read_config_file()

    print("")
    print("  NCA Toolkit — Configuration")
    print("  " + "─" * 40)

    # Show env var status
    env_url = os.environ.get("NCA_API_URL", "")
    env_key = os.environ.get("NCA_API_KEY", "")
    print("")
    print("  Environment variables:")
    print(f"    NCA_API_URL = {env_url or '(not set)'}")
    print(f"    NCA_API_KEY = {env_key[:8] + '...' if env_key else '(not set)'}")

    # Show config file
    print("")
    print(f"  Config file: {CONFIG_FILE}")
    if os.path.isfile(CONFIG_FILE):
        file_stat = os.stat(CONFIG_FILE)
        perms = oct(file_stat.st_mode)[-3:]
        print(f"  Permissions: {perms}")
        print("")
        print("  [default]")
        print(f"    api_url = {file_config.get('api_url', '(not set)')}")
        key = file_config.get("api_key", "")
        print(f"    api_key = {key[:8] + '...' if key else '(not set)'}")

        for name, cfg in profiles.items():
            print(f"")
            print(f"  [{name}]")
            print(f"    api_url = {cfg.get('api_url', '(not set)')}")
            pkey = cfg.get("api_key", "")
            print(f"    api_key = {pkey[:8] + '...' if pkey else '(not set)'}")
    else:
        print("  (not found — run: python nca.py connect)")

    # Show effective config
    print("")
    print("  Effective config (what commands will use):")
    eff_url = env_url or file_config.get("api_url", "")
    eff_key = env_key or file_config.get("api_key", "")
    if eff_url and eff_key:
        print(f"    api_url = {eff_url}")
        print(f"    api_key = {eff_key[:8]}...")
    else:
        print("    (not configured — run: python nca.py connect)")

    print("")


def cmd_test(args):
    """Test API connectivity."""
    result = api_request("/v1/toolkit/test", method="GET")
    print_result(result)


def cmd_status(args):
    """Check job status."""
    result = api_request("/v1/toolkit/job/status", {"job_id": args.job_id})
    print_result(result)


def cmd_transcribe(args):
    """Transcribe or translate media."""
    media_url = file_to_uri(args.file) if args.file else args.media_url
    payload = {"media_url": media_url}
    if args.task:
        payload["task"] = args.task
    if args.language:
        payload["language"] = args.language
    if args.srt:
        payload["include_srt"] = True
    if args.segments:
        payload["include_segments"] = True
    if args.word_timestamps:
        payload["word_timestamps"] = True
    if args.words_per_line:
        payload["words_per_line"] = args.words_per_line
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    result = api_request("/v1/media/transcribe", payload)
    print_result(result)


def cmd_convert(args):
    """Convert media between formats."""
    media_url = file_to_uri(args.file) if args.file else args.media_url
    payload = {
        "media_url": media_url,
        "format": args.format,
    }
    if args.video_codec:
        payload["video_codec"] = args.video_codec
    if args.audio_codec:
        payload["audio_codec"] = args.audio_codec
    if args.video_crf is not None:
        payload["video_crf"] = args.video_crf
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    result = api_request("/v1/media/convert", payload)
    print_result(result)


def cmd_convert_mp3(args):
    """Convert media to MP3."""
    media_url = file_to_uri(args.file) if args.file else args.media_url
    payload = {"media_url": media_url}
    if args.bitrate:
        payload["bitrate"] = args.bitrate
    if args.sample_rate:
        payload["sample_rate"] = args.sample_rate
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    result = api_request("/v1/media/convert/mp3", payload)
    print_result(result)


def cmd_caption(args):
    """Add captions to a video."""
    video_url = file_to_uri(args.file) if args.file else args.video_url
    payload = {"video_url": video_url}
    if args.language:
        payload["language"] = args.language

    settings = {}
    if args.font_size:
        settings["font_size"] = args.font_size
    if args.font_family:
        settings["font_family"] = args.font_family
    if args.word_color:
        settings["word_color"] = args.word_color
    if args.line_color:
        settings["line_color"] = args.line_color
    if args.outline_color:
        settings["outline_color"] = args.outline_color
    if args.style:
        settings["style"] = args.style
    if args.position:
        settings["position"] = args.position
    if args.all_caps:
        settings["all_caps"] = True
    if args.max_words_per_line:
        settings["max_words_per_line"] = args.max_words_per_line
    if settings:
        payload["settings"] = settings

    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    result = api_request("/v1/video/caption", payload)
    print_result(result)


def cmd_video_trim(args):
    """Trim a video."""
    video_url = file_to_uri(args.file) if args.file else args.video_url
    payload = {"video_url": video_url}
    if args.start:
        payload["start"] = args.start
    if args.end:
        payload["end"] = args.end
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    result = api_request("/v1/video/trim", payload)
    print_result(result)


def cmd_video_cut(args):
    """Cut segments from a video."""
    video_url = file_to_uri(args.file) if args.file else args.video_url
    cuts = []
    for cut_str in args.cuts:
        start, end = cut_str.split("-", 1)
        cuts.append({"start": start.strip(), "end": end.strip()})

    payload = {"video_url": video_url, "cuts": cuts}
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    result = api_request("/v1/video/cut", payload)
    print_result(result)


def cmd_video_split(args):
    """Split a video into segments."""
    video_url = file_to_uri(args.file) if args.file else args.video_url
    splits = []
    for split_str in args.splits:
        start, end = split_str.split("-", 1)
        splits.append({"start": start.strip(), "end": end.strip()})

    payload = {"video_url": video_url, "splits": splits}
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    result = api_request("/v1/video/split", payload)
    print_result(result)


def cmd_video_concat(args):
    """Concatenate multiple videos."""
    if args.files:
        video_urls = [{"video_url": file_to_uri(f)} for f in args.files]
    else:
        video_urls = [{"video_url": url} for url in args.video_urls]
    payload = {"video_urls": video_urls}
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    result = api_request("/v1/video/concatenate", payload)
    print_result(result)


def cmd_thumbnail(args):
    """Extract a thumbnail from a video."""
    video_url = file_to_uri(args.file) if args.file else args.video_url
    payload = {"video_url": video_url}
    if args.second is not None:
        payload["second"] = args.second
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    result = api_request("/v1/video/thumbnail", payload)
    print_result(result)


def cmd_screenshot(args):
    """Take a screenshot of a webpage."""
    payload = {}
    if args.url:
        payload["url"] = args.url
    if args.html:
        payload["html"] = args.html
    if args.viewport_width:
        payload["viewport_width"] = args.viewport_width
    if args.viewport_height:
        payload["viewport_height"] = args.viewport_height
    if args.full_page:
        payload["full_page"] = True
    if args.format:
        payload["format"] = args.format
    if args.delay:
        payload["delay"] = args.delay
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    result = api_request("/v1/image/screenshot/webpage", payload)
    print_result(result)


def cmd_metadata(args):
    """Get media file metadata."""
    media_url = file_to_uri(args.file) if args.file else args.media_url
    payload = {"media_url": media_url}
    result = api_request("/v1/media/metadata", payload)
    print_result(result)


def cmd_download(args):
    """Download media from a URL."""
    payload = {"media_url": args.media_url}
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    result = api_request("/v1/BETA/media/download", payload)
    print_result(result)


def cmd_silence(args):
    """Detect silence in media."""
    media_url = file_to_uri(args.file) if args.file else args.media_url
    payload = {
        "media_url": media_url,
        "duration": args.duration,
    }
    if args.noise:
        payload["noise"] = args.noise
    if args.start:
        payload["start"] = args.start
    if args.end:
        payload["end"] = args.end
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    result = api_request("/v1/media/silence", payload)
    print_result(result)


def cmd_ffmpeg(args):
    """Run custom FFmpeg commands."""
    payload = json.loads(args.payload)
    result = api_request("/v1/ffmpeg/compose", payload)
    print_result(result)


def cmd_upload_s3(args):
    """Upload a file to S3."""
    payload = {"file_url": args.file_url}
    if args.filename:
        payload["filename"] = args.filename
    if args.public:
        payload["public"] = True
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    result = api_request("/v1/s3/upload", payload)
    print_result(result)


def cmd_upload_gcp(args):
    """Upload a file to GCP Storage."""
    payload = {"file_url": args.file_url}
    if args.filename:
        payload["filename"] = args.filename
    if args.public:
        payload["public"] = True
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    result = api_request("/v1/gcp/upload", payload)
    print_result(result)


# ─── Argument Parser ──────────────────────────────────────────────────────────


def build_parser():
    parser = argparse.ArgumentParser(
        prog="nca",
        description="NCA Toolkit CLI - interact with your NCA Toolkit API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration (checked in order):
  1. Environment variables: NCA_API_URL, NCA_API_KEY
  2. Config file: ~/.nca-toolkit/config

Getting started:
  python nca.py connect             Connect CLI to a running API
  python nca.py config              Show current configuration
  python nca.py test                Test API connectivity

Examples:
  python nca.py transcribe --media-url https://example.com/audio.mp3
  python nca.py transcribe --file ./local/input/audio.mp3
  python nca.py convert --media-url https://example.com/video.mp4 --format webm
  python nca.py convert --file ./local/input/video.mp4 --format webm
  python nca.py caption --video-url https://example.com/video.mp4 --style karaoke
  python nca.py screenshot --url https://example.com --full-page

Local file I/O (use with 'make up-local'):
  1. Place files in ./local/input/
  2. Use --file instead of --media-url or --video-url
  3. Output files appear in ./local/output/
""",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # setup
    p = sub.add_parser("connect", help="Connect CLI to a running API instance")
    p.add_argument("--profile", default="default", help="Config profile name (default: default)")

    # config
    sub.add_parser("config", help="Show current configuration")

    # test
    sub.add_parser("test", help="Test API connectivity")

    # status
    p = sub.add_parser("status", help="Check job status")
    p.add_argument("job_id", help="Job ID to check")

    # transcribe
    p = sub.add_parser("transcribe", help="Transcribe or translate media")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--media-url", help="URL of media to transcribe")
    g.add_argument("--file", "-f", help="Local file path (must be in ./local/input/)")
    p.add_argument("--task", choices=["transcribe", "translate"], help="Task type")
    p.add_argument("--language", help="Source language code")
    p.add_argument("--srt", action="store_true", help="Include SRT output")
    p.add_argument("--segments", action="store_true", help="Include segments")
    p.add_argument("--word-timestamps", action="store_true", help="Include word timestamps")
    p.add_argument("--words-per-line", type=int, help="Words per line in SRT")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # convert
    p = sub.add_parser("convert", help="Convert media between formats")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--media-url", help="URL of media to convert")
    g.add_argument("--file", "-f", help="Local file path (must be in ./local/input/)")
    p.add_argument("--format", required=True, help="Target format (e.g., mp4, webm, avi)")
    p.add_argument("--video-codec", help="Video codec (default: libx264)")
    p.add_argument("--audio-codec", help="Audio codec (default: aac)")
    p.add_argument("--video-crf", type=float, help="Video CRF quality (0-51)")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # convert-mp3
    p = sub.add_parser("convert-mp3", help="Convert media to MP3")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--media-url", help="URL of media to convert")
    g.add_argument("--file", "-f", help="Local file path (must be in ./local/input/)")
    p.add_argument("--bitrate", help="Audio bitrate (e.g., 128k, 320k)")
    p.add_argument("--sample-rate", type=float, help="Sample rate")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # caption
    p = sub.add_parser("caption", help="Add captions to a video")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--video-url", help="URL of video to caption")
    g.add_argument("--file", "-f", help="Local file path (must be in ./local/input/)")
    p.add_argument("--language", help="Language code (default: auto)")
    p.add_argument("--style", choices=["classic", "karaoke", "highlight", "underline", "word_by_word"], help="Caption style")
    p.add_argument("--position", choices=["bottom_left", "bottom_center", "bottom_right", "middle_left", "middle_center", "middle_right", "top_left", "top_center", "top_right"], help="Caption position")
    p.add_argument("--font-size", type=int, help="Font size")
    p.add_argument("--font-family", help="Font family")
    p.add_argument("--word-color", help="Active word color")
    p.add_argument("--line-color", help="Line text color")
    p.add_argument("--outline-color", help="Outline color")
    p.add_argument("--all-caps", action="store_true", help="Use all caps")
    p.add_argument("--max-words-per-line", type=int, help="Max words per line")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # video-trim
    p = sub.add_parser("video-trim", help="Trim a video")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--video-url", help="URL of video to trim")
    g.add_argument("--file", "-f", help="Local file path (must be in ./local/input/)")
    p.add_argument("--start", help="Start time (e.g., 00:00:10)")
    p.add_argument("--end", help="End time (e.g., 00:01:30)")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # video-cut
    p = sub.add_parser("video-cut", help="Cut segments from a video")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--video-url", help="URL of video")
    g.add_argument("--file", "-f", help="Local file path (must be in ./local/input/)")
    p.add_argument("--cuts", nargs="+", required=True, help="Cut ranges (e.g., 00:00:10-00:00:20)")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # video-split
    p = sub.add_parser("video-split", help="Split a video into segments")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--video-url", help="URL of video")
    g.add_argument("--file", "-f", help="Local file path (must be in ./local/input/)")
    p.add_argument("--splits", nargs="+", required=True, help="Split ranges (e.g., 00:00:00-00:01:00)")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # video-concat
    p = sub.add_parser("video-concat", help="Concatenate multiple videos")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--video-urls", nargs="+", help="URLs of videos to concatenate")
    g.add_argument("--files", nargs="+", help="Local file paths (must be in ./local/input/)")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # thumbnail
    p = sub.add_parser("thumbnail", help="Extract a thumbnail from a video")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--video-url", help="URL of video")
    g.add_argument("--file", "-f", help="Local file path (must be in ./local/input/)")
    p.add_argument("--second", type=float, help="Timestamp in seconds (default: 0)")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # screenshot
    p = sub.add_parser("screenshot", help="Take a screenshot of a webpage")
    p.add_argument("--url", help="URL to screenshot")
    p.add_argument("--html", help="HTML content to render")
    p.add_argument("--viewport-width", type=int, help="Viewport width")
    p.add_argument("--viewport-height", type=int, help="Viewport height")
    p.add_argument("--full-page", action="store_true", help="Capture full page")
    p.add_argument("--format", choices=["png", "jpeg"], help="Image format")
    p.add_argument("--delay", type=int, help="Delay in ms before capture")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # metadata
    p = sub.add_parser("metadata", help="Get media file metadata")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--media-url", help="URL of media file")
    g.add_argument("--file", "-f", help="Local file path (must be in ./local/input/)")

    # download
    p = sub.add_parser("download", help="Download media from a URL")
    p.add_argument("--media-url", required=True, help="URL to download from")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # silence
    p = sub.add_parser("silence", help="Detect silence in media")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--media-url", help="URL of media file")
    g.add_argument("--file", "-f", help="Local file path (must be in ./local/input/)")
    p.add_argument("--duration", type=float, required=True, help="Min silence duration (seconds)")
    p.add_argument("--noise", help="Noise threshold (default: -30dB)")
    p.add_argument("--start", help="Start time")
    p.add_argument("--end", help="End time")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # ffmpeg
    p = sub.add_parser("ffmpeg", help="Run custom FFmpeg compose commands")
    p.add_argument("--payload", required=True, help="JSON payload for FFmpeg compose")

    # upload-s3
    p = sub.add_parser("upload-s3", help="Upload a file to S3")
    p.add_argument("--file-url", required=True, help="URL of file to upload")
    p.add_argument("--filename", help="Target filename")
    p.add_argument("--public", action="store_true", help="Make file public")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # upload-gcp
    p = sub.add_parser("upload-gcp", help="Upload a file to GCP Storage")
    p.add_argument("--file-url", required=True, help="URL of file to upload")
    p.add_argument("--filename", help="Target filename")
    p.add_argument("--public", action="store_true", help="Make file public")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    return parser


COMMANDS = {
    "connect": cmd_connect,
    "config": cmd_config,
    "test": cmd_test,
    "status": cmd_status,
    "transcribe": cmd_transcribe,
    "convert": cmd_convert,
    "convert-mp3": cmd_convert_mp3,
    "caption": cmd_caption,
    "video-trim": cmd_video_trim,
    "video-cut": cmd_video_cut,
    "video-split": cmd_video_split,
    "video-concat": cmd_video_concat,
    "thumbnail": cmd_thumbnail,
    "screenshot": cmd_screenshot,
    "metadata": cmd_metadata,
    "download": cmd_download,
    "silence": cmd_silence,
    "ffmpeg": cmd_ffmpeg,
    "upload-s3": cmd_upload_s3,
    "upload-gcp": cmd_upload_gcp,
}


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    handler = COMMANDS.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
