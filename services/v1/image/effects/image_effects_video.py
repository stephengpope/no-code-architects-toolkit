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
import logging
from services.file_management import download_file
from PIL import Image
from config import LOCAL_STORAGE_PATH
logger = logging.getLogger(__name__)

def process_image_effects_video(image_url, length, frame_rate, effect_type, job_id, webhook_url=None, orientation=None):
    """
    Generates a video from an image with specific effects like zoom-in-out or panning.
    """
    try:
        # Download the image file
        image_path = download_file(image_url, LOCAL_STORAGE_PATH)
        logger.info(f"Job {job_id}: Downloaded image for effects video to {image_path}")

        # Prepare the output path
        output_path = os.path.join(LOCAL_STORAGE_PATH, f"{job_id}.mp4")

        # Determine output dimensions based on orientation or default to landscape
        if orientation == 'portrait':
            scale_dims = "4320:7680"  # High-res intermediate for portrait
            output_dims = "1080x1920" # Final output dimensions
            ow, oh = 1080, 1920
            iw, ih = 4320, 7680 # Input dimensions *to zoompan filter* after initial scale
            logger.info(f"Job {job_id}: Using specified portrait orientation.")
        else:
            # Default to landscape
            if orientation != 'landscape' and orientation is not None:
                 logger.warning(f"Job {job_id}: Invalid orientation specified: '{orientation}'. Defaulting to landscape.")
            orientation = 'landscape'
            scale_dims = "7680:4320"  # High-res intermediate for landscape
            output_dims = "1920x1080" # Final output dimensions
            ow, oh = 1920, 1080
            iw, ih = 7680, 4320 # Input dimensions *to zoompan filter* after initial scale
            logger.info(f"Job {job_id}: Using landscape orientation (specified or default).")

        # Calculate total frames and midpoint
        total_frames = int(length * frame_rate)
        mid_frame = total_frames / 2

        # Build the zoompan filter string based on effect_type
        vf_filter = ""
        if effect_type == "zoom_in_out":
            max_zoom = 1.5 # Define how much to zoom in
            # Expression: Zoom in linearly to max_zoom until mid_frame, then zoom out linearly back to 1
            zoom_expr = f"if(lt(on,{mid_frame}), 1+(({max_zoom}-1)*on/{mid_frame}), {max_zoom}-(({max_zoom}-1)*(on-{mid_frame})/{mid_frame}))"
            vf_filter = f"scale={scale_dims}:force_original_aspect_ratio=decrease,pad={iw}:{ih}:(ow-iw)/2:(oh-ih)/2,zoompan=z='{zoom_expr}':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={output_dims},fps={frame_rate}"
            logger.info(f"Job {job_id}: Using zoom_in_out effect.")

        elif effect_type == "pan_rlr":
             # Ensure zoom is 1 (no zoom for panning)
             # Expression: Pan x from right (iw-ow) to left (0) until mid_frame, then pan x from left (0) to right (iw-ow)
             pan_x_expr = f"if(lt(on,{mid_frame}), ({iw}-{ow})*(1-on/{mid_frame}), ({iw}-{ow})*((on-{mid_frame})/{mid_frame}))"
             vf_filter = f"scale={scale_dims}:force_original_aspect_ratio=decrease,pad={iw}:{ih}:(ow-iw)/2:(oh-ih)/2,zoompan=z=1:d={total_frames}:x='{pan_x_expr}':y='(ih-{oh})/2':s={output_dims},fps={frame_rate}"
             logger.info(f"Job {job_id}: Using pan_rlr (right-left-right) effect.")
        else:
            # Default or fallback: Simple zoom-in (copied from original function)
            zoom_speed_default = 0.03 # Default zoom speed if needed
            zoom_factor = 1 + (zoom_speed_default * length)
            vf_filter = f"scale={scale_dims}:force_original_aspect_ratio=decrease,pad={iw}:{ih}:(ow-iw)/2:(oh-ih)/2,zoompan=z='min(1+({zoom_speed_default}*on/{frame_rate}),{zoom_factor})':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={output_dims},fps={frame_rate}"
            logger.warning(f"Job {job_id}: Unknown effect_type '{effect_type}'. Defaulting to simple zoom-in.")


        # Prepare FFmpeg command
        cmd = [
            'ffmpeg', '-framerate', str(frame_rate), '-loop', '1', '-i', image_path,
            '-vf', vf_filter,
            '-c:v', 'libx264', '-r', str(frame_rate), '-t', str(length), '-pix_fmt', 'yuv420p', output_path
        ]

        logger.info(f"Job {job_id}: Running FFmpeg command: {' '.join(cmd)}")

        # Run FFmpeg command
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Job {job_id}: FFmpeg command failed. Error: {result.stderr}")
            # Clean up input file even on error
            if os.path.exists(image_path):
                os.remove(image_path)
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)

        logger.info(f"Job {job_id}: Video created successfully: {output_path}")

        # Clean up input file
        os.remove(image_path)

        return output_path
    except Exception as e:
        logger.error(f"Job {job_id}: Error in process_image_effects_video: {str(e)}", exc_info=True)
        # Clean up potentially downloaded input file on error
        if 'image_path' in locals() and os.path.exists(image_path):
             try:
                 os.remove(image_path)
             except OSError as rm_err:
                 logger.error(f"Job {job_id}: Error cleaning up input file {image_path}: {rm_err}")
        raise 
