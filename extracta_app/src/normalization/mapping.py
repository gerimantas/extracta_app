"""Mapping of raw extracted rows to canonical transaction structure.

Handles both two-column (amount_in/amount_out) and single signed amount pattern.
For MVP we implement single signed amount logic when header_map provides generic 'amount' mapping.
"""
from __future__ import annotations

import uuid
from typing import Any


def _parse_float(val) -> float:
    try:
        return float(str(val).replace(",", "").strip())
    except Exception as exc:  # pragma: no cover (rare parsing anomaly)
        raise ValueError(f"Invalid numeric value: {val}") from exc


def map_row(raw: dict[str, Any], header_map: dict[str, str], *, source_file: str, source_file_hash: str) -> dict[str, Any] | None:
    # Must have date + description + either amount or amount_in/out
    if "Date" not in raw or "Description" not in raw:
        return None
    # Canonical base
    transaction_date = raw["Date"]
    description = raw["Description"]

    amount_in = 0.0
    amount_out = 0.0
    # Signed amount logic
    if "Amount" in raw:
        amt = _parse_float(raw["Amount"])
        if amt < 0:
            amount_out = abs(amt)
        elif amt > 0:
            amount_in = amt
        else:  # zero row skip? treat as info only
            amount_in = 0.0
            amount_out = 0.0
    else:
        # Future: handle separate columns e.g. Credit/Debit
        return None

    row = {
        "transaction_id": str(uuid.uuid4()),
        "transaction_date": transaction_date,
        "description": description,
        "amount_in": amount_in,
        "amount_out": amount_out,
        "counterparty": description,  # MVP pass-through
        "category_id": None,
        "source_file": source_file,
        "source_file_hash": source_file_hash,
    }
    return row

__all__ = ["map_row"]
