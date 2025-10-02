"""PDF extraction adapter using pdfplumber with graceful fallback.

Strategy:
 1. Attempt structured extraction via pdfplumber pages (extract_text per page).
 2. Split page text by newlines, strip blank lines → raw rows.
 3. On any exception, fallback to simple binary read + newline split.

Returns a list of dicts: [{"raw_text": <line>}, ...]
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Dict


def extract_raw_rows(path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    p = Path(path)
    try:
        import pdfplumber  # type: ignore

        with pdfplumber.open(p) as pdf:  # pragma: no cover - open mocked in tests
            for page in pdf.pages:
                try:
                    text = page.extract_text() or ""
                except Exception:
                    text = ""
                for line in text.splitlines():
                    line = line.strip()
                    if line:
                        rows.append({"raw_text": line})
    except Exception:
        # Fallback: naive newline split of file content (text mode decode best effort)
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            content = ""
        for line in content.splitlines():
            line = line.strip()
            if line:
                rows.append({"raw_text": line})
    return rows

__all__ = ["extract_raw_rows"]
