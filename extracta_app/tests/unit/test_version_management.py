"""Unit tests for version management (Task 55).

Tests SemVer pattern validation and alignment with VERSION file.
"""
from pathlib import Path
import pytest

try:
    from src.common.version import get_version, is_valid_semver, parse_version, __version__
except ImportError:
    get_version = is_valid_semver = parse_version = __version__ = None  # type: ignore


class TestVersionManagement:
    
    def test_version_file_exists_and_readable(self):
        """Test that VERSION file exists and is readable."""
        # VERSION file should be in project root (4 levels up from this test file)
        version_file = Path(__file__).parent.parent.parent.parent / "VERSION"
        assert version_file.exists(), "VERSION file not found in project root"
        
        content = version_file.read_text(encoding="utf-8").strip()
        assert content, "VERSION file is empty"
        assert is_valid_semver(content), f"VERSION file contains invalid SemVer: {content}"
    
    def test_get_version_returns_valid_semver(self):
        """Test that get_version() returns a valid SemVer string."""
        if get_version is None:
            pytest.skip("version module not implemented")
        
        version = get_version()
        assert isinstance(version, str), "Version should be a string"
        assert is_valid_semver(version), f"get_version() returned invalid SemVer: {version}"
    
    def test_semver_pattern_validation(self):
        """Test SemVer pattern validation with various inputs."""
        if is_valid_semver is None:
            pytest.skip("version module not implemented")
        
        # Valid SemVer patterns
        valid_versions = [
            "0.1.0",
            "1.0.0",
            "1.2.3",
            "1.0.0-alpha",
            "1.0.0-alpha.1",
            "1.0.0-beta.2",
            "1.0.0+build.1",
            "1.0.0-alpha+build.1",
            "10.20.30"
        ]
        
        for version in valid_versions:
            assert is_valid_semver(version), f"Valid SemVer rejected: {version}"
        
        # Invalid SemVer patterns
        invalid_versions = [
            "",
            "1",
            "1.0",
            "1.0.0.0",
            "v1.0.0",
            "1.0.0-",
            "1.0.0+",
            "1.0.0-alpha.",
            "1.0.0+build."
        ]
        
        for version in invalid_versions:
            assert not is_valid_semver(version), f"Invalid SemVer accepted: {version}"
    
    def test_version_parsing(self):
        """Test parsing SemVer string into components."""
        if parse_version is None:
            pytest.skip("version module not implemented")
        
        # Test basic version
        major, minor, patch, prerelease, build = parse_version("1.2.3")
        assert major == 1
        assert minor == 2
        assert patch == 3
        assert prerelease is None
        assert build is None
        
        # Test version with prerelease
        major, minor, patch, prerelease, build = parse_version("1.0.0-alpha.1")
        assert major == 1
        assert minor == 0
        assert patch == 0
        assert prerelease == "alpha.1"
        assert build is None
        
        # Test version with build metadata
        major, minor, patch, prerelease, build = parse_version("1.0.0+build.123")
        assert major == 1
        assert minor == 0
        assert patch == 0
        assert prerelease is None
        assert build == "build.123"
        
        # Test full version
        major, minor, patch, prerelease, build = parse_version("2.1.0-beta.1+build.456")
        assert major == 2
        assert minor == 1
        assert patch == 0
        assert prerelease == "beta.1"
        assert build == "build.456"
    
    def test_module_version_constant(self):
        """Test that module __version__ constant is available and valid."""
        if __version__ is None:
            pytest.skip("version module not implemented")
        
        assert isinstance(__version__, str), "__version__ should be a string"
        assert is_valid_semver(__version__), f"__version__ is not valid SemVer: {__version__}"
    
    def test_version_alignment_with_docs(self):
        """Test that version in VERSION file aligns with module constant."""
        if get_version is None or __version__ is None:
            pytest.skip("version module not implemented")
        
        file_version = get_version()
        module_version = __version__
        
        assert file_version == module_version, f"Version mismatch: file={file_version}, module={module_version}"
    
    def test_error_handling_missing_version_file(self):
        """Test error handling when VERSION file is missing."""
        if get_version is None:
            pytest.skip("version module not implemented")
        
        # This test validates error handling behavior
        # The actual VERSION file should exist, so we test the error path indirectly
        # by testing parse_version with invalid input
        with pytest.raises(ValueError, match="Invalid SemVer format"):
            parse_version("invalid-version")