from pathlib import Path
import pytest

try:
    from src.extraction.image_extractor import extract_raw_rows  # type: ignore
except ImportError:
    extract_raw_rows = None  # type: ignore


def test_image_extractor_basic(monkeypatch, tmp_path: Path):
    assert extract_raw_rows is not None, "image_extractor not implemented (Task 22 pending)"
    img_path = tmp_path / "sample.png"
    # minimal png header bytes to satisfy Pillow if used (we may not open due to mocking)
    img_path.write_bytes(b"\x89PNG\r\n\x1a\n")

    # Monkeypatch pytesseract.image_to_string to return predictable lines
    import sys
    class DummyPT:
        @staticmethod
        def image_to_string(_img, lang='eng'):
            return "Alpha\nBeta\n\nGamma"
    if 'pytesseract' not in sys.modules:
        sys.modules['pytesseract'] = DummyPT()
    else:
        monkeypatch.setattr(sys.modules['pytesseract'], 'image_to_string', DummyPT.image_to_string)

    rows = extract_raw_rows(str(img_path))
    assert len(rows) == 3
    assert rows[0]['raw_text'] == 'Alpha'
    assert rows[1]['raw_text'] == 'Beta'
    assert rows[2]['raw_text'] == 'Gamma'


def test_image_extractor_empty(monkeypatch, tmp_path: Path):
    assert extract_raw_rows is not None, "image_extractor not implemented (Task 22 pending)"
    img_path = tmp_path / "empty.jpg"
    img_path.write_bytes(b"\xff\xd8\xff\xd9")  # minimal jpeg
    import sys
    class DummyPT2:
        @staticmethod
        def image_to_string(_img, lang='eng'):
            return "   \n  "
    if 'pytesseract' not in sys.modules:
        sys.modules['pytesseract'] = DummyPT2()
    else:
        monkeypatch.setattr(sys.modules['pytesseract'], 'image_to_string', DummyPT2.image_to_string)
    rows = extract_raw_rows(str(img_path))
    assert rows == []
