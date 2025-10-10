import os
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any
import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory that is automatically cleaned up after the test."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def temp_file() -> Generator[Path, None, None]:
    """Create a temporary file that is automatically cleaned up after the test."""
    fd, temp_path = tempfile.mkstemp()
    os.close(fd)
    path = Path(temp_path)
    yield path
    if path.exists():
        path.unlink()


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Provide a mock configuration dictionary for testing."""
    return {
        "DEBUG": True,
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "DATABASE_URL": "sqlite:///:memory:",
        "UPLOAD_FOLDER": "/tmp/test_uploads",
        "MAX_CONTENT_LENGTH": 16 * 1024 * 1024,  # 16MB
        "ALLOWED_EXTENSIONS": {"png", "jpg", "jpeg", "gif", "mp4", "mp3", "wav"},
        "FFMPEG_PATH": "/usr/bin/ffmpeg",
        "FFPROBE_PATH": "/usr/bin/ffprobe",
    }


@pytest.fixture
def mock_flask_app(mock_config):
    """Create a mock Flask application for testing."""
    app = Mock()
    app.config = mock_config
    app.logger = Mock()
    return app


@pytest.fixture
def mock_request():
    """Create a mock Flask request object."""
    request = Mock()
    request.files = {}
    request.form = {}
    request.args = {}
    request.json = {}
    request.method = "GET"
    request.headers = {}
    return request


@pytest.fixture
def sample_media_files(temp_dir) -> Dict[str, Path]:
    """Create sample media files for testing."""
    files = {}
    
    # Create a sample text file
    text_file = temp_dir / "sample.txt"
    text_file.write_text("This is a sample text file for testing.")
    files["text"] = text_file
    
    # Create a sample JSON file
    json_file = temp_dir / "sample.json"
    json_file.write_text('{"key": "value", "number": 42}')
    files["json"] = json_file
    
    # Create a sample image file (1x1 pixel PNG)
    image_file = temp_dir / "sample.png"
    # Minimal PNG header for a 1x1 transparent pixel
    png_data = bytes.fromhex(
        "89504e470d0a1a0a0000000d494844520000000100000001"
        "0802000000907753de000000017352474200aece1ce90000"
        "000467414d410000b18f0bfc6105000000097048597300000e"
        "c300000ec301c76fa8640000000c49444154185763f8ff00"
        "000301000118dd8db40000000049454e44ae426082"
    )
    image_file.write_bytes(png_data)
    files["image"] = image_file
    
    return files


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls for testing FFmpeg and other command-line tools."""
    mock = MagicMock()
    mock.run.return_value = MagicMock(
        returncode=0,
        stdout="mock output",
        stderr=""
    )
    mock.check_output.return_value = b"mock output"
    return mock


@pytest.fixture
def mock_cloud_storage():
    """Mock cloud storage clients for testing."""
    return {
        "gcs": Mock(),  # Google Cloud Storage
        "s3": Mock(),   # AWS S3
    }


@pytest.fixture
def mock_whisper_model():
    """Mock OpenAI Whisper model for testing transcription."""
    model = Mock()
    model.transcribe.return_value = {
        "text": "This is a mock transcription.",
        "segments": [
            {
                "start": 0.0,
                "end": 2.0,
                "text": "This is a mock transcription."
            }
        ],
        "language": "en"
    }
    return model


@pytest.fixture
def env_vars():
    """Set and restore environment variables for testing."""
    original_env = os.environ.copy()
    
    def _set_env(**kwargs):
        for key, value in kwargs.items():
            os.environ[key] = str(value)
        return os.environ
    
    yield _set_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically clean up any test files created during tests."""
    yield
    # Clean up common test directories if they exist
    test_dirs = ["test_output", "test_uploads", "test_temp"]
    for dir_name in test_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            shutil.rmtree(dir_path)


@pytest.fixture
def mock_http_response():
    """Create a mock HTTP response for testing API calls."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"status": "success"}
    response.text = '{"status": "success"}'
    response.content = b'{"status": "success"}'
    response.headers = {"Content-Type": "application/json"}
    return response