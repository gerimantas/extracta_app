"""Integration test for `document_delete` log event (Feature 002 Task 5.4)."""
from __future__ import annotations

import json
from pathlib import Path

from extracta_app.src.persistence.migrations import init_db
from extracta_app.src.persistence.documents_repository import create_document, delete_document_by_file_hash
from extracta_app.src.persistence.transactions_repository import bulk_insert_transactions


def test_document_delete_log_event(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(str(db_path))

    log_file = Path("logs/pipeline.log")
    if log_file.exists():
        log_file.unlink()

    # Create document + a couple of transactions referencing it
    file_hash = "hash_del_1"
    create_document(str(db_path), filename="to_delete.pdf", file_hash=file_hash, document_type="Other")
    rows = []
    for i in range(2):
        rows.append({
            "transaction_id": f"t{i}",
            "transaction_date": "2025-01-01",
            "description": f"Row {i}",
            "amount_in": 0.0,
            "amount_out": 1.0,
            "counterparty": None,
            "category_id": None,
            "source_file": "to_delete.pdf",
            "source_file_hash": file_hash,
            "normalization_hash": f"nh{i}",
            "year": 2025,
            "month": "2025-01",
            "mapping_version": "v1",
            "logic_version": "0.1.0",
        })
    bulk_insert_transactions(str(db_path), rows)

    removed = delete_document_by_file_hash(str(db_path), file_hash)
    assert removed == 2

    lines = [l.strip() for l in log_file.read_text(encoding="utf-8").splitlines() if l.strip()]
    events = [json.loads(l) for l in lines if 'document_delete' in l]
    assert events, "document_delete event missing"
    evt = events[0]
    for field in ["event", "file_hash", "removed_tx_count", "ts"]:
        assert field in evt
    assert evt["removed_tx_count"] == 2
    assert evt["event"] == "document_delete"
