"""Categorization service (Task 36).

Provides CRUD operations for categories and assignment to transactions.

Rules:
 - Category names unique (case-sensitive for simplicity now).
 - Cannot delete a category while it is referenced by any transaction.
 - Renaming preserves ID; duplicate target name raises ValueError.
 - Assignment updates transaction.category_id.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List, Dict, Any


def _connect(db_path: str) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def create_category(db_path: str, name: str) -> int:
    if not name or not name.strip():
        raise ValueError("Category name required")
    con = _connect(db_path)
    try:
        # Check duplicate
        cur = con.execute("SELECT category_id FROM categories WHERE name=?", (name,))
        if cur.fetchone():
            raise ValueError(f"Category '{name}' already exists")
        cur = con.execute("INSERT INTO categories(name) VALUES (?)", (name,))
        con.commit()
        return int(cur.lastrowid)
    finally:
        con.close()


def list_categories(db_path: str) -> List[Dict[str, Any]]:
    con = _connect(db_path)
    try:
        cur = con.execute("SELECT category_id, name, created_at FROM categories ORDER BY name")
        return [
            {"category_id": r[0], "name": r[1], "created_at": r[2]} for r in cur.fetchall()
        ]
    finally:
        con.close()


def rename_category(db_path: str, category_id: int, new_name: str) -> None:
    if not new_name.strip():
        raise ValueError("New name empty")
    con = _connect(db_path)
    try:
        cur = con.execute("SELECT category_id FROM categories WHERE name=?", (new_name,))
        if cur.fetchone():
            raise ValueError(f"Category '{new_name}' already exists")
        updated = con.execute(
            "UPDATE categories SET name=? WHERE category_id=?", (new_name, category_id)
        )
        if updated.rowcount == 0:
            raise ValueError(f"Category {category_id} not found")
        con.commit()
    finally:
        con.close()


def assign_category(db_path: str, transaction_id: str, category_id: int) -> None:
    con = _connect(db_path)
    try:
        # Ensure category exists
        cur = con.execute("SELECT 1 FROM categories WHERE category_id=?", (category_id,))
        if not cur.fetchone():
            raise ValueError(f"Category {category_id} does not exist")
        updated = con.execute(
            "UPDATE transactions SET category_id=? WHERE transaction_id=?",
            (category_id, transaction_id),
        )
        if updated.rowcount == 0:
            raise ValueError(f"Transaction {transaction_id} not found")
        con.commit()
    finally:
        con.close()


def delete_category(db_path: str, category_id: int) -> None:
    con = _connect(db_path)
    try:
        # Check references
        cur = con.execute(
            "SELECT 1 FROM transactions WHERE category_id=? LIMIT 1", (category_id,)
        )
        if cur.fetchone():
            raise ValueError("Category in use; cannot delete")
        deleted = con.execute(
            "DELETE FROM categories WHERE category_id=?", (category_id,)
        )
        if deleted.rowcount == 0:
            raise ValueError(f"Category {category_id} not found")
        con.commit()
    finally:
        con.close()


__all__ = [
    "create_category",
    "list_categories",
    "rename_category",
    "assign_category",
    "delete_category",
]
