import uuid
from pathlib import Path

try:
    from src.persistence.migrations import init_db  # type: ignore
except ImportError:
    init_db = None  # type: ignore

try:
    from src.persistence.transactions_repository import bulk_insert_transactions  # type: ignore
except ImportError:
    bulk_insert_transactions = None  # type: ignore

try:
    from src.reporting.executor import execute_report  # type: ignore
except ImportError:
    execute_report = None  # type: ignore

# Reuse request shape similar to query builder tests


def _tx(tx_date: str, amount_out: float) -> dict:
    tid = str(uuid.uuid4())
    return {
        "transaction_id": tid,
        "transaction_date": tx_date,
        "description": f"D-{tx_date}",
        "amount_in": 0.0,
        "amount_out": amount_out,
        "counterparty": f"C-{tx_date}",
        "category_id": None,
        "source_file": "seed.pdf",
        "source_file_hash": "a" * 64,
        "normalization_hash": tid.replace("-", ""),
        "year": int(tx_date[:4]),
        "month": tx_date[:7],
        "mapping_version": "v1",
        "logic_version": "0.1.0",
    }


def _seed(db_path: Path):
    rows = [
        _tx("2025-01-05", 10.0),
        _tx("2025-01-10", 5.0),
        _tx("2025-02-01", 7.0),
    ]
    bulk_insert_transactions(str(db_path), rows)


def test_execute_report_grouped(tmp_path: Path):
    assert init_db is not None
    assert bulk_insert_transactions is not None
    assert execute_report is not None, "execute_report not implemented (Task 40 pending)"
    db_path = tmp_path / "r.db"
    init_db(str(db_path))
    _seed(db_path)

    request = {
        "filters": {"date_from": "2025-01-01", "date_to": "2025-12-31"},
        "grouping": ["month"],
        "aggregations": [
            {"field": "amount_out", "func": "sum", "alias": "total_out"},
        ],
    }
    result = execute_report(str(db_path), request)
    rows = result["rows"]
    # Expect two months
    assert len(rows) == 2
    by_month = {r["month"]: r["total_out"] for r in rows}
    assert by_month["2025-01"] == 15.0
    assert by_month["2025-02"] == 7.0


def test_execute_report_no_group(tmp_path: Path):
    assert execute_report is not None, "execute_report not implemented (Task 40 pending)"
    db_path = tmp_path / "r2.db"
    init_db(str(db_path))
    _seed(db_path)
    request = {
        "filters": {"date_from": "2025-01-01", "date_to": "2025-03-01"},
        "grouping": [],
        "aggregations": [
            {"field": "amount_out", "func": "sum", "alias": "out_sum"},
        ],
    }
    result = execute_report(str(db_path), request)
    rows = result["rows"]
    assert len(rows) == 1
    assert rows[0]["out_sum"] == 22.0
