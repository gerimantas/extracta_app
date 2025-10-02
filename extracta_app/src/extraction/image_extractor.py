"""Image OCR extraction adapter using pytesseract.

Pipeline:
 1. Open image with Pillow (convert to grayscale for consistency)
 2. Pass to pytesseract.image_to_string (lang='eng')
 3. Split lines; strip; discard blanks

Returns list of dicts with raw_text field.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Dict


def extract_raw_rows(path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    p = Path(path)
    try:
        from PIL import Image  # type: ignore
        import pytesseract  # type: ignore

        with Image.open(p) as img:  # pragma: no cover (IO mocked in tests)
            gray = img.convert("L")
            text = pytesseract.image_to_string(gray, lang="eng")
    except Exception:
        text = ""

    for line in text.splitlines():
        line = line.strip()
        if line:
            rows.append({"raw_text": line})
    return rows

__all__ = ["extract_raw_rows"]
