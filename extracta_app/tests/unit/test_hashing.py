import hashlib
from pathlib import Path

try:
    from src.common.hashing import file_sha256, normalization_hash  # type: ignore
except ImportError:  # Module not yet implemented (Task 12) or path issue
    file_sha256 = None  # type: ignore
    normalization_hash = None  # type: ignore


def test_file_sha256_deterministic(tmp_path: Path):
    test_file = tmp_path / "sample.txt"
    content = b"abc\n"
    test_file.write_bytes(content)
    expected = hashlib.sha256(content).hexdigest()
    assert file_sha256 is not None, "file_sha256 not implemented (Task 12 pending)"
    assert file_sha256(str(test_file)) == expected


def test_normalization_hash_ordering():
    """Ensures the normalization hash uses the documented canonical ordering and numeric formatting.

    Ordering (from data-model.md):
    [transaction_date, description, amount_in, amount_out, counterparty, source_file, source_file_hash, year, month] + mapping_version + logic_version
    Numeric formatting: two decimal places.
    """
    assert normalization_hash is not None, "normalization_hash not implemented (Task 12 pending)"
    row = {
        "transaction_date": "2025-01-15",
        "description": "Coffee",
        "amount_in": 0.0,
        "amount_out": 3.5,
        "counterparty": "Coffee",
        "source_file": "statement_jan.pdf",
        "source_file_hash": "a" * 64,
        "year": 2025,
        "month": "2025-01",
    }
    mapping_version = "v1"
    logic_version = "0.1.0"

    base = "|".join([
        row["transaction_date"],
        row["description"],
        f"{row['amount_in']:.2f}",
        f"{row['amount_out']:.2f}",
        row["counterparty"],
        row["source_file"],
        row["source_file_hash"],
        str(row["year"]),
        row["month"],
    ]) + f"|{mapping_version}|{logic_version}"
    expected = hashlib.sha256(base.encode("utf-8")).hexdigest()
    actual = normalization_hash(row, mapping_version, logic_version)
    assert actual == expected, (
        "Normalization hash mismatch: expected canonical ordering or formatting not applied.\n"
        f"Expected: {expected}\nActual:   {actual}\nBase String: {base}"
    )


def test_normalization_hash_numeric_formatting():
    """Changing raw float representation should not affect hash: formatting must normalize to two decimals."""
    assert normalization_hash is not None, "normalization_hash not implemented (Task 12 pending)"
    row_a = {
        "transaction_date": "2025-01-15",
        "description": "Rounded",
        "amount_in": 0.0,
        "amount_out": 3.5,  # 3.50
        "counterparty": "Rounded",
        "source_file": "statement_jan.pdf",
        "source_file_hash": "b" * 64,
        "year": 2025,
        "month": "2025-01",
    }
    row_b = dict(row_a)
    row_b["amount_out"] = 3.5000000001  # same to two decimals
    mapping_version = "v1"
    logic_version = "0.1.0"
    h_a = normalization_hash(row_a, mapping_version, logic_version)
    h_b = normalization_hash(row_b, mapping_version, logic_version)
    assert h_a == h_b, "Hashes differ due to improper numeric normalization (should be identical)."
