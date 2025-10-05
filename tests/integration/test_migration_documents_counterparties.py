import os
import sqlite3
import tempfile
import sys
from pathlib import Path

# Ensure project root on path for direct test execution scenarios
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from extracta_app.src.persistence.migrations import init_db, CURRENT_SCHEMA_VERSION  # type: ignore


def table_exists(con: sqlite3.Connection, name: str) -> bool:
    cur = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    return cur.fetchone() is not None


def column_exists(con: sqlite3.Connection, table: str, column: str) -> bool:
    cur = con.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())


def test_migrations_add_documents_and_counterparties():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        # initial run
        init_db(db_path)
        con = sqlite3.connect(db_path)
        try:
            assert table_exists(con, "documents")
            assert table_exists(con, "counterparties")
            assert table_exists(con, "transactions")
            assert column_exists(con, "transactions", "counterparty_id")
            # schema version recorded
            cur = con.execute("SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1")
            ver = cur.fetchone()[0]
            assert ver == CURRENT_SCHEMA_VERSION
            # idempotent second run
            init_db(db_path)
            cur2 = con.execute("SELECT COUNT(*) FROM schema_version")
            count_rows = cur2.fetchone()[0]
            assert count_rows >= 1
        finally:
            con.close()
