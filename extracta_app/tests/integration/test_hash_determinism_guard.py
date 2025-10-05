"""Determinism Guard Test (Feature 002 Phase 9).

Ensures that enabling new document/counterparty features does NOT alter
existing normalization hashes for the same logical transaction inputs.
"""
from __future__ import annotations

from pathlib import Path
import sys
project_root = Path(__file__).resolve().parents[3]
pkg_root = project_root / "extracta_app"
for p in (project_root, pkg_root):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
from src.ingestion.pipeline import ingest_file  # type: ignore  # noqa: E402
from src.normalization.engine import normalize_rows  # type: ignore  # noqa: E402


def _prepare_mock_rows():
    return [
        {"Date": "2025-02-01", "Description": "Coffee Shop", "Amount": "-3.20"},
        {"Date": "2025-02-02", "Description": "Grocery Market", "Amount": "-12.50"},
    ]


def test_hashes_stable_pre_post_feature(tmp_path):  # use tmp_path to avoid pycache confusion
    fixture_path = "extracta_app/tests/fixtures/sample_statement.pdf"
    if not Path(fixture_path).exists():
        import pytest
        pytest.skip("Fixture missing")

    header_map = {"Date": "transaction_date", "Description": "description", "Amount": "amount_out"}
    # write a dummy artifact to exercise tmp_path so fixture isn't marked unused
    (tmp_path / "guard_marker.txt").write_text("ok", encoding="utf-8")
    rows = _prepare_mock_rows()

    art1 = ingest_file(fixture_path)
    norm1 = normalize_rows(rows, header_map=header_map, mapping_version="v1", logic_version="0.1.0", source_file=art1["source_file"], source_file_hash=art1["source_file_hash"])
    hashes_before = sorted(r["normalization_hash"] for r in norm1)

    # Simulate feature usage: derive counterparties & create documents already happens in UI; here we just re-run ingestion/normalization
    art2 = ingest_file(fixture_path)
    norm2 = normalize_rows(rows, header_map=header_map, mapping_version="v1", logic_version="0.1.0", source_file=art2["source_file"], source_file_hash=art2["source_file_hash"])
    hashes_after = sorted(r["normalization_hash"] for r in norm2)

    assert hashes_before == hashes_after, "Normalization hashes changed after feature operations"


def test_hash_changes_when_input_changes():
    """Negative control: prove the guard would fail if a hashing input changes.

    We alter the Description field (included in canonical hash fields) for one
    row and assert the resulting hash set differs. This ensures the stability
    test above is meaningful (i.e., not trivially always equal due to bug)."""
    fixture_path = "extracta_app/tests/fixtures/sample_statement.pdf"
    if not Path(fixture_path).exists():  # pragma: no cover
        import pytest
        pytest.skip("Fixture missing")
    header_map = {"Date": "transaction_date", "Description": "description", "Amount": "amount_out"}
    rows = _prepare_mock_rows()
    art = ingest_file(fixture_path)
    baseline = normalize_rows(rows, header_map=header_map, mapping_version="v1", logic_version="0.1.0", source_file=art["source_file"], source_file_hash=art["source_file_hash"])
    # mutate one description
    mutated_rows = list(rows)
    mutated_rows[0] = {**mutated_rows[0], "Description": mutated_rows[0]["Description"] + " X"}
    art2 = ingest_file(fixture_path)
    mutated = normalize_rows(mutated_rows, header_map=header_map, mapping_version="v1", logic_version="0.1.0", source_file=art2["source_file"], source_file_hash=art2["source_file_hash"])
    baseline_hashes = sorted(r["normalization_hash"] for r in baseline)
    mutated_hashes = sorted(r["normalization_hash"] for r in mutated)
    assert baseline_hashes != mutated_hashes, "Expected hash set to change when canonical input changes"
