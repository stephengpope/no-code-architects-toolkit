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
import logging
from services.file_management import download_file
from config import LOCAL_STORAGE_PATH

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def process_media_convert(media_url, job_id, output_format='mp4', video_codec='libx264', video_preset='medium', video_crf=23, audio_codec='aac', audio_bitrate='128k', webhook_url=None):
    """
    Convert media to specified format with customizable encoding settings.
    
    Args:
        media_url (str): URL of the media file to convert
        job_id (str): Unique job identifier
        output_format (str): Target format (e.g., 'mp4', 'mov', 'mp3', etc.)
        video_codec (str): Video codec to use (default: 'libx264')
        video_preset (str): Encoding preset for speed/quality tradeoff (default: 'medium')
        video_crf (int): Constant Rate Factor for quality (0-51, default: 23)
        audio_codec (str): Audio codec to use (default: 'aac')
        audio_bitrate (str): Audio bitrate (default: '128k')
        webhook_url (str, optional): URL to send completion webhook
        
    Returns:
        str: Path to the converted output file
    """
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
            # Always override the audio codec for audio-only formats
            # to ensure format compatibility, regardless of what was requested
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
            
            # Apply additional video encoding options when not using copy
            if video_codec != 'copy':
                output_options['preset'] = video_preset
                output_options['crf'] = str(video_crf)
                
            # Apply audio bitrate when not using copy
            if audio_codec != 'copy':
                output_options['b:a'] = audio_bitrate
        
        # Configure output
        stream = ffmpeg.output(stream, output_path, **output_options)
        
        # Get the ffmpeg command for logging
        cmd = ffmpeg.compile(stream)
        logger.info(f"Running ffmpeg command: {' '.join(cmd)}")
        
        # Run the conversion
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        
        # Clean up input file
        os.remove(input_filename)
        logger.info(f"Media conversion successful: {output_path} to format {output_format}")

        # Ensure the output file exists locally before attempting upload
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file {output_path} does not exist after conversion.")

        return output_path

    except Exception as e:
        error_msg = f"Media conversion failed: {str(e)}"
        logger.error(error_msg)
        
        # Handle ffmpeg errors specially to provide more context
        if hasattr(e, 'stderr') and e.stderr:
            stderr_output = e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else str(e.stderr)
            detailed_error = f"FFmpeg error details: {stderr_output}"
            logger.error(detailed_error)
            # Raise with combined error info for better debugging
            raise Exception(f"{error_msg} - {detailed_error}")
        
        # Clean up input file if it exists
        if 'input_filename' in locals() and os.path.exists(input_filename):
            try:
                os.remove(input_filename)
                logger.info(f"Cleaned up input file: {input_filename}")
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up input file: {str(cleanup_error)}")
                
        # Clean up output file if it exists
        if 'output_path' in locals() and os.path.exists(output_path):
            try:
                os.remove(output_path)
                logger.info(f"Cleaned up output file: {output_path}")
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up output file: {str(cleanup_error)}")
                
        raise