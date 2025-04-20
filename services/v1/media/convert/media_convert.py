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
import subprocess
from services.file_management import download_file
from config import LOCAL_STORAGE_PATH

def process_media_convert(media_url, job_id, output_format='mp4', video_codec='copy', audio_codec='copy', webhook_url=None):
    """Convert media to specified format with optional codec changes."""
    input_filename = download_file(media_url, os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_input"))
    output_filename = f"{job_id}.{output_format}"
    output_path = os.path.join(LOCAL_STORAGE_PATH, output_filename)

    try:
        # Set up the ffmpeg conversion
        stream = ffmpeg.input(input_filename)
        output_options = {}
        
        # Add format if specified
        if output_format:
            output_options['format'] = output_format
        
        # Handle audio-only formats
        audio_only_formats = ['mp3', 'aac', 'wav', 'flac', 'ogg', 'opus']
        
        if output_format in audio_only_formats:
            # For audio-only formats, we need specific audio codecs
            if audio_codec == 'copy':
                # Map codec to formats appropriately
                if output_format == 'mp3':
                    audio_codec = 'libmp3lame'
                elif output_format == 'aac':
                    audio_codec = 'aac'
                elif output_format == 'opus':
                    audio_codec = 'libopus'
                elif output_format == 'flac':
                    audio_codec = 'flac'
                elif output_format == 'ogg':
                    audio_codec = 'libvorbis'
                elif output_format == 'wav':
                    audio_codec = 'pcm_s16le'
            
            # For audio-only output, we don't need video codec
            output_options['acodec'] = audio_codec
            
            # Use the -vn flag to remove video stream
            output_options['vn'] = None
        else:
            # For video formats, apply both video and audio codec settings
            output_options['vcodec'] = video_codec
            output_options['acodec'] = audio_codec
        
        # Configure output
        stream = ffmpeg.output(stream, output_path, **output_options)
        
        # Get the ffmpeg command for logging
        cmd = ffmpeg.compile(stream)
        print(f"Running ffmpeg command: {' '.join(cmd)}")
        
        # Run the conversion
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        
        # Clean up input file
        os.remove(input_filename)
        print(f"Media conversion successful: {output_path} to format {output_format}")

        # Ensure the output file exists locally before attempting upload
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file {output_path} does not exist after conversion.")

        return output_path

    except Exception as e:
        print(f"Media conversion failed: {str(e)}")
        if isinstance(e, subprocess.CalledProcessError) and hasattr(e, 'stderr'):
            print(f"FFmpeg error details: {e.stderr.decode('utf-8')}")
        raise 