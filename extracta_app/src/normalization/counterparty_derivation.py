"""Counterparty derivation batch process (Feature 002 Phase 4).

Scans transactions lacking a meaningful counterparty value and applies the
deterministic heuristic to populate the `counterparty` column. Idempotent:
already populated rows are skipped. Returns stats for observability.
"""
from __future__ import annotations

import sqlite3
from typing import Any, Dict

from .counterparty_heuristic import extract_counterparty_name
from src.logging.json_logger import emit_log_event
from src.persistence.counterparties_repository import get_or_create


def derive_counterparties(db_path: str) -> Dict[str, Any]:
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute(
            "SELECT transaction_id, description, counterparty, counterparty_id FROM transactions"
        )
        rows = cur.fetchall()
        to_update: list[tuple[str, int | None, str]] = []  # (counterparty, counterparty_id, transaction_id)
        skipped = 0
        for tx_id, desc, existing, _existing_id in rows:
            if existing not in (None, "", "Unknown"):
                skipped += 1
                continue
            name = extract_counterparty_name(desc or "")
            if name == "Unknown" and existing in (None, "", "Unknown"):
                skipped += 1
                emit_log_event({
                    "event": "counterparty_autoderive_fail",
                    "transaction_id": tx_id,
                    "reason": "heuristic_unknown"
                })
                continue
            if name != existing:
                cp_id = get_or_create(db_path, display_name=name, normalized=name.lower())
                to_update.append((name, cp_id, tx_id))
        for cp, cp_id, tid in to_update:
            con.execute(
                "UPDATE transactions SET counterparty=?, counterparty_id=? WHERE transaction_id=?",
                (cp, cp_id, tid),
            )
        con.commit()
        return {"scanned": len(rows), "assigned": len(to_update), "skipped": skipped}
    finally:
        con.close()

__all__ = ["derive_counterparties"]
