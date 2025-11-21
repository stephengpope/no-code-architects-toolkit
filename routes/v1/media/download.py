from flask import Blueprint
from app_utils import *
import logging
import os
import yt_dlp
import tempfile
from werkzeug.utils import secure_filename
import uuid
from services.cloud_storage import upload_file
from services.authentication import authenticate
from services.file_management import download_file
from urllib.parse import quote, urlparse
import requests

v1_media_download_bp = Blueprint('v1_media_download', __name__)
logger = logging.getLogger(__name__)

@v1_media_download_bp.route('/v1/BETA/media/download', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "media_url": {"type": "string", "format": "uri"},
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"},
        "cookie": {"type": "string", "description": "Path to cookie file, URL to cookie file, or cookie string in Netscape format"},
        "cloud_upload": {"type": "boolean"},
        "format": {
            "type": "object",
            "properties": {
                "quality": {"type": "string"},
                "format_id": {"type": "string"},
                "resolution": {"type": "string"},
                "video_codec": {"type": "string"},
                "audio_codec": {"type": "string"}
            }
        },
        "audio": {
            "type": "object",
            "properties": {
                "extract": {"type": "boolean"},
                "format": {"type": "string"},
                "quality": {"type": "string"}
            }
        },
        "thumbnails": {
            "type": "object",
            "properties": {
                "download": {"type": "boolean"},
                "download_all": {"type": "boolean"},
                "formats": {"type": "array", "items": {"type": "string"}},
                "convert": {"type": "boolean"},
                "embed_in_audio": {"type": "boolean"}
            }
        },
        "subtitles": {
            "type": "object",
            "properties": {
                "download": {"type": "boolean"},
                "languages": {"type": "array", "items": {"type": "string"}},
                "format": {
                    "type": "string",
                    "enum": [
                        "srt",      # SubRip Subtitle (most common)
                        "vtt",      # Web Video Text Tracks
                        "json3"     # YouTube's JSON format
                    ]
                },
                "cloud_upload": {"type": "boolean"}
            }
        },
        "download": {
            "type": "object",
            "properties": {
                "max_filesize": {"type": "integer"},
                "rate_limit": {"type": "string"},
                "retries": {"type": "integer"}
            }
        }
    },
    "required": ["media_url"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def download_media(job_id, data):
    media_url = data['media_url']
    cookie = data.get('cookie')

    format_options = data.get('format', {})
    audio_options = data.get('audio', {})
    thumbnail_options = data.get('thumbnails', {})
    subtitle_options = data.get('subtitles', {})
    download_options = data.get('download', {})

    logger.info(f"Job {job_id}: Received download request for {media_url}")

    try:
        # Create a temporary directory for downloads
        with tempfile.TemporaryDirectory() as temp_dir:
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'best',  # Download best quality
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'download': data.get('cloud_upload', True)
            }
            
            ydl_opts['proxy'] = os.environ.get('MEDIA_DOWNLOAD_PROXY')

            # Add cookies if provided
            if cookie:
                if os.path.isfile(cookie):
                    ydl_opts['cookiefile'] = cookie
                elif urlparse(cookie).scheme in ('http', 'https'):
                    # If cookie is a URL, download it first
                    ydl_opts['cookiefile'] = download_file(cookie, temp_dir)
                else:
                    # If cookie is a string, write it to a temporary file
                    cookie_file = os.path.join(temp_dir, 'cookies.txt')
                    with open(cookie_file, 'w') as f:
                        f.write(cookie)
                    ydl_opts['cookiefile'] = cookie_file

            # Add format options if specified
            if format_options:
                format_str = []
                if format_options.get('quality'):
                    format_str.append(format_options['quality'])
                if format_options.get('format_id'):
                    format_str.append(format_options['format_id'])
                if format_options.get('resolution'):
                    format_str.append(format_options['resolution'])
                if format_options.get('video_codec'):
                    format_str.append(format_options['video_codec'])
                if format_options.get('audio_codec'):
                    format_str.append(format_options['audio_codec'])
                if format_str:
                    ydl_opts['format'] = '+'.join(format_str)

            # Add audio options if specified
            if audio_options:
                if audio_options.get('extract'):
                    ydl_opts['extract_audio'] = True
                    if audio_options.get('format'):
                        ydl_opts['audio_format'] = audio_options['format']
                    if audio_options.get('quality'):
                        ydl_opts['audio_quality'] = audio_options['quality']

            # Add thumbnail options if specified
            if thumbnail_options:
                ydl_opts['writesubtitles'] = thumbnail_options.get('download', False)
                ydl_opts['writeallsubtitles'] = thumbnail_options.get('download_all', False)
                if thumbnail_options.get('formats'):
                    ydl_opts['subtitleslangs'] = thumbnail_options['formats']
                ydl_opts['convert_thumbnails'] = thumbnail_options.get('convert', False)
                ydl_opts['embed_thumbnail_in_audio'] = thumbnail_options.get('embed_in_audio', False)

            # Add subtitle options if specified
            if subtitle_options:
                ydl_opts['writesubtitles'] = subtitle_options.get('download', False)
                if subtitle_options.get('languages'):
                    ydl_opts['subtitleslangs'] = subtitle_options['languages']
                if subtitle_options.get('format'):
                    ydl_opts['subtitlesformat'] = subtitle_options['format']

            # Add download options if specified
            if download_options:
                if download_options.get('max_filesize'):
                    ydl_opts['max_filesize'] = download_options['max_filesize']
                if download_options.get('rate_limit'):
                    ydl_opts['limit_rate'] = download_options['rate_limit']
                if download_options.get('retries'):
                    ydl_opts['retries'] = download_options['retries']

            # Download the media
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(media_url, download=data.get('cloud_upload', True))
                
                if not data.get('cloud_upload', True):
                    media_url = info['url']
                else:
                    filename = ydl.prepare_filename(info)
                    # Upload to cloud storage
                    media_url = upload_file(filename)
                    # Clean up the temporary file
                    os.remove(filename)

                # Prepare response
                response = {
                    "media": {
                        "media_url": media_url,
                        "title": info.get('title'),
                        "format_id": info.get('format_id'),
                        "ext": info.get('ext'),
                        "resolution": info.get('resolution'),
                        "filesize": info.get('filesize'),
                        "width": info.get('width'),
                        "height": info.get('height'),
                        "fps": info.get('fps'),
                        "video_codec": info.get('vcodec'),
                        "audio_codec": info.get('acodec'),
                        "upload_date": info.get('upload_date'),
                        "duration": info.get('duration'),
                        "view_count": info.get('view_count'),
                        "uploader": info.get('uploader'),
                        "uploader_id": info.get('uploader_id'),
                        "description": info.get('description')
                    }
                }

                # Add thumbnails if available and requested
                if info.get('thumbnails') and thumbnail_options.get('download', False):
                    response["thumbnails"] = []
                    for thumbnail in info['thumbnails']:
                        if thumbnail.get('url'):
                            try:
                                # Download the thumbnail first
                                thumbnail_path = download_file(thumbnail['url'], temp_dir)
                                # Upload to cloud storage
                                thumbnail_url = upload_file(thumbnail_path)
                                # Clean up the temporary thumbnail file
                                os.remove(thumbnail_path)
                                
                                response["thumbnails"].append({
                                    "id": thumbnail.get('id', 'default'),
                                    "image_url": thumbnail_url,
                                    "width": thumbnail.get('width'),
                                    "height": thumbnail.get('height'),
                                    "original_format": thumbnail.get('ext'),
                                    "converted": thumbnail.get('converted', False)
                                })
                            except Exception as e:
                                logger.error(f"Error processing thumbnail: {str(e)}")
                                continue

                # Process subtitles if available
                if 'subtitles' in info and subtitle_options.get('download', False):
                    logger.info(f"Job {job_id}: Found subtitles in info: {info['subtitles']}")
                    response["subtitles"] = {}  # Changed from array to object
                    requested_languages = subtitle_options.get('languages', [])
                    requested_format = subtitle_options.get('format', 'srt')
                    subtitle_cloud_upload = subtitle_options.get('cloud_upload', True)  # Default to True
                    
                    # If no languages specified, use all available languages
                    if not requested_languages:
                        requested_languages = list(info['subtitles'].keys())
                        logger.info(f"Job {job_id}: No languages specified, using all available: {requested_languages}")
                    
                    for lang, subtitle_list in info['subtitles'].items():
                        # Skip if language not in requested list
                        if lang not in requested_languages:
                            continue
                            
                        try:
                            logger.info(f"Job {job_id}: Processing subtitle for language {lang}")
                            # Find the requested format
                            subtitle_data = None
                            for subtitle in subtitle_list:
                                if subtitle['ext'] == requested_format:
                                    subtitle_data = subtitle
                                    break
                                    
                            if not subtitle_data:
                                logger.warning(f"Job {job_id}: Requested format {requested_format} not available for {lang}")
                                continue
                            
                            # If cloud upload is requested, download and upload the subtitle
                            if subtitle_cloud_upload:
                                try:
                                    subtitle_path = download_file(subtitle_data['url'], temp_dir)
                                    cloud_url = upload_file(subtitle_path)
                                    subtitle_data['url'] = cloud_url
                                except Exception as e:
                                    logger.warning(f"Job {job_id}: Failed to download subtitle for {lang}: {str(e)}")
                                    continue
                            
                            # Add subtitle data to response using language code as key
                            response["subtitles"][lang] = subtitle_data
                            logger.info(f"Job {job_id}: Successfully processed subtitle for {lang}")
                        except Exception as e:
                            logger.error(f"Job {job_id}: Error processing subtitle: {str(e)}")
                            continue
                else:
                    logger.info(f"Job {job_id}: No subtitles found in info or download not requested")
                
                return response, "/v1/media/download", 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during download process - {str(e)}")
        return str(e), "/v1/media/download", 500 