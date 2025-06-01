from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
from youtube_transcript_api.formatters import TextFormatter, SRTFormatter
import re

def extract_video_id(video_url):
    """
    Extract video ID from YouTube URL.
    Supports various YouTube URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    """
    # Regular expression patterns for different YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, video_url)
        if match:
            return match.group(1)
    
    # If no pattern matches, assume it's already a video ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', video_url):
        return video_url
    
    raise ValueError(f"Could not extract video ID from URL: {video_url}")

def fetch_youtube_transcript(video_url, languages=None, format="json"):
    try:
        # Extract video ID from URL
        video_id = extract_video_id(video_url)
        
        transcript_obj = YouTubeTranscriptApi.list_transcripts(video_id).find_transcript(languages or ['en'])
        fetched_transcript = transcript_obj.fetch()
        if fetched_transcript is None:
            return {"error": "No transcript available for this video."}

        if format == "plain":
            text = TextFormatter().format_transcript(fetched_transcript)
            return {"transcript": text}
        elif format == "srt":
            try:
                srt = SRTFormatter().format_transcript(fetched_transcript)
                return {"transcript": srt}
            except Exception as e:
                return {"error": f"SRT formatting error: {e}"}
        else:  # default to JSON
            # Convert to a basic list like the formatters do
            transcript_list = []
            for entry in fetched_transcript:
                transcript_list.append({
                    'text': entry.text,
                    'start': entry.start, 
                    'duration': entry.duration
                })
            return {"transcript": transcript_list}
    except ValueError as e:
        return {"error": str(e)}
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as e:
        return {"error": str(e)}
    except TypeError as e:
        return {"error": f"TypeError: {e}"}
    except Exception as e:
        return {"error": str(e)} 