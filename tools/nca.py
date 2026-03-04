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
import shutil
import stat
import sys
import time
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


def is_local_api():
    """Check if the configured API is running locally."""
    url, _ = get_config()
    from urllib.parse import urlparse as _urlparse
    host = _urlparse(url).hostname or ""
    return host in ("localhost", "127.0.0.1", "0.0.0.0", "::1")


def upload_file_to_api(local_path):
    """Upload a local file to the API via multipart POST, return the cloud URL."""
    url, key = get_config()
    full_url = f"{url}/v1/files/upload"

    if not os.path.isfile(local_path):
        print(f"Error: File not found: {local_path}", file=sys.stderr)
        sys.exit(1)

    filename = os.path.basename(local_path)
    boundary = f"----NCABoundary{os.urandom(8).hex()}"

    # Build multipart body manually (zero dependencies)
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode())
    body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
    with open(local_path, "rb") as f:
        body.extend(f.read())
    body.extend(f"\r\n--{boundary}--\r\n".encode())

    headers = {
        "X-API-Key": key,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }

    req = urllib.request.Request(full_url, data=bytes(body), headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            result = json.loads(resp.read().decode())
            cloud_url = result.get("url", "")
            print(f"  Uploaded {filename} -> {cloud_url}", file=sys.stderr)
            return cloud_url
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Upload failed (HTTP {e.code}): {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Upload failed: {e.reason}", file=sys.stderr)
        sys.exit(1)


def resolve_file(local_path):
    """Upload local file to API, return the storage URL."""
    return upload_file_to_api(local_path)


def resolve_files(local_paths):
    """Resolve multiple --files arguments."""
    return [resolve_file(p) for p in local_paths]


# Dummy webhook URL that triggers async mode without needing a real webhook server.
# The API will try to POST to this and fail silently — that's fine, we poll instead.
NOOP_WEBHOOK = "http://localhost:1/noop"


def apply_background(payload, args):
    """If --bg is set, inject a dummy webhook_url to trigger async processing."""
    if getattr(args, "background", False):
        payload["webhook_url"] = NOOP_WEBHOOK
    return payload


# ─── Output Handling ─────────────────────────────────────────────────────────

# Commands that return text/data (not file URLs)
TEXT_COMMANDS = {"transcribe", "metadata", "silence", "status", "test", "config"}

# Commands that return file URLs to download
FILE_COMMANDS = {
    "convert", "convert-mp3", "caption", "video-trim", "video-cut",
    "video-split", "video-concat", "thumbnail", "screenshot",
    "download", "ffmpeg", "upload-s3", "upload-gcp",
}


def download_output(url, output_dir="."):
    """Download an output file from the API to local disk.

    Handles HTTP/HTTPS URLs (download) and file:// URLs (copy from ./local/output/).
    Returns the local file path, or None on failure.
    """
    from urllib.parse import urlparse
    parsed = urlparse(url)

    filename = os.path.basename(parsed.path)
    if not filename:
        filename = "output"

    dest_path = os.path.join(output_dir, filename)

    if parsed.scheme == "file":
        # file:// URI from local Docker API — translate to host path
        container_path = parsed.path  # e.g., /data/output/foo.mp4
        if container_path.startswith("/data/output/"):
            local_path = os.path.join(".", "local", "output", container_path[len("/data/output/"):])
        else:
            local_path = container_path

        if os.path.isfile(local_path):
            os.makedirs(output_dir, exist_ok=True)
            shutil.copy2(local_path, dest_path)
        else:
            print(f"Warning: Local file not found: {local_path}", file=sys.stderr)
            return None
    else:
        # HTTP/HTTPS download
        os.makedirs(output_dir, exist_ok=True)
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                with open(dest_path, "wb") as f:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            print(f"Warning: Failed to download {url}: {e}", file=sys.stderr)
            return None

    return dest_path


def extract_urls(obj):
    """Extract all URLs (http://, https://, file://) from a response object."""
    results = []

    def _walk(item, path=""):
        if isinstance(item, str):
            if item.startswith(("http://", "https://", "file://")):
                results.append((path, item))
        elif isinstance(item, dict):
            for k, v in item.items():
                _walk(v, f"{path}.{k}" if path else k)
        elif isinstance(item, list):
            for i, v in enumerate(item):
                _walk(v, f"{path}[{i}]")

    _walk(obj)
    return results


def handle_output(result, command, output_dir=".", json_mode=False, background=False):
    """Process API result: download files, print text or file paths.

    Args:
        result: Full API response dict (with "response" key)
        command: The CLI command name (e.g., "transcribe", "convert")
        output_dir: Directory to save downloaded files
        json_mode: If True, print full JSON and skip downloads
        background: If True, just print job_id for async tracking
    """
    if json_mode:
        print(json.dumps(result, indent=2))
        return

    response = result.get("response")
    code = result.get("code", 200)

    # 202 accepted (webhook/async mode) — print job_id to stdout for capture
    if code == 202:
        job_id = result.get("job_id", "unknown")
        if background:
            # Print just the job_id to stdout so it can be captured
            print(job_id)
            print(f"  Job submitted. Check status: python3 tools/nca.py status {job_id}", file=sys.stderr)
            print(f"  Wait for result:  python3 tools/nca.py wait {job_id}", file=sys.stderr)
        else:
            print(f"Job submitted: {job_id}", file=sys.stderr)
            print(f"Status: processing", file=sys.stderr)
        return

    # Error responses
    if code != 200 or response is None:
        message = result.get("message", "Unknown error")
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)

    # Text commands: print content directly
    if command in TEXT_COMMANDS:
        if command == "transcribe":
            if isinstance(response, dict):
                text = response.get("text")
                if text:
                    print(text)
                srt = response.get("srt")
                if srt:
                    print("\n--- SRT ---\n")
                    print(srt)
                segments = response.get("segments")
                if segments:
                    print("\n--- Segments ---\n")
                    print(json.dumps(segments, indent=2))
            else:
                print(response)
        else:
            # metadata, silence, status, test: print as formatted JSON
            print(json.dumps(response, indent=2))
        return

    # File commands: find URLs, download them, print local paths
    if isinstance(response, str) and response.startswith(("http://", "https://", "file://")):
        # Single URL response (convert, caption, trim, etc.)
        local_path = download_output(response, output_dir)
        if local_path:
            print(local_path)
        else:
            print(response)  # Fallback: print the URL
        return

    # Complex response with embedded URLs (split, download, ffmpeg, etc.)
    urls = extract_urls(response)
    if urls:
        for _key_path, url in urls:
            local_path = download_output(url, output_dir)
            if local_path:
                print(local_path)
            else:
                print(url)
        return

    # No URLs found: just print the response as JSON
    print(json.dumps(response, indent=2))


def poll_job(job_id, interval=5, timeout=600):
    """Poll job status until complete. Returns the final result dict.

    The job status file contains:
      {"job_status": "queued|running|done|failed", "response": {...}}
    The /v1/toolkit/job/status endpoint wraps that in the standard envelope:
      {"code": 200, "response": {"job_status": "...", "response": {...}}}
    """
    elapsed = 0
    while elapsed < timeout:
        result = api_request("/v1/toolkit/job/status", {"job_id": job_id})
        # The actual job data is inside result["response"]
        job_data = result.get("response", {})
        if isinstance(job_data, dict):
            job_status = job_data.get("job_status", "unknown")
        else:
            job_status = "unknown"

        if job_status == "done":
            # The completed response is nested inside job_data["response"]
            completed_response = job_data.get("response")
            if completed_response and isinstance(completed_response, dict):
                return completed_response
            return result

        if job_status == "failed":
            print(f"Error: Job {job_id} failed", file=sys.stderr)
            sys.exit(1)

        print(f"  Status: {job_status} ({elapsed}s elapsed)", file=sys.stderr)
        time.sleep(interval)
        elapsed += interval

    print(f"Error: Job timed out after {timeout}s", file=sys.stderr)
    sys.exit(1)


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
    handle_output(result, "test", getattr(args, "output_dir", "."), getattr(args, "json_output", False))


def cmd_status(args):
    """Check job status."""
    result = api_request("/v1/toolkit/job/status", {"job_id": args.job_id})
    if args.json_output:
        print(json.dumps(result, indent=2))
        return
    # Show a clean status summary
    job_data = result.get("response", {})
    if isinstance(job_data, dict):
        status = job_data.get("job_status", "unknown")
        print(status)
    else:
        print(json.dumps(result, indent=2))


def cmd_wait(args):
    """Wait for a background job to complete, then show/download results."""
    # Determine the command type from the job response to handle output correctly
    command = getattr(args, "command_type", None) or "unknown"
    interval = getattr(args, "interval", 5)

    print(f"  Waiting for job {args.job_id}...", file=sys.stderr)
    result = poll_job(args.job_id, interval=interval)

    # Try to detect the command type from the endpoint in the response
    endpoint = result.get("endpoint", "")
    if "transcribe" in endpoint:
        command = "transcribe"
    elif "metadata" in endpoint:
        command = "metadata"
    elif "silence" in endpoint:
        command = "silence"
    elif any(x in endpoint for x in ["convert", "caption", "trim", "cut", "split",
                                       "concatenate", "thumbnail", "screenshot",
                                       "ffmpeg", "download"]):
        command = endpoint.split("/")[-1]  # Use last path segment

    handle_output(result, command, args.output_dir, args.json_output)


def cmd_transcribe(args):
    """Transcribe or translate media."""
    media_url = resolve_file(args.file) if args.file else args.media_url
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
    apply_background(payload, args)

    result = api_request("/v1/media/transcribe", payload)

    # Write transcription to file if --output-file was given
    output_file = getattr(args, "output_file", None)
    if output_file:
        path = os.path.expanduser(output_file)
        with open(path, "w") as f:
            if args.json_output:
                json.dump(result, f, indent=2)
            else:
                response = result.get("response", {})
                text = response.get("text", "") if isinstance(response, dict) else str(response)
                f.write(text)
                srt = response.get("srt") if isinstance(response, dict) else None
                if srt:
                    f.write("\n\n--- SRT ---\n\n")
                    f.write(srt)
        print(path)
        return

    handle_output(result, "transcribe", args.output_dir, args.json_output, args.background)


def cmd_convert(args):
    """Convert media between formats."""
    media_url = resolve_file(args.file) if args.file else args.media_url
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
    apply_background(payload, args)

    result = api_request("/v1/media/convert", payload)
    handle_output(result, "convert", args.output_dir, args.json_output, args.background)


def cmd_convert_mp3(args):
    """Convert media to MP3."""
    media_url = resolve_file(args.file) if args.file else args.media_url
    payload = {"media_url": media_url}
    if args.bitrate:
        payload["bitrate"] = args.bitrate
    if args.sample_rate:
        payload["sample_rate"] = args.sample_rate
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    apply_background(payload, args)

    result = api_request("/v1/media/convert/mp3", payload)
    handle_output(result, "convert-mp3", args.output_dir, args.json_output, args.background)


def cmd_caption(args):
    """Add captions to a video."""
    video_url = resolve_file(args.file) if args.file else args.video_url
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

    apply_background(payload, args)

    result = api_request("/v1/video/caption", payload)
    handle_output(result, "caption", args.output_dir, args.json_output, args.background)


def cmd_video_trim(args):
    """Trim a video."""
    video_url = resolve_file(args.file) if args.file else args.video_url
    payload = {"video_url": video_url}
    if args.start:
        payload["start"] = args.start
    if args.end:
        payload["end"] = args.end
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    apply_background(payload, args)

    result = api_request("/v1/video/trim", payload)
    handle_output(result, "video-trim", args.output_dir, args.json_output, args.background)


def cmd_video_cut(args):
    """Cut segments from a video."""
    video_url = resolve_file(args.file) if args.file else args.video_url
    cuts = []
    for cut_str in args.cuts:
        start, end = cut_str.split("-", 1)
        cuts.append({"start": start.strip(), "end": end.strip()})

    payload = {"video_url": video_url, "cuts": cuts}
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    apply_background(payload, args)

    result = api_request("/v1/video/cut", payload)
    handle_output(result, "video-cut", args.output_dir, args.json_output, args.background)


def cmd_video_split(args):
    """Split a video into segments."""
    video_url = resolve_file(args.file) if args.file else args.video_url
    splits = []
    for split_str in args.splits:
        start, end = split_str.split("-", 1)
        splits.append({"start": start.strip(), "end": end.strip()})

    payload = {"video_url": video_url, "splits": splits}
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    apply_background(payload, args)

    result = api_request("/v1/video/split", payload)
    handle_output(result, "video-split", args.output_dir, args.json_output, args.background)


def cmd_video_concat(args):
    """Concatenate multiple videos."""
    if args.files:
        video_urls = [{"video_url": u} for u in resolve_files(args.files)]
    else:
        video_urls = [{"video_url": url} for url in args.video_urls]
    payload = {"video_urls": video_urls}
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    apply_background(payload, args)

    result = api_request("/v1/video/concatenate", payload)
    handle_output(result, "video-concat", args.output_dir, args.json_output, args.background)


def cmd_thumbnail(args):
    """Extract a thumbnail from a video."""
    video_url = resolve_file(args.file) if args.file else args.video_url
    payload = {"video_url": video_url}
    if args.second is not None:
        payload["second"] = args.second
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    apply_background(payload, args)

    result = api_request("/v1/video/thumbnail", payload)
    handle_output(result, "thumbnail", args.output_dir, args.json_output, args.background)


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

    apply_background(payload, args)

    result = api_request("/v1/image/screenshot/webpage", payload)
    handle_output(result, "screenshot", args.output_dir, args.json_output, args.background)


def cmd_metadata(args):
    """Get media file metadata."""
    media_url = resolve_file(args.file) if args.file else args.media_url
    payload = {"media_url": media_url}
    apply_background(payload, args)
    result = api_request("/v1/media/metadata", payload)
    handle_output(result, "metadata", args.output_dir, args.json_output, args.background)


def cmd_download(args):
    """Download media from a URL."""
    payload = {"media_url": args.media_url}
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    apply_background(payload, args)
    result = api_request("/v1/BETA/media/download", payload)
    handle_output(result, "download", args.output_dir, args.json_output, args.background)


def cmd_silence(args):
    """Detect silence in media."""
    media_url = resolve_file(args.file) if args.file else args.media_url
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

    apply_background(payload, args)
    result = api_request("/v1/media/silence", payload)
    handle_output(result, "silence", args.output_dir, args.json_output, args.background)


def cmd_ffmpeg(args):
    """Run custom FFmpeg commands."""
    payload = json.loads(args.payload)
    apply_background(payload, args)
    result = api_request("/v1/ffmpeg/compose", payload)
    handle_output(result, "ffmpeg", args.output_dir, args.json_output, args.background)


def cmd_upload_s3(args):
    """Upload a file to S3."""
    payload = {"file_url": args.file_url}
    if args.filename:
        payload["filename"] = args.filename
    if args.public:
        payload["public"] = True
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    apply_background(payload, args)
    result = api_request("/v1/s3/upload", payload)
    handle_output(result, "upload-s3", args.output_dir, args.json_output, args.background)


def cmd_upload_gcp(args):
    """Upload a file to GCP Storage."""
    payload = {"file_url": args.file_url}
    if args.filename:
        payload["filename"] = args.filename
    if args.public:
        payload["public"] = True
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    apply_background(payload, args)
    result = api_request("/v1/gcp/upload", payload)
    handle_output(result, "upload-gcp", args.output_dir, args.json_output, args.background)


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
  python nca.py transcribe --file ~/recordings/meeting.mp3
  python nca.py convert --file ~/videos/clip.mp4 --format webm
  python nca.py convert --file ~/videos/clip.mp4 --format webm -o ~/Downloads
  python nca.py caption --video-url https://example.com/video.mp4 --style karaoke
  python nca.py screenshot --url https://example.com --full-page

Local files:
  Use --file with any path. Files are uploaded to the API automatically.
  Output files are downloaded to the current directory (use -o to change).
  Use --json for full JSON response instead of human-readable output.

Background mode:
  Use --bg to run long tasks without blocking. Returns a job ID immediately.
  python nca.py transcribe --file ~/audio.mp3 --bg     # Returns job ID
  python nca.py status <job_id>                          # Check if done
  python nca.py wait <job_id>                            # Block until done, show result
""",
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # Shared flags available on every subcommand (--json, -o, --bg)
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--json", dest="json_output", action="store_true",
                        help="Output full JSON response instead of human-readable text")
    shared.add_argument("--output-dir", "-o", default=".",
                        help="Directory for downloaded output files (default: current directory)")
    shared.add_argument("--bg", "--background", dest="background", action="store_true",
                        help="Run in background: submit job and return immediately with job ID")

    # setup
    p = sub.add_parser("connect", parents=[shared], help="Connect CLI to a running API instance")
    p.add_argument("--profile", default="default", help="Config profile name (default: default)")

    # config
    sub.add_parser("config", parents=[shared], help="Show current configuration")

    # test
    sub.add_parser("test", parents=[shared], help="Test API connectivity")

    # status
    p = sub.add_parser("status", parents=[shared], help="Check job status")
    p.add_argument("job_id", help="Job ID to check")

    # wait
    p = sub.add_parser("wait", parents=[shared], help="Wait for a background job to complete")
    p.add_argument("job_id", help="Job ID to wait for")
    p.add_argument("--interval", type=int, default=5, help="Poll interval in seconds (default: 5)")

    # transcribe
    p = sub.add_parser("transcribe", parents=[shared], help="Transcribe or translate media")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--media-url", help="URL of media to transcribe")
    g.add_argument("--file", "-f", help="Local file path (uploaded automatically)")
    p.add_argument("--task", choices=["transcribe", "translate"], help="Task type")
    p.add_argument("--language", help="Source language code")
    p.add_argument("--srt", action="store_true", help="Include SRT output")
    p.add_argument("--segments", action="store_true", help="Include segments")
    p.add_argument("--word-timestamps", action="store_true", help="Include word timestamps")
    p.add_argument("--words-per-line", type=int, help="Words per line in SRT")
    p.add_argument("--output-file", help="Write transcription text to this file")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # convert
    p = sub.add_parser("convert", parents=[shared], help="Convert media between formats")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--media-url", help="URL of media to convert")
    g.add_argument("--file", "-f", help="Local file path (uploaded automatically)")
    p.add_argument("--format", required=True, help="Target format (e.g., mp4, webm, avi)")
    p.add_argument("--video-codec", help="Video codec (default: libx264)")
    p.add_argument("--audio-codec", help="Audio codec (default: aac)")
    p.add_argument("--video-crf", type=float, help="Video CRF quality (0-51)")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # convert-mp3
    p = sub.add_parser("convert-mp3", parents=[shared], help="Convert media to MP3")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--media-url", help="URL of media to convert")
    g.add_argument("--file", "-f", help="Local file path (uploaded automatically)")
    p.add_argument("--bitrate", help="Audio bitrate (e.g., 128k, 320k)")
    p.add_argument("--sample-rate", type=float, help="Sample rate")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # caption
    p = sub.add_parser("caption", parents=[shared], help="Add captions to a video")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--video-url", help="URL of video to caption")
    g.add_argument("--file", "-f", help="Local file path (uploaded automatically)")
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
    p = sub.add_parser("video-trim", parents=[shared], help="Trim a video")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--video-url", help="URL of video to trim")
    g.add_argument("--file", "-f", help="Local file path (uploaded automatically)")
    p.add_argument("--start", help="Start time (e.g., 00:00:10)")
    p.add_argument("--end", help="End time (e.g., 00:01:30)")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # video-cut
    p = sub.add_parser("video-cut", parents=[shared], help="Cut segments from a video")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--video-url", help="URL of video")
    g.add_argument("--file", "-f", help="Local file path (uploaded automatically)")
    p.add_argument("--cuts", nargs="+", required=True, help="Cut ranges (e.g., 00:00:10-00:00:20)")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # video-split
    p = sub.add_parser("video-split", parents=[shared], help="Split a video into segments")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--video-url", help="URL of video")
    g.add_argument("--file", "-f", help="Local file path (uploaded automatically)")
    p.add_argument("--splits", nargs="+", required=True, help="Split ranges (e.g., 00:00:00-00:01:00)")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # video-concat
    p = sub.add_parser("video-concat", parents=[shared], help="Concatenate multiple videos")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--video-urls", nargs="+", help="URLs of videos to concatenate")
    g.add_argument("--files", nargs="+", help="Local file paths (uploaded automatically)")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # thumbnail
    p = sub.add_parser("thumbnail", parents=[shared], help="Extract a thumbnail from a video")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--video-url", help="URL of video")
    g.add_argument("--file", "-f", help="Local file path (uploaded automatically)")
    p.add_argument("--second", type=float, help="Timestamp in seconds (default: 0)")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # screenshot
    p = sub.add_parser("screenshot", parents=[shared], help="Take a screenshot of a webpage")
    p.add_argument("--url", help="URL to screenshot")
    p.add_argument("--html", help="HTML content to render")
    p.add_argument("--viewport-width", type=int, help="Viewport width")
    p.add_argument("--viewport-height", type=int, help="Viewport height")
    p.add_argument("--full-page", action="store_true", help="Capture full page")
    p.add_argument("--format", choices=["png", "jpeg"], help="Image format")
    p.add_argument("--delay", type=int, help="Delay in ms before capture")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # metadata
    p = sub.add_parser("metadata", parents=[shared], help="Get media file metadata")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--media-url", help="URL of media file")
    g.add_argument("--file", "-f", help="Local file path (uploaded automatically)")

    # download
    p = sub.add_parser("download", parents=[shared], help="Download media from a URL")
    p.add_argument("--media-url", required=True, help="URL to download from")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # silence
    p = sub.add_parser("silence", parents=[shared], help="Detect silence in media")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--media-url", help="URL of media file")
    g.add_argument("--file", "-f", help="Local file path (uploaded automatically)")
    p.add_argument("--duration", type=float, required=True, help="Min silence duration (seconds)")
    p.add_argument("--noise", help="Noise threshold (default: -30dB)")
    p.add_argument("--start", help="Start time")
    p.add_argument("--end", help="End time")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # ffmpeg
    p = sub.add_parser("ffmpeg", parents=[shared], help="Run custom FFmpeg compose commands")
    p.add_argument("--payload", required=True, help="JSON payload for FFmpeg compose")

    # upload-s3
    p = sub.add_parser("upload-s3", parents=[shared], help="Upload a file to S3")
    p.add_argument("--file-url", required=True, help="URL of file to upload")
    p.add_argument("--filename", help="Target filename")
    p.add_argument("--public", action="store_true", help="Make file public")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # upload-gcp
    p = sub.add_parser("upload-gcp", parents=[shared], help="Upload a file to GCP Storage")
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
    "wait": cmd_wait,
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
