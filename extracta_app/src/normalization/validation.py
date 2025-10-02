"""Row-level validation prior to normalization mapping.

Provides a single entrypoint `validate_rows` that:
 1. Ensures non-empty input.
 2. Verifies required columns are present in each row.
 3. Normalizes date formats with fallback parsing (ISO, EU dd/mm/YYYY, US mm/dd/YYYY).
 4. Collects soft anomalies (zero amount rows) instead of failing.

Returns (cleaned_rows, anomalies_list).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]


def _normalize_date(value: str) -> str:
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {value}")


def validate_rows(rows: list[dict[str, Any]], required_columns: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not rows:
        raise ValueError("No rows extracted (empty input)")
    missing_cols = set(required_columns)
    cleaned: list[dict[str, Any]] = []
    anomalies: list[dict[str, Any]] = []
    for r in rows:
        if any(col not in r for col in required_columns):
            raise ValueError(f"Missing required columns in row: {r}")
        # Date normalization
        r = dict(r)
        r[required_columns[0]] = _normalize_date(r[required_columns[0]])
        # Soft anomaly: zero amount row (if Amount column present and zero)
        amount_col = None
        for c in ("Amount", "amount", "AMOUNT"):
            if c in r:
                amount_col = c
                break
        if amount_col and str(r[amount_col]).strip() in ("0", "0.0", "0.00"):
            anomalies.append({"type": "zero_amount", "row": r})
        cleaned.append(r)
        missing_cols -= {c for c in required_columns if c in r}
    if missing_cols:
        # If any column missing globally (should already be caught per-row)
        raise ValueError(f"Required columns missing: {missing_cols}")
    return cleaned, anomalies

__all__ = ["validate_rows"]
