"""Version management for Extracta (Task 55).

Provides unified version access and SemVer validation for the project.
Version is read from the VERSION file in project root.
"""
from pathlib import Path
import re

# SemVer pattern for validation
SEMVER_PATTERN = re.compile(r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*))?(?:\+([a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*))?$')

def get_version() -> str:
    """Get the current version from VERSION file in project root."""
    # Find VERSION file relative to this module (src/common/version.py -> project root)
    version_file = Path(__file__).parent.parent.parent.parent / "VERSION"
    
    if not version_file.exists():
        raise FileNotFoundError(f"VERSION file not found at {version_file}")
    
    version = version_file.read_text(encoding="utf-8").strip()
    
    if not is_valid_semver(version):
        raise ValueError(f"Invalid SemVer format in VERSION file: {version}")
    
    return version

def is_valid_semver(version: str) -> bool:
    """Validate that version string follows SemVer pattern."""
    return bool(SEMVER_PATTERN.match(version))

def parse_version(version: str) -> tuple[int, int, int, str | None, str | None]:
    """Parse SemVer string into components.
    
    Returns:
        Tuple of (major, minor, patch, prerelease, build_metadata)
    """
    match = SEMVER_PATTERN.match(version)
    if not match:
        raise ValueError(f"Invalid SemVer format: {version}")
    
    major, minor, patch, prerelease, build_metadata = match.groups()
    return (int(major), int(minor), int(patch), prerelease, build_metadata)

# Module-level version constant
__version__ = get_version()

__all__ = ["get_version", "is_valid_semver", "parse_version", "__version__"]