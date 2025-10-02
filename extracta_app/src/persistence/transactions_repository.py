"""Transactions repository (Task 34).

Provides append-only bulk insert + simple fetch APIs.
Idempotency: duplicate primary keys ignored (INSERT OR IGNORE).
"""
from __future__ import annotations

import sqlite3
from typing import Iterable, Dict, Any, List, Optional

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


def bulk_insert_transactions(db_path: str, rows: Iterable[Dict[str, Any]]) -> int:
    """Bulk insert rows; returns number of inserted (new) rows.

    Duplicate transaction_id rows are ignored.
    """
    rows_list = list(rows)
    if not rows_list:
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
        return cur.rowcount if cur.rowcount is not None else 0
    finally:
        con.close()


def get_transactions(db_path: str, *, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    sql = SELECT_BASE
    params: list[Any] = []
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute(sql, params)
        rows = cur.fetchall()
        result: List[Dict[str, Any]] = []
        for raw in rows:
            result.append({col: raw[i] for i, col in enumerate(TX_COLUMNS)})
        return result
    finally:
        con.close()

__all__ = ["bulk_insert_transactions", "get_transactions"]
