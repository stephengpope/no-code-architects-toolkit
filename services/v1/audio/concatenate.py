# Copyright (c) 2025 Stephen G. Pope
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.



import os
import ffmpeg
from services.file_management import download_file
from config import LOCAL_STORAGE_PATH

def process_audio_concatenate(media_urls, job_id, webhook_url=None):
    """Combine multiple audio files into one."""
    input_files = []
    output_filename = f"{job_id}.mp3"
    output_path = os.path.join(LOCAL_STORAGE_PATH, output_filename)

    try:
        # Download all media files
        for i, media_item in enumerate(media_urls):
            url = media_item['audio_url']
            input_filename = download_file(url, os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_input_{i}"))
            input_files.append(input_filename)

        # Generate an absolute path concat list file for FFmpeg
        concat_file_path = os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_concat_list.txt")
        with open(concat_file_path, 'w') as concat_file:
            for input_file in input_files:
                # Write absolute paths to the concat list
                concat_file.write(f"file '{os.path.abspath(input_file)}'\n")

        # Use the concat demuxer to concatenate the audio files without re-encoding
        (
            ffmpeg.input(concat_file_path, format='concat', safe=0).
                output(output_path, c='copy').
                run(overwrite_output=True)
        )

        # Clean up input files
        for f in input_files:
            os.remove(f)
            
        os.remove(concat_file_path)  # Remove the concat list file after the operation

        print(f"Audio combination successful: {output_path}")

        # Check if the output file exists locally before upload
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file {output_path} does not exist after combination.")

        return output_path
    except Exception as e:
        print(f"Audio combination failed: {str(e)}")
        raise 