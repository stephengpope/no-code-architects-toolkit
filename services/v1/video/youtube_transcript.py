from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
from youtube_transcript_api.formatters import TextFormatter, SRTFormatter

def fetch_youtube_transcript(video_id, languages=None, format="json"):
    try:
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
            return {"transcript": fetched_transcript}
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as e:
        return {"error": str(e)}
    except TypeError as e:
        return {"error": f"TypeError: {e}"}
    except Exception as e:
        return {"error": str(e)} 