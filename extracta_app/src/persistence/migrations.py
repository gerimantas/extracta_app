"""Database migrations / initialization.

Phase 0 (schema version 1) tables:
    - transactions
    - categories
    - report_templates
    - schema_version

Schema version 2 additions (Feature 002):
    - documents (file metadata + classification)
    - counterparties (canonical counterparty names)
    - transactions.counterparty_id column (nullable; FK logical relation)
    - Backfill documents from existing transactions distinct (source_file, source_file_hash)

Design Principles:
 - Idempotent: safe to call multiple times.
 - Forward-only: version increments, no downgrade path (append-only philosophy).
 - Deterministic: no non-deterministic default values beyond timestamp convenience.
"""
from __future__ import annotations

import sqlite3
from typing import Iterable
from pathlib import Path

CURRENT_SCHEMA_VERSION = 2  # bump when new structural elements added
CURRENT_APP_VERSION = "0.1.0"

BASE_DDL: list[str] = [
    # transactions table: append-only (v1)
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
    # categories table (v1)
    """CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
    );""",
    # report templates (v1)
    """CREATE TABLE IF NOT EXISTS report_templates (
        template_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        definition_json TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
        updated_at TEXT
    );""",
    # schema version (v1)
    """CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER NOT NULL,
        app_version TEXT NOT NULL,
        applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
    );""",
]

# v2 new tables
V2_DDL: list[str] = [
    """CREATE TABLE IF NOT EXISTS documents (
        document_id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        file_hash TEXT NOT NULL UNIQUE,
        upload_date TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
        status TEXT NOT NULL DEFAULT 'Success',
        document_type TEXT NOT NULL DEFAULT 'Other',
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
    );""",
    """CREATE TABLE IF NOT EXISTS counterparties (
        counterparty_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        name_normalized TEXT NOT NULL UNIQUE,
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
    );""",
]


def _table_columns(con: sqlite3.Connection, table: str) -> set[str]:
    cur = con.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cur.fetchall()}


def _add_counterparty_id_column(con: sqlite3.Connection) -> None:
    if "counterparty_id" not in _table_columns(con, "transactions"):
        con.execute("ALTER TABLE transactions ADD COLUMN counterparty_id INTEGER")


def _backfill_documents(con: sqlite3.Connection) -> None:
    """Populate documents table for existing transactions if empty.

    Backfill rule: For each distinct (source_file, source_file_hash) create a documents row
    status=Success, document_type=Other. Only runs if documents has zero rows.
    """
    # ensure table exists
    con.execute("CREATE TABLE IF NOT EXISTS documents (document_id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT NOT NULL, file_hash TEXT NOT NULL UNIQUE, upload_date TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')), status TEXT NOT NULL DEFAULT 'Success', document_type TEXT NOT NULL DEFAULT 'Other', created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')))")
    cur = con.execute("SELECT COUNT(1) FROM documents")
    if cur.fetchone()[0] != 0:
        return
    # gather distinct
    cur = con.execute("SELECT DISTINCT source_file, source_file_hash FROM transactions")
    rows: Iterable[tuple[str, str]] = cur.fetchall()
    for filename, file_hash in rows:
        if file_hash:
            con.execute(
                "INSERT OR IGNORE INTO documents(filename, file_hash, status, document_type) VALUES (?,?, 'Success','Other')",
                (filename, file_hash),
            )


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
        # create base schema
        for ddl in BASE_DDL:
            con.execute(ddl)
        # read current version
        cur = con.execute("SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1")
        row = cur.fetchone()
        existing_version = row[0] if row else 0
        # apply v2 if needed
        if existing_version < 2:
            for ddl in V2_DDL:
                con.execute(ddl)
            _add_counterparty_id_column(con)
            _backfill_documents(con)
        _ensure_version_row(con)
        con.commit()
    finally:
        con.close()

__all__ = ["init_db", "CURRENT_SCHEMA_VERSION"]
