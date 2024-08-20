import os
import whisper
import srt
from datetime import timedelta
from services.file_management import download_file, STORAGE_PATH

def process_transcription(media_url, output_type):
    """Transcribe media and return the transcript or SRT file."""
    input_filename = download_file(media_url, os.path.join(STORAGE_PATH, 'input_media'))

    try:
        model = whisper.load_model("base")
        result = model.transcribe(input_filename)

        if output_type == 'transcript':
            output = result['text']
        elif output_type == 'srt':
            srt_subtitles = []
            for i, segment in enumerate(result['segments'], start=1):
                start = timedelta(seconds=segment['start'])
                end = timedelta(seconds=segment['end'])
                text = segment['text'].strip()
                srt_subtitles.append(srt.Subtitle(i, start, end, text))
            output = srt.compose(srt_subtitles)
        else:
            raise ValueError("Invalid output type. Must be 'transcript' or 'srt'.")

        os.remove(input_filename)
        print(f"Transcription successful, output type: {output_type}")
        return output
    except Exception as e:
        print(f"Transcription failed: {str(e)}")
        raise
