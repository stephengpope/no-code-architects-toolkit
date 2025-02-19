import os
import json
import boto3
import re
import argparse
from pathlib import Path
from typing import Optional, List, Dict

def validate_storage_key(key: str) -> str:
    """
    Strictly validate a storage key.
    Must be lowercase, start with a letter, and contain only letters, numbers, and underscores.
    
    Args:
        key (str): The key to validate
        
    Returns:
        str: The key if valid
        
    Raises:
        ValueError: If key doesn't match the required format
    """
    # Remove extension if present
    key = os.path.splitext(key)[0]
    
    if not key:
        raise ValueError("Empty key is not allowed")
        
    if key != key.lower():
        raise ValueError(f"Key must be lowercase: '{key}'")
        
    if not re.match(r'^[a-z][a-z0-9_]*$', key):
        raise ValueError(
            f"Invalid key format '{key}'. Keys must:\n"
            "- Start with a lowercase letter\n"
            "- Contain only lowercase letters, numbers, and underscores\n"
            "- No spaces or special characters allowed"
        )
    
    return key

def get_videos_from_input_dir() -> List[Dict[str, str]]:
    """Get list of videos from the input directory"""
    input_dir = Path(__file__).parent / 'input'
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    videos = []
    for video_path in input_dir.glob('*.mp4'):
        key = validate_storage_key(video_path.stem)
        videos.append({
            "path": str(video_path),
            "key": f"{key}.mp4"
        })
    
    return videos

# Example video sources (only used if not reading from input dir)
VIDEO_SOURCES: List[Dict[str, str]] = [
    {
        "url": "https://example.com/video1.mp4",
        "key": "intro_video.mp4"
    },
    {
        "url": "https://example.com/video2.mp4",
        "key": "tutorial_part1.mp4"
    }
]

def load_env_variables() -> dict:
    """Load environment variables from .env_variables.json"""
    env_path = Path(__file__).parent.parent / '.env_variables.json'
    with open(env_path) as f:
        return json.load(f)

def get_s3_client():
    """Initialize and return an S3 client configured for Supabase storage"""
    env_vars = load_env_variables()
    
    return boto3.client(
        's3',
        endpoint_url=env_vars['S3_ENDPOINT_URL'],
        aws_access_key_id=env_vars['S3_ACCESS_KEY'],
        aws_secret_access_key=env_vars['S3_SECRET_KEY'],
        region_name=env_vars['S3_REGION']
    )

def upload_video_to_supabase(
    video_path: str,
    destination_key: Optional[str] = None,
    content_type: str = 'video/mp4'
) -> str:
    """
    Upload a video file to Supabase storage.
    
    Args:
        video_path (str): Path to the video file to upload
        destination_key (Optional[str]): The key (path) where the file will be stored in Supabase.
                                       If not provided, uses the filename.
        content_type (str): The content type of the file. Defaults to 'video/mp4'
    
    Returns:
        str: The URL of the uploaded video
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    env_vars = load_env_variables()
    s3_client = get_s3_client()
    
    # If no destination key is provided, use the validated basename
    if destination_key is None:
        destination_key = f"{validate_storage_key(os.path.basename(video_path))}.mp4"
    
    # Upload the file
    with open(video_path, 'rb') as video_file:
        s3_client.upload_fileobj(
            video_file,
            env_vars['S3_BUCKET_NAME'],
            destination_key,
            ExtraArgs={'ContentType': content_type}
        )
    
    # Construct and return the URL
    url = f"{env_vars['S3_ENDPOINT_URL']}/object/public/{env_vars['S3_BUCKET_NAME']}/{destination_key}"
    return url

def main():
    parser = argparse.ArgumentParser(description='Upload videos to Supabase storage')
    parser.add_argument('--from_input_dir', action='store_true', default=True,
                      help='Read videos from scripts/input directory (default: True)')
    parser.add_argument('--no-from_input_dir', action='store_false', dest='from_input_dir',
                      help='Do not read from input directory, use VIDEO_SOURCES instead')
    
    args = parser.parse_args()
    
    try:
        if args.from_input_dir:
            videos = get_videos_from_input_dir()
            print(f"Found {len(videos)} videos in input directory")
            
            for video in videos:
                print(f"\nUploading {video['path']} as {video['key']}...")
                url = upload_video_to_supabase(video['path'], video['key'])
                print(f"Successfully uploaded to: {url}")
        else:
            print("Using predefined VIDEO_SOURCES")
            for source in VIDEO_SOURCES:
                # Note: This branch is not implemented as it requires downloading from URLs
                print(f"Warning: Uploading from URLs is not implemented yet")
                break
                
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 