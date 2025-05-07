import os
import requests
import time
import ffmpeg
import asyncio
import edge_tts
import re
from config import LOCAL_STORAGE_PATH
from time import sleep

def check_ratelimit(response: requests.Response) -> bool:
    """
    Checks if the response is a ratelimit response (status code 429).
    If it is, it sleeps for the time specified in the response's 'X-RateLimit-Reset' header.
    """
    if response.status_code == 429:
        try:
            reset_time = int(response.headers["X-RateLimit-Reset"])
            sleep_duration = reset_time - int(time.time())
            if sleep_duration > 0:
                print(f"Rate limit hit. Sleeping for {sleep_duration} seconds.")
                time.sleep(sleep_duration)
                return False  # Do not retry immediately; wait for the specified time
        except KeyError:
            print("Rate limit hit, but no 'X-RateLimit-Reset' header found.")
            return False
    return True  # Return True if no rate limit, or if we handled the rate limit correctly


def chunk_text_for_tts(text, max_chars):
    # Normalize whitespace
    text = text.replace("\n", " ").strip()

    # Split by paragraphs (if labeled) or just treat as one big paragraph
    paragraphs = re.split(r"(?i)paragraph \d+\.?", text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]  # Remove blanks

    all_chunks = []

    for paragraph in paragraphs:
        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)

        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chars:
                current_chunk += sentence + " "
            else:
                all_chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk.strip():
            all_chunks.append(current_chunk.strip())

    return all_chunks


def handle_streamlabs_polly_tts(text, voice, job_id):
    """
    Generate TTS audio using Streamlabs Polly and save it to LOCAL_STORAGE_PATH.
    Handles long text by chunking and combining audio files using ffmpeg.
    """
    # Define the valid voices inside the function
    # https://lazypy.ro/tts/
    VALID_VOICES = [
        "Brian", "Emma", "Russell", "Joey", "Matthew", "Joanna", "Kimberly", 
        "Amy", "Geraint", "Nicole", "Justin", "Ivy", "Kendra", "Salli", "Raveena"
    ]

    if not voice:
        voice = "Brian"

    # Validate the voice to make sure it's in the valid voices list
    if voice not in VALID_VOICES:
        raise ValueError(f"Invalid voice: {voice}. Valid voices are: {', '.join(VALID_VOICES)}")

    # Chunk the text to avoid exceeding the limit for Streamlabs Polly TTS
    chunks = chunk_text_for_tts(text,550)
    audio_chunk_paths = []

    # Loop through each chunk and request audio from Streamlabs Polly
    for idx, chunk in enumerate(chunks):
        body = {"voice": voice, "text": chunk, "service": "polly"}
        headers = {"Referer": "https://streamlabs.com/"}

        while True:
            response = requests.post("https://streamlabs.com/polly/speak", headers=headers, data=body)

            if check_ratelimit(response):  # If rate limit isn't hit, break out of retry loop
                if response.status_code == 200:  # Success
                    try:
                        # Get the audio URL from the response and download the audio file
                        voice_data = requests.get(response.json()["speak_url"])
                        chunk_filename = f"{job_id}_part_{idx}.mp3"
                        chunk_path = os.path.join(LOCAL_STORAGE_PATH, chunk_filename)

                        # Save the audio to the file system
                        with open(chunk_path, "wb") as f:
                            f.write(voice_data.content)

                        audio_chunk_paths.append(chunk_path)
                        print(f"Chunk {idx} saved successfully.")
                        break  # Break out of the retry loop once successful
                    except (KeyError, requests.exceptions.JSONDecodeError):
                        print(f"Error occurred while downloading audio for chunk {idx}")
                        return None
                else:
                    print(f"Error {response.status_code} occurred for chunk {idx}.")
                    return None
            else:
                print(f"Rate limit hit for chunk {idx}, retrying...")

    # Combine all the audio chunks into one file using ffmpeg
    if not audio_chunk_paths:
        print("No audio files were generated.")
        return None

    output_filename = f"{job_id}.mp3"
    output_path = os.path.join(LOCAL_STORAGE_PATH, output_filename)

    try:
        # Create the concat list for ffmpeg
        concat_file_path = os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_concat_list.txt")
        with open(concat_file_path, 'w') as concat_file:
            for path in audio_chunk_paths:
                concat_file.write(f"file '{os.path.abspath(path)}'\n")

        # Concatenate the audio files using ffmpeg
        ffmpeg.input(concat_file_path, format='concat', safe=0).output(output_path, c='copy').run(overwrite_output=True)

        # Clean up chunk files and concat file
        for path in audio_chunk_paths:
            os.remove(path)
        os.remove(concat_file_path)

        print(f"Audio combination successful: {output_path}")

        # Ensure the final output file exists
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file {output_path} does not exist after combination.")

        return output_path
    except Exception as e:
        print(f"Audio combination failed: {str(e)}")
        raise


def handle_edge_tts(text, voice, job_id):
    """
    Generate TTS audio using edge-tts, upload to cloud, and return the cloud URL.
    """
    speed=1.0
    format="mp3"

    async def _generate_tts_async(text, voice, output_path, rate="+0%", format="mp3"):
        # Fetch available voices
        voices = await edge_tts.list_voices()
        valid_voices = {v["ShortName"] for v in voices}
        # Default or validate voice
        if not voice:
            voice = "en-US-AvaNeural"
        elif voice not in valid_voices:
            raise ValueError(
                f"Invalid voice: {voice}.\n"
                f"You can preview voice samples at: https://tts.travisvn.com/\n\n"
                f"Available voices are:\n" + ", ".join(sorted(valid_voices))
            )
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(output_path)

    # Prepare output path
    output_filename = f"{job_id}.{format}"
    output_path = os.path.join(LOCAL_STORAGE_PATH, output_filename)

    # Convert speed to edge-tts rate string
    rate_percent = int((speed - 1.0) * 100)
    rate_str = f"{rate_percent:+d}%"

    # Run edge-tts asynchronously
    asyncio.run(_generate_tts_async(text, voice, output_path, rate=rate_str, format=format))

    return output_path






TTS_HANDLERS = {
    'edge-tts': handle_edge_tts,
    'streamlabs-polly': handle_streamlabs_polly_tts,  # Added Streamlabs Polly handler here
}

def generate_tts(tts, text, voice, job_id):
    """
    Generate TTS audio using the specified tts and return the file path.
    """
    # Default to edge-tts if no tts is specified
    
    if tts not in TTS_HANDLERS:
        raise ValueError(f"Unsupported tts: {tts}")

    # Call the appropriate handler function
    return TTS_HANDLERS[tts](text, voice, job_id)