import os
import json

def test_authenticate_endpoint(client):
    response = client.post('/authenticate', headers={'X-API-Key': os.environ.get('API_KEY')})
    assert response.status_code == 200
    assert response.json == [{"message": "Authorized"}]

def test_authenticate_fail(client):
    response = client.post('/authenticate', headers={'X-API-Key': 'wrong-key'})
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}

def test_convert_media_to_mp3(client, mocker):
    data = {
        "media_url": "https://drive.google.com/uc?id=1b7POZjewqM6HWPt27r0NShO1pDXDDfq9",
        "webhook_url": None
    }
    mocker.patch('services.convert_media_to_mp3.process_conversion', return_value="test.mp3")
    response = client.post('/media-to-mp3', json=data, headers={'X-API-Key': os.environ.get('API_KEY')})
    assert response.status_code == 200
    assert response.json['filename'].endswith('.mp3')

def test_transcribe_media(client, mocker):
    data = {
        "media_url": "https://drive.google.com/uc?id=1b7POZjewqM6HWPt27r0NShO1pDXDDfq9",
        "output": "transcript",
        "webhook_url": None
    }
    mocker.patch('services.transcribe_media.process_transcription', return_value="test transcription")
    response = client.post('/transcribe', json=data, headers={'X-API-Key': os.environ.get('API_KEY')})
    assert response.status_code == 200
    assert "response" in response.json

def test_combine_videos(client, mocker):
    data = {
        "media_urls": ["https://drive.google.com/uc?id=1b7POZjewqM6HWPt27r0NShO1pDXDDfq9", "https://drive.google.com/uc?id=1b7POZjewqM6HWPt27r0NShO1pDXDDfq9"],
        "webhook_url": None
    }
    mocker.patch('services.combine_videos.process_video_combination', return_value="combined.mp4")
    response = client.post('/combine-videos', json=data, headers={'X-API-Key': os.environ.get('API_KEY')})
    assert response.status_code == 200
    assert response.json['filename'].endswith('combined.mp4')

def test_audio_mixing(client, mocker):
    data = {
        "video_url": "https://drive.google.com/uc?id=1b7POZjewqM6HWPt27r0NShO1pDXDDfq9",
        "audio_url": "https://file-examples.com/storage/fe28b3ef8666c4c399639b9/2017/11/file_example_MP3_5MG.mp3",
        "video_vol": 100,
        "audio_vol": 100,
        "output_length": "video",
        "webhook_url": None
    }
    mocker.patch('services.audio_mixing.process_audio_mixing', return_value="mixed.mp4")
    response = client.post('/audio-mixing', json=data, headers={'X-API-Key': os.environ.get('API_KEY')})
    assert response.status_code == 200
    assert response.json['filename'].endswith('mixed.mp4')

def test_gdrive_upload(client, mocker):
    data = {
        "file_url": "https://drive.google.com/uc?id=1b7POZjewqM6HWPt27r0NShO1pDXDDfq9",
        "filename": "test.mp4",
        "folder_id": "folder_id",
        "webhook_url": None
    }
    mocker.patch('services.gdrive_upload.process_gdrive_upload', return_value="file_id")
    response = client.post('/gdrive-upload', json=data, headers={'X-API-Key': os.environ.get('API_KEY')})
    assert response.status_code == 200
    assert "file_id" in response.json
