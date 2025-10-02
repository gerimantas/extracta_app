"""Report execution layer (Task 40).

Uses query_builder.build_report_query to produce SQL, executes against SQLite,
and returns dictionary with rows + metadata.
"""
from __future__ import annotations

import sqlite3
from typing import Dict, Any

from src.reporting.query_builder import build_report_query


def execute_report(db_path: str, request: Dict[str, Any]) -> Dict[str, Any]:
    sql, params = build_report_query(request)
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute(sql, params)
        columns = [d[0] for d in cur.description]
        rows = [dict(zip(columns, r)) for r in cur.fetchall()]
    finally:
        con.close()
    return {
        "sql": sql,
        "params": params,
        "rows": rows,
        "row_count": len(rows),
    }

__all__ = ["execute_report"]
