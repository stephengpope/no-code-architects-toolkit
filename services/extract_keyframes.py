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
from services.file_management import download_file

STORAGE_PATH = "/tmp/"

def process_keyframe_extraction(video_url, job_id):
    video_path = download_file(video_url, STORAGE_PATH)

    # Extract keyframes
    output_pattern = os.path.join(STORAGE_PATH, f"{job_id}_%03d.jpg")
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f"select='eq(pict_type,I)',scale=iw*sar:ih,setsar=1",
        '-vsync', 'vfr',
        output_pattern
    ]

    print(f"Images: {cmd}")

    subprocess.run(cmd, check=True)

    # Upload keyframes to GCS and get URLs
    output_filenames = []
    for filename in sorted(os.listdir(STORAGE_PATH)):
        if filename.startswith(f"{job_id}_") and filename.endswith(".jpg"):
            file_path = os.path.join(STORAGE_PATH, filename)
            output_filenames.append(file_path)

    # Clean up input file
    os.remove(video_path)

    return output_filenames