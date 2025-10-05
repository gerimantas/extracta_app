"""Counterparties repository (Feature 002).

Supports canonical counterparty creation, rename, merge.
"""
from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Sequence

from extracta_app.src.logging.json_logger import emit_log_event


class RenameCollisionError(RuntimeError):
    """Raised when attempting to rename to an existing normalized name."""


def get_or_create(db_path: str, *, display_name: str, normalized: str) -> int:
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute("SELECT counterparty_id FROM counterparties WHERE name_normalized=?", (normalized,))
        row = cur.fetchone()
        if row:
            return int(row[0])
        con.execute(
            "INSERT INTO counterparties(name, name_normalized) VALUES (?, ?)",
            (display_name, normalized),
        )
        con.commit()
        cur2 = con.execute("SELECT counterparty_id FROM counterparties WHERE name_normalized=?", (normalized,))
        return int(cur2.fetchone()[0])
    finally:
        con.close()


def list_counterparties(db_path: str) -> List[Dict[str, Any]]:
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute(
            "SELECT counterparty_id, name, name_normalized, created_at FROM counterparties ORDER BY name"
        )
        return [
            {
                "counterparty_id": r[0],
                "name": r[1],
                "name_normalized": r[2],
                "created_at": r[3],
            }
            for r in cur.fetchall()
        ]
    finally:
        con.close()


def rename(db_path: str, *, counterparty_id: int, new_display_name: str) -> None:
    normalized = new_display_name.lower()
    con = sqlite3.connect(db_path)
    try:
        # Collision check
        cur = con.execute(
            "SELECT counterparty_id FROM counterparties WHERE name_normalized=?", (normalized,)
        )
        row = cur.fetchone()
        if row and int(row[0]) != counterparty_id:
            raise RenameCollisionError(f"Name collision for {normalized}")
        con.execute(
            "UPDATE counterparties SET name=?, name_normalized=? WHERE counterparty_id=?",
            (new_display_name, normalized, counterparty_id),
        )
        con.commit()
        emit_log_event({
            "event": "counterparty_rename",
            "counterparty_id": counterparty_id,
            "new_name": new_display_name,
        })
    finally:
        con.close()


def merge(db_path: str, *, winner_id: int, losing_ids: Sequence[int]) -> int:
    if not losing_ids:
        return 0
    con = sqlite3.connect(db_path)
    try:
        reassigned_total = 0
        for losing in losing_ids:
            if losing == winner_id:
                continue
            cur = con.execute(
                "UPDATE transactions SET counterparty_id=? WHERE counterparty_id=?",
                (winner_id, losing),
            )
            reassigned = cur.rowcount or 0
            reassigned_total += reassigned
            con.execute(
                "DELETE FROM counterparties WHERE counterparty_id=?", (losing,)
            )
        con.commit()
        emit_log_event({
            "event": "counterparty_merge",
            "winner_id": winner_id,
            "losing_ids": list(losing_ids),
            "reassigned_tx_count": reassigned_total,
        })
        return reassigned_total
    finally:
        con.close()


__all__ = [
    "get_or_create",
    "list_counterparties",
    "rename",
    "merge",
    "RenameCollisionError",
]
