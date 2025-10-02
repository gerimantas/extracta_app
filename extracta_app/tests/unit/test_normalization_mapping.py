
try:
    from src.normalization.mapping import map_row  # type: ignore
except ImportError:
    map_row = None  # type: ignore


HEADER_MAP = {
    "Date": "transaction_date",
    "Description": "description",
    "Amount": "amount",  # single signed amount
}


def test_map_row_positive_amount_out():
    assert map_row is not None, "map_row not implemented (Task 28 pending)"
    raw = {"Date": "2025-01-15", "Description": "Coffee", "Amount": "-3.50"}
    mapped = map_row(raw, HEADER_MAP, source_file="statement.pdf", source_file_hash="h" * 64)
    assert mapped["amount_out"] == 3.50
    assert mapped["amount_in"] == 0


def test_map_row_negative_amount_in():
    assert map_row is not None, "map_row not implemented (Task 28 pending)"
    raw = {"Date": "2025-01-16", "Description": "Refund", "Amount": "12.00"}
    mapped = map_row(raw, HEADER_MAP, source_file="statement.pdf", source_file_hash="h" * 64)
    assert mapped["amount_in"] == 12.00
    assert mapped["amount_out"] == 0


def test_map_row_missing_field_returns_none():
    assert map_row is not None, "map_row not implemented (Task 28 pending)"
    raw = {"Description": "No date", "Amount": "5"}
    mapped = map_row(raw, HEADER_MAP, source_file="s.pdf", source_file_hash="h" * 64)
    assert mapped is None
