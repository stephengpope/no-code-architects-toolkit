from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
from youtube_transcript_api.formatters import TextFormatter, SRTFormatter
import re
import os
import tempfile
import json
from config import LOCAL_STORAGE_PATH
from services.cloud_storage import upload_file

def extract_video_id(youtube_url):
    """
    Extract video ID from YouTube URL.
    Supports various YouTube URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID (YouTube Shorts)
    """
    # Regular expression patterns for different YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    # If no pattern matches, assume it's already a video ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', youtube_url):
        return youtube_url
    
    raise ValueError(f"Could not extract video ID from URL: {youtube_url}")

def fetch_youtube_transcript(youtube_url, languages=None, format="json", response_type="direct", job_id=None):
    try:
        # Extract video ID from URL
        video_id = extract_video_id(youtube_url)
        
        transcript_obj = YouTubeTranscriptApi.list_transcripts(video_id).find_transcript(languages or ['en'])
        fetched_transcript = transcript_obj.fetch()
        if fetched_transcript is None:
            return {"error": "No transcript available for this video."}

        if format == "plain":
            text = TextFormatter().format_transcript(fetched_transcript)
            transcript_data = {"transcript": text}
        elif format == "srt":
            try:
                srt = SRTFormatter().format_transcript(fetched_transcript)
                transcript_data = {"transcript": srt}
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
            transcript_data = {"transcript": transcript_list}
        
        # Handle response type
        if response_type == "cloud":
            # Define file extensions for different formats
            format_extensions = {
                "json": ".json",
                "plain": ".txt",
                "srt": ".srt"
            }
            file_extension = format_extensions.get(format, ".json")  # Default to .json if format is unknown

            # Create a temporary file and upload it to cloud storage
            temp_file_path = os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_transcript{file_extension}")
            
            try:
                # Write transcript data to temporary file
                with open(temp_file_path, 'w', encoding='utf-8') as f:
                    if format == "json":
                        json.dump(transcript_data["transcript"], f, ensure_ascii=False, indent=2)
                    elif format == "plain":
                        f.write(transcript_data["transcript"])
                    elif format == "srt":
                        f.write(transcript_data["transcript"])
                    else: # Should not happen given the format validation, but good to have a fallback
                        json.dump(transcript_data, f, ensure_ascii=False, indent=2)
                
                # Upload to cloud storage
                cloud_url = upload_file(temp_file_path)
                
                # Clean up temporary file
                os.remove(temp_file_path)
                
                return {
                    "transcript_url": cloud_url,
                    "response_type": "cloud"
                }
            except Exception as e:
                # Clean up on error
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                return {"error": f"Cloud storage upload failed: {e}"}
        else:
            # Direct response (default behavior)
            transcript_data["response_type"] = "direct"
            return transcript_data
            
    except ValueError as e:
        return {"error": str(e)}
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as e:
        return {"error": str(e)}
    except TypeError as e:
        return {"error": f"TypeError: {e}"}
    except Exception as e:
        return {"error": str(e)} 