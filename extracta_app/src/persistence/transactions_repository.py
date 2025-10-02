"""Transactions repository (Task 34).

Provides append-only bulk insert + simple fetch APIs.
Idempotency: duplicate primary keys ignored (INSERT OR IGNORE).
"""
from __future__ import annotations

import sqlite3
import time
from collections.abc import Iterable
from typing import Any

from src.logging.json_logger import emit_log_event

TX_COLUMNS = [
    "transaction_id",
    "transaction_date",
    "description",
    "amount_in",
    "amount_out",
    "counterparty",
    "category_id",
    "source_file",
    "source_file_hash",
    "normalization_hash",
    "year",
    "month",
    "mapping_version",
    "logic_version",
]

INSERT_SQL = (
    "INSERT OR IGNORE INTO transactions (" + ",".join(TX_COLUMNS) + ") VALUES (" + ",".join(["?"] * len(TX_COLUMNS)) + ")"
)

SELECT_BASE = "SELECT " + ",".join(TX_COLUMNS) + " FROM transactions"


def bulk_insert_transactions(db_path: str, rows: Iterable[dict[str, Any]]) -> int:
    """Bulk insert rows; returns number of inserted (new) rows.

    Duplicate transaction_id rows are ignored.
    """
    start_time = time.time()
    rows_list = list(rows)

    try:
        if not rows_list:
            # Log empty persistence
            emit_log_event({
                "stage": "persistence",
                "status": "success",
                "in_count": 0,
                "out_count": 0,
                "error_count": 0,
                "duration_ms": int((time.time() - start_time) * 1000)
            })
            return 0

        con = sqlite3.connect(db_path)
        try:
            cur = con.executemany(
                INSERT_SQL,
                [
                    [
                        r.get(col) for col in TX_COLUMNS
                    ]
                    for r in rows_list
                ],
            )
            con.commit()
            inserted_count = cur.rowcount if cur.rowcount is not None else 0

            # Log successful persistence
            emit_log_event({
                "stage": "persistence",
                "status": "success",
                "in_count": len(rows_list),
                "out_count": inserted_count,
                "error_count": 0,
                "duration_ms": int((time.time() - start_time) * 1000)
            })

            return inserted_count
        finally:
            con.close()

    except Exception as e:
        # Log failed persistence
        emit_log_event({
            "stage": "persistence",
            "status": "error",
            "in_count": len(rows_list) if rows_list else 0,
            "out_count": 0,
            "error_count": 1,
            "duration_ms": int((time.time() - start_time) * 1000),
            "exception_type": type(e).__name__,
            "message": str(e)
        })
        raise


def get_transactions(db_path: str, *, limit: int | None = None) -> list[dict[str, Any]]:
    sql = SELECT_BASE
    params: list[Any] = []
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute(sql, params)
        rows = cur.fetchall()
        result: list[dict[str, Any]] = []
        for raw in rows:
            result.append({col: raw[i] for i, col in enumerate(TX_COLUMNS)})
        return result
    finally:
        con.close()

__all__ = ["bulk_insert_transactions", "get_transactions"]
