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
import subprocess
import json
import logging
from services.file_management import download_file
from config import LOCAL_STORAGE_PATH

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_media_metadata(media_url, job_id=None):
    """
    Extract metadata from a media file including video/audio properties.
    
    Args:
        media_url (str): URL of the media file to analyze
        job_id (str, optional): Unique job identifier
        
    Returns:
        dict: Dictionary containing all available metadata for the media file
    """
    logger.info(f"Starting metadata extraction for {media_url}")
    
    # Download the file
    input_filename = download_file(media_url, os.path.join(LOCAL_STORAGE_PATH, f"{job_id}_metadata_input"))
    logger.info(f"Downloaded media to local file: {input_filename}")
    
    try:
        # Initialize metadata dictionary
        metadata = {}
        
        # Get file size
        metadata['filesize'] = os.path.getsize(input_filename)
        metadata['filesize_mb'] = round(metadata['filesize'] / (1024 * 1024), 2)  # Convert to MB
        
        # Run ffprobe to get detailed metadata
        ffprobe_command = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            input_filename
        ]
        
        logger.info(f"Running ffprobe command: {' '.join(ffprobe_command)}")
        result = subprocess.run(ffprobe_command, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Error during ffprobe: {result.stderr}")
            raise Exception(f"ffprobe error: {result.stderr}")
            
        probe_data = json.loads(result.stdout)
        
        # Get format information
        if 'format' in probe_data:
            format_data = probe_data['format']
            
            # Get duration if available
            if 'duration' in format_data:
                metadata['duration'] = float(format_data['duration'])
                # Format duration as HH:MM:SS.mm
                mins, secs = divmod(metadata['duration'], 60)
                hours, mins = divmod(mins, 60)
                metadata['duration_formatted'] = f"{int(hours):02d}:{int(mins):02d}:{secs:.2f}"
            
            # Get format/container type
            if 'format_name' in format_data:
                metadata['format'] = format_data['format_name']
                
            # Get overall bitrate if available
            if 'bit_rate' in format_data:
                metadata['overall_bitrate'] = int(format_data['bit_rate'])
                metadata['overall_bitrate_mbps'] = round(metadata['overall_bitrate'] / 1000000, 2)  # Convert to Mbps
        
        # Process streams information
        if 'streams' in probe_data:
            has_video = False
            has_audio = False
            
            for stream in probe_data['streams']:
                stream_type = stream.get('codec_type')
                
                if stream_type == 'video' and not has_video:
                    has_video = True
                    
                    # Basic video properties
                    metadata['video_codec'] = stream.get('codec_name', 'unknown')
                    metadata['video_codec_long'] = stream.get('codec_long_name', 'unknown')
                    
                    # Resolution
                    if 'width' in stream and 'height' in stream:
                        metadata['width'] = stream['width']
                        metadata['height'] = stream['height']
                        metadata['resolution'] = f"{stream['width']}x{stream['height']}"
                    
                    # Frame rate
                    if 'r_frame_rate' in stream:
                        try:
                            num, den = map(int, stream['r_frame_rate'].split('/'))
                            if den != 0:  # Avoid division by zero
                                metadata['fps'] = round(num / den, 2)
                        except (ValueError, ZeroDivisionError):
                            logger.warning("Unable to parse frame rate")
                    
                    # Bitrate
                    if 'bit_rate' in stream:
                        metadata['video_bitrate'] = int(stream['bit_rate'])
                        metadata['video_bitrate_mbps'] = round(metadata['video_bitrate'] / 1000000, 2)  # Convert to Mbps
                    
                    # Pixel format
                    if 'pix_fmt' in stream:
                        metadata['pixel_format'] = stream['pix_fmt']
                    
                elif stream_type == 'audio' and not has_audio:
                    has_audio = True
                    
                    # Basic audio properties
                    metadata['audio_codec'] = stream.get('codec_name', 'unknown')
                    metadata['audio_codec_long'] = stream.get('codec_long_name', 'unknown')
                    
                    # Audio channels
                    if 'channels' in stream:
                        metadata['audio_channels'] = stream['channels']
                    
                    # Sample rate
                    if 'sample_rate' in stream:
                        metadata['audio_sample_rate'] = int(stream['sample_rate'])
                        metadata['audio_sample_rate_khz'] = round(metadata['audio_sample_rate'] / 1000, 1)  # Convert to kHz
                    
                    # Bitrate
                    if 'bit_rate' in stream:
                        metadata['audio_bitrate'] = int(stream['bit_rate'])
                        metadata['audio_bitrate_kbps'] = round(metadata['audio_bitrate'] / 1000, 0)  # Convert to kbps
            
            # Add flags indicating presence of streams
            metadata['has_video'] = has_video
            metadata['has_audio'] = has_audio
        
        # Clean up the downloaded file
        if os.path.exists(input_filename):
            os.remove(input_filename)
            logger.info(f"Removed temporary file: {input_filename}")
        
        return metadata
        
    except Exception as e:
        logger.error(f"Metadata extraction failed: {str(e)}")
        
        # Clean up temporary file if it exists
        if 'input_filename' in locals() and os.path.exists(input_filename):
            os.remove(input_filename)
            
        raise