"""Report templates storage (Task 42).

Idempotent save semantics:
 - If name absent -> insert.
 - If name present and definition identical (JSON canonical) -> return existing id (no update).
 - If name present and definition differs -> update definition_json & updated_at, return id.
"""
from __future__ import annotations

import json
import sqlite3
from typing import Optional, Dict, Any, List


def _connect(db_path: str) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def _canonical_json(d: Dict[str, Any]) -> str:
    # Stable ordering & separators for deterministic comparison
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def save_template(db_path: str, name: str, definition: Dict[str, Any]) -> int:
    if not name.strip():
        raise ValueError("Template name required")
    cj = _canonical_json(definition)
    con = _connect(db_path)
    try:
        cur = con.execute(
            "SELECT template_id, definition_json FROM report_templates WHERE name=?",
            (name,),
        )
        row = cur.fetchone()
        if row is None:
            cur2 = con.execute(
                "INSERT INTO report_templates(name, definition_json) VALUES (?, ?)",
                (name, cj),
            )
            con.commit()
            return int(cur2.lastrowid)
        template_id, existing_json = row
        if existing_json == cj:
            return int(template_id)
        # Update existing
        con.execute(
            "UPDATE report_templates SET definition_json=?, updated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now') WHERE template_id=?",
            (cj, template_id),
        )
        con.commit()
        return int(template_id)
    finally:
        con.close()


def get_template_by_name(db_path: str, name: str) -> Optional[Dict[str, Any]]:
    con = _connect(db_path)
    try:
        cur = con.execute(
            "SELECT template_id, name, definition_json, created_at, updated_at FROM report_templates WHERE name=?",
            (name,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "template_id": row[0],
            "name": row[1],
            "definition": json.loads(row[2]),
            "created_at": row[3],
            "updated_at": row[4],
        }
    finally:
        con.close()


def list_templates(db_path: str) -> List[Dict[str, Any]]:
    con = _connect(db_path)
    try:
        cur = con.execute(
            "SELECT template_id, name, definition_json, created_at, updated_at FROM report_templates ORDER BY name"
        )
        out: List[Dict[str, Any]] = []
        for row in cur.fetchall():
            out.append(
                {
                    "template_id": row[0],
                    "name": row[1],
                    "definition": json.loads(row[2]),
                    "created_at": row[3],
                    "updated_at": row[4],
                }
            )
        return out
    finally:
        con.close()


__all__ = ["save_template", "get_template_by_name", "list_templates"]
