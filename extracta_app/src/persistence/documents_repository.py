"""Documents repository (Feature 002).

Provides CRUD style operations for documents table introduced in schema v2.
Deletion cascades (manually) all transactions referencing the file hash.
"""
from __future__ import annotations

import sqlite3
from typing import Any, List, Dict

from extracta_app.src.logging.json_logger import emit_log_event


def create_document(db_path: str, *, filename: str, file_hash: str, document_type: str, status: str = "Success") -> int:
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute(
            """
            INSERT OR IGNORE INTO documents(filename, file_hash, document_type, status)
            VALUES (?,?,?,?)
            """,
            (filename, file_hash, document_type, status),
        )
        con.commit()
        if cur.rowcount:
            emit_log_event({
                "event": "document_create",
                "filename": filename,
                "file_hash": file_hash,
                "document_type": document_type,
                "status": status
            })
        # fetch id
        cur2 = con.execute("SELECT document_id FROM documents WHERE file_hash=?", (file_hash,))
        row = cur2.fetchone()
        return int(row[0]) if row else -1
    finally:
        con.close()


def list_documents(db_path: str) -> List[Dict[str, Any]]:
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute(
            "SELECT document_id, filename, file_hash, upload_date, status, document_type FROM documents ORDER BY upload_date DESC"
        )
        rows = cur.fetchall()
        return [
            {
                "document_id": r[0],
                "filename": r[1],
                "file_hash": r[2],
                "upload_date": r[3],
                "status": r[4],
                "document_type": r[5],
            }
            for r in rows
        ]
    finally:
        con.close()


def delete_document_by_file_hash(db_path: str, file_hash: str) -> int:
    """Delete document and all transactions referencing it.

    Returns number of removed transactions.
    """
    con = sqlite3.connect(db_path)
    try:
        cur_cnt = con.execute(
            "SELECT COUNT(*) FROM transactions WHERE source_file_hash=?", (file_hash,)
        )
        tx_count = int(cur_cnt.fetchone()[0])
        con.execute("DELETE FROM transactions WHERE source_file_hash=?", (file_hash,))
        con.execute("DELETE FROM documents WHERE file_hash=?", (file_hash,))
        con.commit()
        emit_log_event({
            "event": "document_delete",
            "file_hash": file_hash,
            "removed_tx_count": tx_count,
        })
        return tx_count
    finally:
        con.close()


__all__ = [
    "create_document",
    "list_documents",
    "delete_document_by_file_hash",
]
