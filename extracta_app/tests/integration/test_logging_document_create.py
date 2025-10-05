"""Integration test for `document_create` log event (Feature 002 Task 3.3).

We simulate creation of a document metadata record via repository to assert
that the JSON log line contains required fields.
"""
from __future__ import annotations

import json
from pathlib import Path

from extracta_app.src.persistence.migrations import init_db
from extracta_app.src.persistence.documents_repository import create_document


def test_document_create_log_event(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(str(db_path))

    log_file = Path("logs/pipeline.log")
    if log_file.exists():
        log_file.unlink()

    create_document(str(db_path), filename="sample.pdf", file_hash="hash123", document_type="Purchase Receipt")

    assert log_file.exists(), "Log file not created"
    lines = [l.strip() for l in log_file.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert lines, "No log lines captured"

    # Find our document_create event
    events = [json.loads(l) for l in lines if 'document_create' in l]
    assert events, "document_create event not found"
    evt = events[0]
    # Required fields
    for field in ["event", "filename", "file_hash", "document_type", "status", "ts"]:
        assert field in evt, f"Missing field {field}"
    assert evt["event"] == "document_create"
    assert evt["document_type"] == "Purchase Receipt"
