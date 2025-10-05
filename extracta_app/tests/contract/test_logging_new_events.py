"""Contract test for new logging events introduced in Feature 002 (Phase 8).

Validates presence and basic field sets (not exhaustive ordering) for:
 - document_create
 - document_delete
 - counterparty_merge
 - counterparty_rename
 - counterparty_autoderive_fail
"""
from __future__ import annotations

import json
from pathlib import Path

from extracta_app.src.persistence.migrations import init_db
from extracta_app.src.persistence.documents_repository import create_document, delete_document_by_file_hash
from extracta_app.src.persistence.counterparties_repository import get_or_create, rename, merge
from extracta_app.src.normalization.counterparty_derivation import derive_counterparties
from extracta_app.src.persistence.transactions_repository import bulk_insert_transactions


def _read_events() -> list[dict]:
    log_file = Path("logs/pipeline.log")
    if not log_file.exists():
        return []
    out = []
    for line in log_file.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def test_new_event_types_and_fields(tmp_path):
    db_path = tmp_path / "events.db"
    init_db(str(db_path))
    log_file = Path("logs/pipeline.log")
    if log_file.exists():
        log_file.unlink()

    # document_create
    create_document(str(db_path), filename="d1.pdf", file_hash="fh1", document_type="Other")

    # Prepare transactions for autoderive fail (numeric only) and a good one
    rows = [
        {
            "transaction_id": "t1",
            "transaction_date": "2025-01-01",
            "description": "123 456",
            "amount_in": 0.0,
            "amount_out": 1.0,
            "counterparty": None,
            "category_id": None,
            "source_file": "d1.pdf",
            "source_file_hash": "fh1",
            "normalization_hash": "nh1",
            "year": 2025,
            "month": "2025-01",
            "mapping_version": "v1",
            "logic_version": "0.1.0",
        },
        {
            "transaction_id": "t2",
            "transaction_date": "2025-01-01",
            "description": "PAYMENT TO ALPHA LLC",
            "amount_in": 0.0,
            "amount_out": 2.0,
            "counterparty": None,
            "category_id": None,
            "source_file": "d1.pdf",
            "source_file_hash": "fh1",
            "normalization_hash": "nh2",
            "year": 2025,
            "month": "2025-01",
            "mapping_version": "v1",
            "logic_version": "0.1.0",
        },
    ]
    bulk_insert_transactions(str(db_path), rows)
    derive_counterparties(str(db_path))  # produces autoderive fail for t1

    # create two counterparties to test rename and merge
    cp1 = get_or_create(str(db_path), display_name="Alpha Llc", normalized="alpha llc")
    cp2 = get_or_create(str(db_path), display_name="Beta Inc", normalized="beta inc")
    rename(str(db_path), counterparty_id=cp2, new_display_name="Beta Incorporated")
    merge(str(db_path), winner_id=cp1, losing_ids=[cp2])

    # document_delete
    delete_document_by_file_hash(str(db_path), "fh1")

    events = _read_events()
    kinds = {e.get("event") for e in events}
    expected = {"document_create", "counterparty_autoderive_fail", "counterparty_rename", "counterparty_merge", "document_delete"}
    missing = expected - kinds
    assert not missing, f"Missing events: {missing}"

    # Basic field presence checks
    def _assert_fields(evt_name: str, required: set[str]):
        found = [e for e in events if e.get("event") == evt_name]
        assert found, f"No event lines for {evt_name}"
        for f in required:
            assert f in found[0], f"Missing field {f} in {evt_name}"

    _assert_fields("document_create", {"filename", "file_hash", "document_type", "status", "ts"})
    _assert_fields("counterparty_autoderive_fail", {"transaction_id", "reason", "ts"})
    _assert_fields("counterparty_rename", {"counterparty_id", "new_name", "ts"})
    _assert_fields("counterparty_merge", {"winner_id", "losing_ids", "reassigned_tx_count", "ts"})
    _assert_fields("document_delete", {"file_hash", "removed_tx_count", "ts"})
