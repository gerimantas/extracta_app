import uuid
from pathlib import Path
import pytest
import hashlib

try:
    from src.persistence.migrations import init_db  # type: ignore
except ImportError:
    init_db = None  # type: ignore

try:
    from src.persistence.transactions_repository import bulk_insert_transactions, get_transactions  # type: ignore
except ImportError:
    bulk_insert_transactions = None  # type: ignore
    get_transactions = None  # type: ignore


def _sample_rows():
    rows = []
    base = {
        "transaction_date": "2025-01-15",
        "description": "Coffee",
        "amount_in": 0.0,
        "amount_out": 3.50,
        "counterparty": "Coffee",
        "category_id": None,
        "source_file": "statement.pdf",
        "source_file_hash": "a" * 64,
        "year": 2025,
        "month": "2025-01",
        "mapping_version": "v1",
        "logic_version": "0.1.0",
    }
    for i in range(2):
        rid = str(uuid.uuid4())
        nh = hashlib.sha256((rid + base["description"]).encode()).hexdigest()
        row = {"transaction_id": rid, "normalization_hash": nh, **base}
        if i == 1:  # second row different amount
            row["amount_out"] = 10.00
            row["description"] = "Groceries"
            row["counterparty"] = "Groceries"
            row["month"] = "2025-02"
            row["transaction_date"] = "2025-02-02"
            row["year"] = 2025
        rows.append(row)
    return rows


def test_bulk_insert_and_idempotency(tmp_path: Path):
    assert init_db is not None, "init_db missing (Task 32)"
    assert bulk_insert_transactions is not None, "bulk_insert_transactions not implemented (Task 34 pending)"
    assert get_transactions is not None, "get_transactions not implemented (Task 34 pending)"
    db_path = tmp_path / "tx.db"
    init_db(str(db_path))
    rows = _sample_rows()
    bulk_insert_transactions(str(db_path), rows)
    fetched = get_transactions(str(db_path))
    assert len(fetched) == 2, f"Expected 2 transactions, found {len(fetched)}"

    # Re-insert same rows -> idempotent (primary key conflict ignored)
    bulk_insert_transactions(str(db_path), rows)
    fetched2 = get_transactions(str(db_path))
    assert len(fetched2) == 2, "Duplicate insert should not create additional rows"
