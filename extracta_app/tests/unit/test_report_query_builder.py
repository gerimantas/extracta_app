import pytest

try:
    from src.reporting.query_builder import build_report_query  # type: ignore
except ImportError:
    build_report_query = None  # type: ignore


REQ_WITH_GROUP = {
    "filters": {
        "date_from": "2025-01-01",
        "date_to": "2025-03-31",
        "category_ids": [1, 2],
    },
    "grouping": ["month"],
    "aggregations": [
        {"field": "amount_out", "func": "sum", "alias": "total_out"},
    ],
}

REQ_NO_GROUP = {
    "filters": {
        "date_from": "2025-01-01",
        "date_to": "2025-01-31",
    },
    "grouping": [],
    "aggregations": [
        {"field": "amount_in", "func": "sum", "alias": "in_sum"},
        {"field": "amount_out", "func": "sum", "alias": "out_sum"},
        {"field": "transaction_id", "func": "count", "alias": "count_tx"},
    ],
}


def test_build_query_with_grouping():
    assert build_report_query is not None, "build_report_query not implemented (Task 38 pending)"
    sql, params = build_report_query(REQ_WITH_GROUP)
    # Basic structure expectations
    assert "SELECT month" in sql
    # Normalize case for assertion to avoid brittle case differences
    assert "sum(amount_out) as total_out" in sql.lower()
    assert "FROM transactions" in sql
    assert "GROUP BY month" in sql
    assert "ORDER BY month" in sql
    # Filters param order: date_from, date_to, category_ids...
    assert params[0] == REQ_WITH_GROUP["filters"]["date_from"]
    assert params[1] == REQ_WITH_GROUP["filters"]["date_to"]
    # Category IDs appear afterward
    assert set(params[2:]) == {1, 2}


def test_build_query_no_grouping():
    assert build_report_query is not None, "build_report_query not implemented (Task 38 pending)"
    sql, params = build_report_query(REQ_NO_GROUP)
    assert "GROUP BY" not in sql
    assert "SUM(amount_in) AS in_sum" in sql or "sum(amount_in) AS in_sum" in sql
    assert params[0] == REQ_NO_GROUP["filters"]["date_from"]
    assert params[1] == REQ_NO_GROUP["filters"]["date_to"]


def test_invalid_aggregation_func():
    assert build_report_query is not None, "build_report_query not implemented (Task 38 pending)"
    bad = {
        "filters": {},
        "grouping": [],
        "aggregations": [{"field": "amount_out", "func": "median", "alias": "m"}],
    }
    with pytest.raises(ValueError):
        build_report_query(bad)
