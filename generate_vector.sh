#!/bin/bash

for file in $(find . -type f \( -iname "*.md" -o -name "*.py" -o -name "Dockerfile" \) \
    -not -name "audio_mixing.py" \
    -not -name "authenticate.py" \
    -not -name "authentication.py" \
    -not -name "caption_video.py" \
    -not -name "combine_videos.py" \
    -not -name "extract_keyframes.py" \
    -not -name "ffmpeg_toolkit.py" \
    -not -name "file_management.py" \
    -not -name "image_to_video.py" \
    -not -name "media_to_mp3.py" \
    -not -name "transcribe_media.py" \
    -not -name "transcription.py"); do
    echo "File START: $file" >> output.txt
    echo -e "\n\n" >> output.txt
    cat "$file" >> output.txt
    echo -e "\n\nFile END\n\n" >> output.txt
done