"""Database migrations / initialization (Task 32).

Creates required SQLite tables idempotently:
  - transactions
  - categories
  - report_templates
  - schema_version

Design Notes:
 - Simple "if not exists" DDL; no complex migration graph yet.
 - A schema_version table stores an integer + semver text for future upgrades.
 - Keep logic minimal to honor simplicity principle; more advanced migrations can wrap this later.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

CURRENT_SCHEMA_VERSION = 1
CURRENT_APP_VERSION = "0.1.0"

DDL_STATEMENTS: list[str] = [
    # transactions table: append-only
    """CREATE TABLE IF NOT EXISTS transactions (
        transaction_id TEXT PRIMARY KEY,
        transaction_date TEXT NOT NULL,
        description TEXT NOT NULL,
        amount_in REAL NOT NULL DEFAULT 0.0,
        amount_out REAL NOT NULL DEFAULT 0.0,
        counterparty TEXT,
        category_id INTEGER,
        source_file TEXT NOT NULL,
        source_file_hash TEXT NOT NULL,
        normalization_hash TEXT NOT NULL,
        year INTEGER NOT NULL,
        month TEXT NOT NULL,
        mapping_version TEXT,
        logic_version TEXT
    );""",
    # categories table
    """CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
    );""",
    # report templates
    """CREATE TABLE IF NOT EXISTS report_templates (
        template_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        definition_json TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
        updated_at TEXT
    );""",
    # schema version
    """CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER NOT NULL,
        app_version TEXT NOT NULL,
        applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
    );""",
]


def _ensure_version_row(con: sqlite3.Connection) -> None:
    cur = con.execute("SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1")
    row = cur.fetchone()
    if row is None or row[0] < CURRENT_SCHEMA_VERSION:
        con.execute(
            "INSERT INTO schema_version(version, app_version) VALUES (?, ?)",
            (CURRENT_SCHEMA_VERSION, CURRENT_APP_VERSION),
        )


def init_db(db_path: str) -> None:
    """Create required tables if absent and record schema version.

    Safe to call multiple times; uses IF NOT EXISTS DDL and version check.
    """
    p = Path(db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p)
    try:
        for ddl in DDL_STATEMENTS:
            con.execute(ddl)
        _ensure_version_row(con)
        con.commit()
    finally:
        con.close()

__all__ = ["init_db", "CURRENT_SCHEMA_VERSION"]
