"""Normalization engine orchestrating validation, mapping, and hash computation."""
from __future__ import annotations

import time
from typing import Any

from src.common.hashing import normalization_hash
from src.logging.json_logger import emit_log_event
from src.normalization.mapping import map_row
from src.normalization.validation import validate_rows


def normalize_rows(
    raw_rows: list[dict[str, Any]],
    *,
    header_map: dict[str, str],
    mapping_version: str,
    logic_version: str,
    source_file: str,
    source_file_hash: str,
) -> list[dict[str, Any]]:
    start_time = time.time()

    try:
        validated, anomalies = validate_rows(raw_rows, required_columns=["Date", "Description", "Amount"])

        # Log validation stage
        emit_log_event({
            "stage": "validation",
            "status": "success",
            "in_count": len(raw_rows),
            "out_count": len(validated),
            "error_count": len(anomalies),
            "duration_ms": int((time.time() - start_time) * 500),  # Partial time
            "source_file": source_file
        })

        normalized: list[dict[str, Any]] = []
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

        # Log normalization stage
        emit_log_event({
            "stage": "normalization",
            "status": "success",
            "in_count": len(validated),
            "out_count": len(normalized),
            "error_count": 0,
            "duration_ms": int((time.time() - start_time) * 1000),
            "source_file": source_file
        })

        # Sort normalized results by normalization_hash for deterministic ordering
        normalized.sort(key=lambda x: x["normalization_hash"])

        return normalized

    except Exception as e:
        # Log failed normalization
        emit_log_event({
            "stage": "normalization",
            "status": "error",
            "in_count": len(raw_rows),
            "out_count": 0,
            "error_count": 1,
            "duration_ms": int((time.time() - start_time) * 1000),
            "source_file": source_file,
            "exception_type": type(e).__name__,
            "message": str(e)
        })
        raise

__all__ = ["normalize_rows"]
