from flask import Blueprint, jsonify
import logging
from services.authentication import authenticate
import boto3
import json

SEVEN_DAYS_IN_SECONDS = 7 * 24 * 60 * 60

v1_videos_get_bp = Blueprint('v1_videos_get', __name__)
logger = logging.getLogger(__name__)

def load_env_variables() -> dict:
    """Load environment variables from .env_variables.json"""
    with open('.env_variables.json') as f:
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

@v1_videos_get_bp.route('/v1/videos', methods=['GET'])
@authenticate
def get_videos():
    logger.info("/v1/videos GET request received")
    try:
        env_vars = load_env_variables()
        s3_client = get_s3_client()

        # List objects in the bucket
        response = s3_client.list_objects_v2(
            Bucket=env_vars['S3_BUCKET_NAME'],
            Prefix='',
        )

        # Filter for MP4 files and format response
        videos = []
        for obj in response.get('Contents', []):
            key = obj['Key']
            if key.lower().endswith('.mp4'):
                signed_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': env_vars['S3_BUCKET_NAME'],
                        'Key': key
                    },
                    ExpiresIn=SEVEN_DAYS_IN_SECONDS
                )
                
                videos.append({
                    "name": key,
                    "presigned_url": signed_url,
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat()
                })

        logger.info(f"Returning {len(videos)} videos to client")
        return jsonify({
            "videos": videos
        }), 200

    except Exception as e:
        logger.error(f"Error getting videos: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500
