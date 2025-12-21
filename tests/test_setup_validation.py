import pytest
import sys
import importlib
from pathlib import Path


class TestSetupValidation:
    """Validation tests to ensure the testing infrastructure is properly configured."""
    
    def test_pytest_is_installed(self):
        """Verify pytest is available."""
        assert "pytest" in sys.modules or importlib.util.find_spec("pytest") is not None
    
    def test_pytest_cov_is_installed(self):
        """Verify pytest-cov is available."""
        try:
            import pytest_cov
            assert pytest_cov is not None
        except ImportError:
            # Alternative check
            assert importlib.util.find_spec("pytest_cov") is not None
    
    def test_pytest_mock_is_installed(self):
        """Verify pytest-mock is available."""
        try:
            import pytest_mock
            assert pytest_mock is not None
        except ImportError:
            # Alternative check
            assert importlib.util.find_spec("pytest_mock") is not None
    
    def test_project_structure_exists(self):
        """Verify the project structure is correctly set up."""
        project_root = Path(__file__).parent.parent
        
        # Check main directories
        assert project_root.exists()
        assert (project_root / "tests").exists()
        assert (project_root / "tests" / "unit").exists()
        assert (project_root / "tests" / "integration").exists()
        
        # Check __init__.py files
        assert (project_root / "tests" / "__init__.py").exists()
        assert (project_root / "tests" / "unit" / "__init__.py").exists()
        assert (project_root / "tests" / "integration" / "__init__.py").exists()
        
        # Check conftest.py
        assert (project_root / "tests" / "conftest.py").exists()
    
    def test_pyproject_toml_exists(self):
        """Verify pyproject.toml exists and contains required sections."""
        project_root = Path(__file__).parent.parent
        pyproject_path = project_root / "pyproject.toml"
        
        assert pyproject_path.exists(), "pyproject.toml not found"
        
        content = pyproject_path.read_text()
        assert "[tool.poetry]" in content, "Poetry configuration not found"
        assert "[tool.pytest.ini_options]" in content, "Pytest configuration not found"
        assert "[tool.coverage.run]" in content, "Coverage configuration not found"
    
    def test_fixtures_are_available(self, temp_dir, mock_config, sample_media_files):
        """Verify that custom fixtures from conftest.py are available."""
        # Test temp_dir fixture
        assert temp_dir.exists()
        assert temp_dir.is_dir()
        
        # Test mock_config fixture
        assert isinstance(mock_config, dict)
        assert "DEBUG" in mock_config
        assert "TESTING" in mock_config
        
        # Test sample_media_files fixture
        assert isinstance(sample_media_files, dict)
        assert "text" in sample_media_files
        assert sample_media_files["text"].exists()
    
    @pytest.mark.unit
    def test_unit_marker_works(self):
        """Verify the unit test marker is properly configured."""
        assert True
    
    @pytest.mark.integration
    def test_integration_marker_works(self):
        """Verify the integration test marker is properly configured."""
        assert True
    
    @pytest.mark.slow
    def test_slow_marker_works(self):
        """Verify the slow test marker is properly configured."""
        assert True
    
    def test_coverage_is_configured(self):
        """Verify coverage is properly configured."""
        project_root = Path(__file__).parent.parent
        pyproject_path = project_root / "pyproject.toml"
        content = pyproject_path.read_text()
        
        # Check coverage settings in pyproject.toml
        assert "--cov=" in content
        assert "--cov-report=html" in content
        assert "--cov-report=xml" in content
        assert "--cov-fail-under=80" in content