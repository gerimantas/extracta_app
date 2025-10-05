import os
import tempfile
import sqlite3
import uuid

from extracta_app.src.persistence.migrations import init_db
from extracta_app.src.persistence import documents_repository as docs_repo  # type: ignore
from extracta_app.src.persistence import counterparties_repository as cp_repo  # type: ignore
from extracta_app.src.persistence.transactions_repository import bulk_insert_transactions


def _txn_row(file_name: str, file_hash: str, amount_in=0.0, amount_out=10.0):
    return {
        "transaction_id": str(uuid.uuid4()),
        "transaction_date": "2025-10-04",
        "description": "CARD PAYMENT RIMI LIETUVA",
        "amount_in": amount_in,
        "amount_out": amount_out,
        "counterparty": "RIMI",
        "category_id": None,
        "source_file": file_name,
        "source_file_hash": file_hash,
        "normalization_hash": str(uuid.uuid4()),
        "year": 2025,
        "month": "2025-10",
        "mapping_version": "0.1.0",
        "logic_version": "0.1.0",
    }


def test_documents_create_list_and_delete_cascade():
    with tempfile.TemporaryDirectory() as tmp:
        db = os.path.join(tmp, "test.db")
        init_db(db)
        fh = "hashA"
        # Insert transactions referencing file hash
        bulk_insert_transactions(db, [_txn_row("fileA.pdf", fh) for _ in range(3)])
        # Backfill may have created document; ensure listing or create
        docs_before = docs_repo.list_documents(db)
        if not any(d["file_hash"] == fh for d in docs_before):
            docs_repo.create_document(db, filename="fileA.pdf", file_hash=fh, document_type="Bank Statement")
        # Verify list
        docs = docs_repo.list_documents(db)
        assert any(d["file_hash"] == fh for d in docs)
        # Delete and cascade
        removed = docs_repo.delete_document_by_file_hash(db, fh)
        assert removed == 3
        # Transactions gone
        con = sqlite3.connect(db)
        try:
            cur = con.execute("SELECT COUNT(*) FROM transactions WHERE source_file_hash=?", (fh,))
            assert cur.fetchone()[0] == 0
        finally:
            con.close()


def test_counterparties_get_or_create_case_insensitive_and_merge():
    with tempfile.TemporaryDirectory() as tmp:
        db = os.path.join(tmp, "test.db")
        init_db(db)
        id1 = cp_repo.get_or_create(db, display_name="Rimi", normalized="rimi")
        id2 = cp_repo.get_or_create(db, display_name="RIMI", normalized="rimi")
        assert id1 == id2
        # Create second variant
        id3 = cp_repo.get_or_create(db, display_name="Rimi Lietuva", normalized="rimi lietuva")
        # Attach transactions to both
        bulk_insert_transactions(db, [_txn_row("f.pdf", "h1"), _txn_row("g.pdf", "h2")])
        con = sqlite3.connect(db)
        try:
            con.execute("UPDATE transactions SET counterparty_id=? WHERE rowid % 2=0", (id1,))
            con.execute("UPDATE transactions SET counterparty_id=? WHERE rowid % 2=1", (id3,))
            con.commit()
        finally:
            con.close()
        reassigned = cp_repo.merge(db, winner_id=id1, losing_ids=[id3])
        assert reassigned > 0
        # Losing id removed
        all_rows = cp_repo.list_counterparties(db)
        losing_ids_present = [r for r in all_rows if r["counterparty_id"] == id3]
        assert not losing_ids_present

        # Edge case: merging again with already removed id -> no effect
        reassigned_second = cp_repo.merge(db, winner_id=id1, losing_ids=[id3])
        assert reassigned_second == 0


def test_counterparties_rename_and_conflict():
    with tempfile.TemporaryDirectory() as tmp:
        db = os.path.join(tmp, "test.db")
        init_db(db)
        _a = cp_repo.get_or_create(db, display_name="Alpha Corp", normalized="alpha corp")
        b = cp_repo.get_or_create(db, display_name="Beta", normalized="beta")
        # Rename without conflict
        cp_repo.rename(db, counterparty_id=b, new_display_name="Beta Ltd")
        # Create explicit conflict
        c = cp_repo.get_or_create(db, display_name="Gamma", normalized="gamma")
        # Attempt rename gamma -> alpha corp (normalized clash with existing alpha corp)
        try:
            cp_repo.rename(db, counterparty_id=c, new_display_name="Alpha Corp")
        except cp_repo.RenameCollisionError:
            pass
        else:
            raise AssertionError("Expected RenameCollisionError not raised")
