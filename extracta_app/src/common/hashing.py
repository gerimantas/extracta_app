"""Hashing utilities ensuring deterministic, reproducible identifiers.

Adheres to Constitution Principles:
- Data Integrity & Determinism: Stable SHA256 hashing for file bytes and
  normalization hash over canonical ordered fields.
- Simplicity: Pure functions, no side effects or global state.

Functions:
    file_sha256(path: str) -> str
        Stream file bytes and return lowercase hex SHA256 digest.
    normalization_hash(row: dict, mapping_version: str, logic_version: str) -> str
        Build canonical string per data-model specification and return SHA256.

The canonical ordering MUST remain synchronized with `data-model.md`. Any change
requires bumping NORMALIZATION_LOGIC_VERSION (handled elsewhere) and updating
tests that assert determinism.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Iterable

CHUNK_SIZE = 8192

# Canonical field order (excluding mapping_version & logic_version which are appended)
CANONICAL_FIELDS: tuple[str, ...] = (
    "transaction_date",
    "description",
    "amount_in",
    "amount_out",
    "counterparty",
    "source_file",
    "source_file_hash",
    "year",
    "month",
)


def file_sha256(path: str) -> str:
    """Return SHA256 hex digest of file at `path`.

    Reads in chunks to avoid large memory usage for big files (1GB scale).
    """
    h = sha256()
    with open(path, "rb") as f:  # noqa: PTH123 (intentional direct open)
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def _format_numeric(value: float) -> str:
    """Format numeric values to two decimal places for hash stability."""
    return f"{float(value):.2f}"


def _coerce_value(key: str, value) -> str:
    """Coerce a value to its canonical string representation.

    Amount fields enforce 2-decimal formatting; year coerces to int string; other
    fields use raw string conversion.
    """
    if key in ("amount_in", "amount_out"):
        return _format_numeric(value)
    if key == "year":
        return str(int(value))
    return str(value)


def _build_canonical_segments(row: dict) -> Iterable[str]:
    for field in CANONICAL_FIELDS:
        if field not in row:
            raise KeyError(f"Missing required field '{field}' for normalization hash")
        yield _coerce_value(field, row[field])


def normalization_hash(row: dict, mapping_version: str, logic_version: str) -> str:
    """Compute deterministic SHA256 over canonical ordered field values + versions.

    Parameters
    ----------
    row : dict
        Dictionary containing at least the CANONICAL_FIELDS.
    mapping_version : str
        Version identifier from YAML mappings (included for provenance).
    logic_version : str
        Application constant representing transformation logic version.
    """
    if not mapping_version:
        raise ValueError("mapping_version must be non-empty")
    if not logic_version:
        raise ValueError("logic_version must be non-empty")

    segments = list(_build_canonical_segments(row))
    base = "|".join(segments + [mapping_version, logic_version])
    return sha256(base.encode("utf-8")).hexdigest()


__all__ = ["file_sha256", "normalization_hash", "CANONICAL_FIELDS"]
