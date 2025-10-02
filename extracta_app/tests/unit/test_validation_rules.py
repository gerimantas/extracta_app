import pytest

try:
    from src.normalization.validation import validate_rows  # type: ignore
except ImportError:
    validate_rows = None  # type: ignore


def test_validation_non_empty_enforced():
    assert validate_rows is not None, "validate_rows not implemented (Task 26 pending)"
    with pytest.raises(ValueError):
        validate_rows([], required_columns=["Date", "Description", "Amount"])


def test_validation_required_columns():
    assert validate_rows is not None, "validate_rows not implemented (Task 26 pending)"
    rows = [{"Date": "2025-01-01", "Amount": "10"}]  # Missing Description
    with pytest.raises(ValueError):
        validate_rows(rows, required_columns=["Date", "Description", "Amount"])


def test_validation_date_fallback_formats():
    assert validate_rows is not None, "validate_rows not implemented (Task 26 pending)"
    rows = [
        {"Date": "2025-01-15", "Description": "ISO", "Amount": "10.00"},
        {"Date": "15/01/2025", "Description": "EU", "Amount": "-5.25"},
        {"Date": "01/16/2025", "Description": "US", "Amount": "0"},
    ]
    cleaned, anomalies = validate_rows(rows, required_columns=["Date", "Description", "Amount"])
    assert len(cleaned) == 3
    dates = [r["Date"] for r in cleaned]
    assert dates == ["2025-01-15", "2025-01-15", "2025-01-16"]
    # Negative amount allowed (soft anomaly only for zero value row?)
    assert any(a["type"] == "zero_amount" for a in anomalies)
