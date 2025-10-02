"""File type detection for ingestion stage.

Supported types (MVP):
    - .pdf  -> 'pdf'
    - .png/.jpg/.jpeg -> 'image'

Raises ValueError for unsupported extensions to enforce explicit design notes
before widening scope (Constitution: Supported Sources & Simplicity).
"""
from __future__ import annotations

from pathlib import Path

SUPPORTED_PDF = {".pdf"}
SUPPORTED_IMAGE = {".png", ".jpg", ".jpeg"}


def detect_file_type(name_or_path: str) -> str:
    """Return logical extractor token for a given filename/path.

    Parameters
    ----------
    name_or_path : str
        Filename or path string. Case-insensitive extension handling.

    Returns
    -------
    str
        'pdf' or 'image'.

    Raises
    ------
    ValueError
        If extension not in allowed set.
    """
    suffix = Path(name_or_path).suffix.lower()
    if suffix in SUPPORTED_PDF:
        return "pdf"
    if suffix in SUPPORTED_IMAGE:
        return "image"
    raise ValueError(f"Unsupported file type '{suffix}'. Allowed: PDF, PNG, JPG/JPEG")


__all__ = ["detect_file_type"]
