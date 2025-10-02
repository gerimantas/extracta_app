from types import SimpleNamespace
from pathlib import Path
import pytest

try:
    from src.extraction.pdf_extractor import extract_raw_rows  # type: ignore
except ImportError:
    extract_raw_rows = None  # type: ignore


class DummyPage:
    def __init__(self, text: str):
        self._text = text

    def extract_text(self):  # pdfplumber API compatibility
        return self._text


def test_pdf_extractor_basic(monkeypatch, tmp_path: Path):
    assert extract_raw_rows is not None, "pdf_extractor not implemented (Task 20 pending)"

    # Create dummy pdf bytes file (content irrelevant due to monkeypatch)
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 dummy")

    class DummyPDF:
        pages = [DummyPage("Row One\nRow Two"), DummyPage("Row Three")]  # two pages

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def dummy_open(path):  # noqa: D401
        return DummyPDF()

    import sys
    if 'pdfplumber' not in sys.modules:
        sys.modules['pdfplumber'] = SimpleNamespace(open=dummy_open)
    else:
        monkeypatch.setattr(sys.modules['pdfplumber'], 'open', dummy_open)

    rows = extract_raw_rows(str(pdf_path))
    assert isinstance(rows, list)
    assert len(rows) == 3
    assert all('raw_text' in r for r in rows)


def test_pdf_extractor_fallback_text(monkeypatch, tmp_path: Path):
    assert extract_raw_rows is not None, "pdf_extractor not implemented (Task 20 pending)"
    pdf_path = tmp_path / "fallback.pdf"
    pdf_path.write_text("LineA\nLineB")

    # Force pdfplumber.open to raise to trigger fallback
    import sys
    def raising_open(path):  # noqa: D401
        raise RuntimeError('fail')
    if 'pdfplumber' not in sys.modules:
        sys.modules['pdfplumber'] = SimpleNamespace(open=raising_open)
    else:
        monkeypatch.setattr(sys.modules['pdfplumber'], 'open', raising_open)

    rows = extract_raw_rows(str(pdf_path))
    # Fallback should split lines
    assert len(rows) == 2
    assert rows[0]['raw_text'] == 'LineA'
