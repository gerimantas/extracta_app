"""Integration test for counterparty derivation (Feature 002 Phase 4).

Steps:
 1. Initialize DB and insert a few normalized transactions (without counterparty).
 2. Run derivation function to assign counterparties using heuristic.
 3. Assert counterparties assigned or 'Unknown' for edge cases.
 4. Re-run derivation to ensure idempotency (no new counterparties or changes).
"""
from __future__ import annotations

import uuid
from pathlib import Path

from extracta_app.src.persistence.migrations import init_db
from extracta_app.src.persistence.transactions_repository import bulk_insert_transactions, get_transactions


def _make_tx(description: str, source_file: str, source_hash: str) -> dict:
    # Minimal required fields; amounts simplified
    return {
        "transaction_id": str(uuid.uuid4()),
        "transaction_date": "2025-01-01",
        "description": description,
        "amount_in": 0.0,
        "amount_out": 10.0,
        "counterparty": None,
        "category_id": None,
        "source_file": source_file,
        "source_file_hash": source_hash,
        "normalization_hash": str(uuid.uuid4()),  # stand-in; real pipeline would compute
        "year": 2025,
        "month": "2025-01",
        "mapping_version": "v1",
        "logic_version": "0.1.0",
    }


def test_counterparty_derivation_assigns_and_is_idempotent(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(str(db_path))

    rows = [
        _make_tx("PAYMENT TO ACME CORPORATION 12345", "a.pdf", "h1"),
        _make_tx("CARD PURCHASE - COFFEE SHOP 987", "a.pdf", "h1"),
        _make_tx("12345 678", "b.pdf", "h2"),  # numeric only -> Unknown
    ]
    bulk_insert_transactions(str(db_path), rows)

    # Import (will be implemented) derivation function
    from extracta_app.src.normalization.counterparty_derivation import derive_counterparties  # type: ignore

    first_result = derive_counterparties(str(db_path))
    assert first_result["assigned"] >= 2  # at least two non-Unknown
    tx_after = get_transactions(str(db_path))
    # Ensure counterparty column updated for first two
    cp_values = [t["counterparty"] for t in tx_after]
    assert any("Acme" in (c or "") for c in cp_values)
    assert any("Coffee" in (c or "") for c in cp_values)
    # Numeric only expects Unknown
    assert any(c is None or c == "Unknown" for c in cp_values)

    # Second run idempotent (no additional assignments beyond already set)
    second_result = derive_counterparties(str(db_path))
    assert second_result["assigned"] == 0
    assert second_result["skipped"] >= 1
