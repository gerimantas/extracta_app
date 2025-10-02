
try:
    from src.normalization.engine import normalize_rows  # type: ignore
except ImportError:
    normalize_rows = None  # type: ignore


HEADER_MAP = {
    "Date": "transaction_date",
    "Description": "description",
    "Amount": "amount",
}


RAW_ROWS = [
    {"Date": "2025-01-15", "Description": "Coffee", "Amount": "-3.50"},
    {"Date": "2025-01-16", "Description": "Refund", "Amount": "12.00"},
]


def test_normalize_rows_deterministic():
    assert normalize_rows is not None, "normalize_rows not implemented (Task 30 pending)"
    run1 = normalize_rows(
        RAW_ROWS,
        header_map=HEADER_MAP,
        mapping_version="v1",
        logic_version="0.1.0",
        source_file="statement.pdf",
        source_file_hash="a" * 64,
    )
    run2 = normalize_rows(
        RAW_ROWS,
        header_map=HEADER_MAP,
        mapping_version="v1",
        logic_version="0.1.0",
        source_file="statement.pdf",
        source_file_hash="a" * 64,
    )
    hashes1 = [r["normalization_hash"] for r in run1]
    hashes2 = [r["normalization_hash"] for r in run2]
    assert hashes1 == hashes2
    assert len(set(hashes1)) == len(hashes1)
