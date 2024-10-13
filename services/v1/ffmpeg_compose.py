import os
import ffmpeg
import requests
import subprocess
from services.file_management import download_file
from services.gcp_toolkit import upload_to_gcs, GCP_BUCKET_NAME, gcs_client

STORAGE_PATH = "/tmp/"

def process_ffmpeg_compose(data, job_id):
    output_filenames = []
    
    # Build FFmpeg command
    command = ["ffmpeg"]
    
    # Add global options
    for option in data.get("global_options", []):
        command.append(option["option"])
        if option["argument"] is not None:
            command.append(str(option["argument"]))
    
    # Add inputs
    for input_data in data["inputs"]:
        if "options" in input_data:
            for option in input_data["options"]:
                command.append(option["option"])
                if option["argument"] is not None:
                    command.append(str(option["argument"]))
        input_path = download_file(input_data["file_url"], STORAGE_PATH)
        command.extend(["-i", input_path])
    
    # Add filters
    if data.get("filters"):
        filter_complex = ";".join(filter_obj["filter"] for filter_obj in data["filters"])
        command.extend(["-filter_complex", filter_complex])
    
    # Add outputs
    for i, output in enumerate(data["outputs"]):
        output_filename = os.path.join(STORAGE_PATH, f"{job_id}_output_{i}.mp4")
        output_filenames.append(output_filename)
        for option in output["options"]:
            command.append(option["option"])
            if option["argument"] is not None:
                command.append(str(option["argument"]))
        command.append(output_filename)
    
    # Execute FFmpeg command
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"FFmpeg command failed: {e.stderr}")
    
    # Clean up input files
    for input_data in data["inputs"]:
        input_path = os.path.join(STORAGE_PATH, os.path.basename(input_data["file_url"]))
        if os.path.exists(input_path):
            os.remove(input_path)
    
    # Upload output files to GCP and create result array
    output_urls = []
    for output_filename in output_filenames:
        if os.path.exists(output_filename):
            gcs_url = upload_to_gcs(output_filename)
            output_urls.append({"file_url": gcs_url})
            os.remove(output_filename)  # Clean up local output file after upload
        else:
            raise Exception(f"Expected output file {output_filename} not found")
    
    return output_urls