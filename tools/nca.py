#!/usr/bin/env python3
"""
NCA Toolkit CLI - Command-line client for the No-Code Architects Toolkit API.

Configuration:
  Set these environment variables:
    NCA_API_URL   - Base URL of your NCA Toolkit instance (e.g., https://nca.example.com)
    NCA_API_KEY   - Your API key for authentication

Usage:
  python nca.py <command> [options]

Commands:
  transcribe     Transcribe or translate audio/video
  convert        Convert media between formats
  convert-mp3    Convert media to MP3
  caption        Add captions to a video
  video-trim     Trim a video to start/end times
  video-cut      Cut segments from a video
  video-split    Split a video into segments
  video-concat   Concatenate multiple videos
  thumbnail      Extract a thumbnail from a video
  screenshot     Take a screenshot of a webpage
  metadata       Get media file metadata
  download       Download media from a URL
  silence        Detect silence in media
  ffmpeg         Run custom FFmpeg commands
  upload-s3      Upload a file to S3
  upload-gcp     Upload a file to GCP Storage
  status         Check job status
  test           Test API connectivity
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def get_config():
    """Load API configuration from environment variables."""
    url = os.environ.get("NCA_API_URL", "").rstrip("/")
    key = os.environ.get("NCA_API_KEY", "")

    if not url:
        print("Error: NCA_API_URL environment variable is not set.", file=sys.stderr)
        print("  export NCA_API_URL=https://your-nca-instance.run.app", file=sys.stderr)
        sys.exit(1)
    if not key:
        print("Error: NCA_API_KEY environment variable is not set.", file=sys.stderr)
        print("  export NCA_API_KEY=your_api_key", file=sys.stderr)
        sys.exit(1)

    return url, key


def api_request(endpoint, payload=None, method="POST"):
    """Make an authenticated request to the NCA Toolkit API."""
    url, key = get_config()
    full_url = f"{url}{endpoint}"

    headers = {
        "X-API-Key": key,
        "Content-Type": "application/json",
    }

    data = json.dumps(payload).encode() if payload else None
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


def print_result(result):
    """Print API result as formatted JSON."""
    print(json.dumps(result, indent=2))


# ─── Command Handlers ─────────────────────────────────────────────────────────


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
    payload = {"media_url": args.media_url}
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
    payload = {
        "media_url": args.media_url,
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
    payload = {"media_url": args.media_url}
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
    payload = {"video_url": args.video_url}
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
    payload = {"video_url": args.video_url}
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
    cuts = []
    for cut_str in args.cuts:
        start, end = cut_str.split("-", 1)
        cuts.append({"start": start.strip(), "end": end.strip()})

    payload = {"video_url": args.video_url, "cuts": cuts}
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    result = api_request("/v1/video/cut", payload)
    print_result(result)


def cmd_video_split(args):
    """Split a video into segments."""
    splits = []
    for split_str in args.splits:
        start, end = split_str.split("-", 1)
        splits.append({"start": start.strip(), "end": end.strip()})

    payload = {"video_url": args.video_url, "splits": splits}
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    result = api_request("/v1/video/split", payload)
    print_result(result)


def cmd_video_concat(args):
    """Concatenate multiple videos."""
    video_urls = [{"video_url": url} for url in args.video_urls]
    payload = {"video_urls": video_urls}
    if args.webhook_url:
        payload["webhook_url"] = args.webhook_url

    result = api_request("/v1/video/concatenate", payload)
    print_result(result)


def cmd_thumbnail(args):
    """Extract a thumbnail from a video."""
    payload = {"video_url": args.video_url}
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
    payload = {"media_url": args.media_url}
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
    payload = {
        "media_url": args.media_url,
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
Environment variables:
  NCA_API_URL   Base URL of your NCA Toolkit (e.g., https://nca.example.com)
  NCA_API_KEY   Your API authentication key

Examples:
  python nca.py test
  python nca.py transcribe --media-url https://example.com/audio.mp3
  python nca.py convert --media-url https://example.com/video.mp4 --format webm
  python nca.py caption --video-url https://example.com/video.mp4 --style karaoke
  python nca.py screenshot --url https://example.com --full-page
""",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # test
    sub.add_parser("test", help="Test API connectivity")

    # status
    p = sub.add_parser("status", help="Check job status")
    p.add_argument("job_id", help="Job ID to check")

    # transcribe
    p = sub.add_parser("transcribe", help="Transcribe or translate media")
    p.add_argument("--media-url", required=True, help="URL of media to transcribe")
    p.add_argument("--task", choices=["transcribe", "translate"], help="Task type")
    p.add_argument("--language", help="Source language code")
    p.add_argument("--srt", action="store_true", help="Include SRT output")
    p.add_argument("--segments", action="store_true", help="Include segments")
    p.add_argument("--word-timestamps", action="store_true", help="Include word timestamps")
    p.add_argument("--words-per-line", type=int, help="Words per line in SRT")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # convert
    p = sub.add_parser("convert", help="Convert media between formats")
    p.add_argument("--media-url", required=True, help="URL of media to convert")
    p.add_argument("--format", required=True, help="Target format (e.g., mp4, webm, avi)")
    p.add_argument("--video-codec", help="Video codec (default: libx264)")
    p.add_argument("--audio-codec", help="Audio codec (default: aac)")
    p.add_argument("--video-crf", type=float, help="Video CRF quality (0-51)")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # convert-mp3
    p = sub.add_parser("convert-mp3", help="Convert media to MP3")
    p.add_argument("--media-url", required=True, help="URL of media to convert")
    p.add_argument("--bitrate", help="Audio bitrate (e.g., 128k, 320k)")
    p.add_argument("--sample-rate", type=float, help="Sample rate")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # caption
    p = sub.add_parser("caption", help="Add captions to a video")
    p.add_argument("--video-url", required=True, help="URL of video to caption")
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
    p.add_argument("--video-url", required=True, help="URL of video to trim")
    p.add_argument("--start", help="Start time (e.g., 00:00:10)")
    p.add_argument("--end", help="End time (e.g., 00:01:30)")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # video-cut
    p = sub.add_parser("video-cut", help="Cut segments from a video")
    p.add_argument("--video-url", required=True, help="URL of video")
    p.add_argument("--cuts", nargs="+", required=True, help="Cut ranges (e.g., 00:00:10-00:00:20)")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # video-split
    p = sub.add_parser("video-split", help="Split a video into segments")
    p.add_argument("--video-url", required=True, help="URL of video")
    p.add_argument("--splits", nargs="+", required=True, help="Split ranges (e.g., 00:00:00-00:01:00)")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # video-concat
    p = sub.add_parser("video-concat", help="Concatenate multiple videos")
    p.add_argument("--video-urls", nargs="+", required=True, help="URLs of videos to concatenate")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # thumbnail
    p = sub.add_parser("thumbnail", help="Extract a thumbnail from a video")
    p.add_argument("--video-url", required=True, help="URL of video")
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
    p.add_argument("--media-url", required=True, help="URL of media file")

    # download
    p = sub.add_parser("download", help="Download media from a URL")
    p.add_argument("--media-url", required=True, help="URL to download from")
    p.add_argument("--webhook-url", help="Webhook URL for async processing")

    # silence
    p = sub.add_parser("silence", help="Detect silence in media")
    p.add_argument("--media-url", required=True, help="URL of media file")
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
