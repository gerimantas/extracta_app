"""Ingestion pipeline orchestrating file hashing, type detection, and raw extraction.

Produces a raw artifact dict:
{
  source_file, source_file_hash, extraction_method, extracted_at, record_count_raw, rows: [...]
}
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Dict, Any

from src.ingestion.router import detect_file_type
# Import extractor modules (not symbols) so tests can monkeypatch their
# public functions via sys.modules lookups before calling ingest_file.
from src.extraction import pdf_extractor, image_extractor  # type: ignore


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:  # pragma: no cover (small; integration tested)
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def ingest_file(path_str: str) -> Dict[str, Any]:
    path = Path(path_str)
    if not path.exists():  # early safety
        raise FileNotFoundError(path)
    file_type = detect_file_type(path.name)
    if file_type == "pdf":
        rows = pdf_extractor.extract_raw_rows(str(path))  # type: ignore[attr-defined]
        method = "pdf"
    else:
        rows = image_extractor.extract_raw_rows(str(path))  # type: ignore[attr-defined]
        method = "image"
    artifact = {
        "source_file": path.name,
        "source_file_hash": _file_sha256(path),
        "extraction_method": method,
        "extracted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "record_count_raw": len(rows),
        "rows": rows,
    }
    return artifact

__all__ = ["ingest_file"]
