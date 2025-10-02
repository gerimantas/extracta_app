from pathlib import Path
import pytest
import hashlib

try:
    from src.ingestion.pipeline import ingest_file  # type: ignore
except ImportError:
    ingest_file = None  # type: ignore


def test_raw_artifact_pdf(monkeypatch, tmp_path: Path):
    assert ingest_file is not None, "ingestion pipeline not implemented (Task 24 pending)"
    f = tmp_path / "mini.pdf"
    f.write_bytes(b"%PDF-1.4 test content")

    # Monkeypatch pdf extractor to avoid real parsing
    import sys
    class DummyPDFExtractor:
        @staticmethod
        def extract_raw_rows(_path: str):
            return [{"raw_text": "R1"}, {"raw_text": "R2"}]
    if 'src.extraction.pdf_extractor' in sys.modules:
        monkeypatch.setattr(sys.modules['src.extraction.pdf_extractor'], 'extract_raw_rows', DummyPDFExtractor.extract_raw_rows)

    artifact = ingest_file(str(f))
    assert artifact['source_file'] == f.name
    assert artifact['extraction_method'] == 'pdf'
    assert artifact['record_count_raw'] == 2
    assert len(artifact['rows']) == 2
    expected_hash = hashlib.sha256(f.read_bytes()).hexdigest()
    assert artifact['source_file_hash'] == expected_hash
    assert 'extracted_at' in artifact


def test_raw_artifact_image(monkeypatch, tmp_path: Path):
    assert ingest_file is not None, "ingestion pipeline not implemented (Task 24 pending)"
    f = tmp_path / "mini.jpg"
    f.write_bytes(b"\xff\xd8\xff\xd9")
    import sys
    class DummyImgExtractor:
        @staticmethod
        def extract_raw_rows(_path: str):
            return [{"raw_text": "Only"}]
    if 'src.extraction.image_extractor' in sys.modules:
        monkeypatch.setattr(sys.modules['src.extraction.image_extractor'], 'extract_raw_rows', DummyImgExtractor.extract_raw_rows)
    artifact = ingest_file(str(f))
    assert artifact['extraction_method'] == 'image'
    assert artifact['record_count_raw'] == 1
    assert artifact['rows'][0]['raw_text'] == 'Only'
