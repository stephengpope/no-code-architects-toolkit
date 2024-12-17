#!/bin/bash

for file in $(find . -type f \( -iname "*.md" -o -iname "*.txt" -o -name "*.py" -o -name "Dockerfile" \) \
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
    echo "File: $file" >> "NCA Toolkit API Vector Doc.txt"
    echo -e "\n\n" >> "NCA Toolkit API Vector Doc.txt"
    cat "$file" >> "NCA Toolkit API Vector Doc.txt"
    echo -e "\n\n" >> "NCA Toolkit API Vector Doc.txt"
done