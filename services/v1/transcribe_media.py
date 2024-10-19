import os
import whisper
import srt
from datetime import timedelta
from whisper.utils import WriteSRT, WriteVTT
from services.file_management import download_file
import logging

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Set the default local storage directory
STORAGE_PATH = "/tmp/"

def process_transcribe_media(media_url, task, format_type, word_timestamps, segments, response_type, language, job_id):
    
    """Transcribe media and return the transcript, SRT or ASS file path."""
    logger.info(f"Starting transcription for media URL: {media_url} with output type: {format_type}")
    input_filename = download_file(media_url, os.path.join(STORAGE_PATH, 'input_media'))
    logger.info(f"Downloaded media to local file: {input_filename}")

    try:
        model = whisper.load_model("base")
        logger.info("Loaded Whisper model")

        result = model.transcribe(
            input_filename,
            word_timestamps=word_timestamps,
            task=task,
            verbose=False
        )

        text = result['text']
        segments_json = None
        captions = None

        logger.info("Generated transcript output")

        if segments is True:
            segments_json = result['segments']

        if format_type in ['srt', 'vtt']:

            srt_subtitles = []
            for i, segment in enumerate(result['segments'], start=1):
                start = timedelta(seconds=segment['start'])
                end = timedelta(seconds=segment['end'])
                segment_text = segment['text'].strip()
                srt_subtitles.append(srt.Subtitle(i, start, end, segment_text))
            
            captions = srt.compose(srt_subtitles)

        os.remove(input_filename)

        logger.info(f"Removed local file: {input_filename}")
        logger.info(f"Transcription successful, output type: {response_type}")

        if (response_type == "json" ):

            return text, segments_json, captions
        else:
            
            text_filename = os.path.join(STORAGE_PATH, f"{job_id}.txt")
            with open(text_filename, 'w') as f:
                f.write(text)
            
            if segments is True:
                segments_filename = os.path.join(STORAGE_PATH, f"{job_id}.json")
                with open(segments_filename, 'w') as f:
                    f.write(str(segments_json))
            else:
                segments_filename = None;

            if format_type in ['srt', 'vtt']:
                captions_filename = os.path.join(STORAGE_PATH, f"{job_id}.srt")
                with open(captions_filename, 'w') as f:
                    f.write(captions)
            else:
                captions_filename = None;

            return text_filename, segments_filename, captions_filename


    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise