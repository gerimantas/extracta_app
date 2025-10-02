"""Report execution layer (Task 40).

Uses query_builder.build_report_query to produce SQL, executes against SQLite,
and returns dictionary with rows + metadata.
"""
from __future__ import annotations

import sqlite3
import time
from typing import Dict, Any

from src.reporting.query_builder import build_report_query
from src.logging.json_logger import emit_log_event


def execute_report(db_path: str, request: Dict[str, Any]) -> Dict[str, Any]:
    start_time = time.time()
    
    try:
        sql, params = build_report_query(request)
        con = sqlite3.connect(db_path)
        try:
            cur = con.execute(sql, params)
            columns = [d[0] for d in cur.description]
            rows = [dict(zip(columns, r)) for r in cur.fetchall()]
        finally:
            con.close()
        
        result = {
            "sql": sql,
            "params": params,
            "rows": rows,
            "row_count": len(rows),
        }
        
        # Log successful report execution
        emit_log_event({
            "stage": "reporting",
            "status": "success",
            "in_count": 1,
            "out_count": len(rows),
            "error_count": 0,
            "duration_ms": int((time.time() - start_time) * 1000)
        })
        
        return result
        
    except Exception as e:
        # Log failed report execution
        emit_log_event({
            "stage": "reporting",
            "status": "error",
            "in_count": 1,
            "out_count": 0,
            "error_count": 1,
            "duration_ms": int((time.time() - start_time) * 1000),
            "exception_type": type(e).__name__,
            "message": str(e)
        })
        raise

__all__ = ["execute_report"]
