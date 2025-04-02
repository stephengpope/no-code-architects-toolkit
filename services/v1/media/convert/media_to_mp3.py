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
import requests
from services.file_management import download_file
from config import LOCAL_STORAGE_PATH

def process_media_to_mp3(media_url, job_id, bitrate='128k', sample_rate=None):
    """Convert media to MP3 format with specified bitrate and sample rate."""
    input_filename = download_file(media_url, os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_input"))
    output_filename = f"{job_id}.mp3"
    output_path = os.path.join(LOCAL_STORAGE_PATH, output_filename)

    try:
        # Build the ffmpeg command
        stream = ffmpeg.input(input_filename)
        output_options = {'acodec': 'libmp3lame', 'audio_bitrate': bitrate}
        
        # Only set sample rate if provided
        if sample_rate is not None:
            output_options['ar'] = sample_rate
            
        # Convert media file to MP3 with specified options
        (
            stream
            .output(output_path, **output_options)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        os.remove(input_filename)
        sample_rate_info = f" and sample rate {sample_rate}Hz" if sample_rate is not None else ""
        print(f"Conversion successful: {output_path} with bitrate {bitrate}{sample_rate_info}")

        # Ensure the output file exists locally before attempting upload
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file {output_path} does not exist after conversion.")

        return output_path

    except Exception as e:
        print(f"Conversion failed: {str(e)}")
        raise 
