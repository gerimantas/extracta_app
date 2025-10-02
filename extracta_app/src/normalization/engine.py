"""Normalization engine orchestrating validation, mapping, and hash computation."""
from __future__ import annotations

from typing import List, Dict, Any
from datetime import datetime

from src.normalization.validation import validate_rows
from src.normalization.mapping import map_row
from src.common.hashing import normalization_hash


def normalize_rows(
    raw_rows: List[Dict[str, Any]],
    *,
    header_map: Dict[str, str],
    mapping_version: str,
    logic_version: str,
    source_file: str,
    source_file_hash: str,
) -> List[Dict[str, Any]]:
    validated, anomalies = validate_rows(raw_rows, required_columns=["Date", "Description", "Amount"])
    # anomalies currently unused; could be logged later
    normalized: List[Dict[str, Any]] = []
    for raw in validated:
        mapped = map_row(raw, header_map, source_file=source_file, source_file_hash=source_file_hash)
        if not mapped:
            continue
        # Derive year & month
        date_str = mapped["transaction_date"]
        year = int(date_str[:4])
        month = date_str[:7]
        mapped.update({
            "year": year,
            "month": month,
            "mapping_version": mapping_version,
            "logic_version": logic_version,
        })
        mapped["normalization_hash"] = normalization_hash(
            mapped,
            mapping_version=mapping_version,
            logic_version=logic_version,
        )
        normalized.append(mapped)
    return normalized

__all__ = ["normalize_rows"]
