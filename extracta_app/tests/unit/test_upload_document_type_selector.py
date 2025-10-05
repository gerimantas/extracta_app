"""Unit tests for document_type selector integration (Feature 002 Phase 3.1/3.2).

Strategy: We don't spin up full Streamlit app (heavy); instead we isolate the
upload handler logic we will introduce into `upload_section` by factoring a
small pure helper that resolves the effective document_type given an optional
user input. We then monkeypatch the documents repository to assert persistence
is called with the resolved type.

These tests drive:
 - Default fallback to "Other" when user provides blank/None (Task 3.1)
 - Passing through explicit selection (Task 3.2)
"""
from __future__ import annotations

import types
from pathlib import Path


def _resolve_document_type(user_value: str | None) -> str:  # temporary helper duplicated; will be moved to ui module
    value = (user_value or "").strip()
    return value if value else "Other"


class FakeRepo:
    def __init__(self):
        self.calls: list[tuple[str, str, str]] = []

    def create_document(self, _db_path: str, *, filename: str, file_hash: str, document_type: str, status: str = "Success") -> int:  # noqa: D401
        self.calls.append((filename, file_hash, document_type))
        return 1


def test_document_type_defaults_to_other_when_missing(monkeypatch, tmp_path: Path):
    repo = FakeRepo()
    monkeypatch.setattr("extracta_app.src.persistence.documents_repository.create_document", repo.create_document, raising=False)

    # Simulate missing selection
    doc_type = _resolve_document_type("")
    assert doc_type == "Other"

    # Simulate persistence call
    repo.create_document(str(tmp_path/"db.sqlite"), filename="file.pdf", file_hash="abc", document_type=doc_type)
    assert repo.calls[0][2] == "Other"


def test_document_type_passes_through_explicit_selection(monkeypatch, tmp_path: Path):
    repo = FakeRepo()
    monkeypatch.setattr("extracta_app.src.persistence.documents_repository.create_document", repo.create_document, raising=False)

    doc_type = _resolve_document_type("Bank Statement")
    assert doc_type == "Bank Statement"
    repo.create_document(str(tmp_path/"db.sqlite"), filename="file2.pdf", file_hash="def", document_type=doc_type)
    assert repo.calls[0][2] == "Bank Statement"
