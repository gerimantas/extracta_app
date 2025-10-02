"""Pytest configuration ensuring the top-level ``src`` package is importable.

Tests import modules via ``from src.common.hashing import ...`` so Python must
see the directory *containing* the ``src`` package (i.e. ``extracta_app``), not
the ``src`` directory itself. Previously we appended ``<repo>/extracta_app/src``
which made subpackages directly importable (``from common import hashing``) but
left ``src.*`` imports failing. This fixes the path to the parent directory.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PACKAGE_DIR = PROJECT_ROOT / "src"  # contains __init__.py
if SRC_PACKAGE_DIR.is_dir():
    project_path = str(PROJECT_ROOT)
    if project_path not in sys.path:
        # Prepend so local sources shadow any env-installed similarly named pkgs.
        sys.path.insert(0, project_path)
