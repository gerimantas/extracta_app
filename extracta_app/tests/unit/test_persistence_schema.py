import sqlite3
from pathlib import Path

# Task 31: Failing test first (no migrations implemented yet)
try:
    from src.persistence.migrations import init_db  # type: ignore
except ImportError:
    init_db = None  # type: ignore

REQUIRED_TABLES = {
    "transactions",
    "categories",
    "report_templates",
    "schema_version",
}


def _existing_tables(db_path: Path) -> set[str]:
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return {r[0] for r in cur.fetchall()}
    finally:
        con.close()


def test_init_db_creates_tables(tmp_path: Path):
    db_path = tmp_path / "test.db"
    # Assert function exists (will fail now until Task 32 implemented)
    assert init_db is not None, "init_db not implemented (Task 32 pending)"

    # Once implemented, call and verify tables
    init_db(str(db_path))  # type: ignore[misc]
    tables = _existing_tables(db_path)
    missing = REQUIRED_TABLES - tables
    assert not missing, f"Missing expected tables: {missing} (found: {tables})"

    # Optional: check a few critical columns of transactions
    con = sqlite3.connect(db_path)
    try:
        cur = con.execute("PRAGMA table_info(transactions)")
        cols = {row[1] for row in cur.fetchall()}
    finally:
        con.close()
    for col in [
        "transaction_id",
        "transaction_date",
        "amount_in",
        "amount_out",
        "normalization_hash",
    ]:
        assert col in cols, f"Column '{col}' missing in transactions table (have {cols})"
