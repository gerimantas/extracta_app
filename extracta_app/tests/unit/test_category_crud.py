from pathlib import Path
import uuid
import pytest

try:
    from src.persistence.migrations import init_db  # type: ignore
except ImportError:
    init_db = None  # type: ignore

try:
    from src.persistence.transactions_repository import bulk_insert_transactions, get_transactions  # type: ignore
except ImportError:
    bulk_insert_transactions = None  # type: ignore
    get_transactions = None  # type: ignore

try:
    from src.categorization.service import (
        create_category,
        list_categories,
        rename_category,
        assign_category,
        delete_category,
    )  # type: ignore
except ImportError:
    create_category = list_categories = rename_category = assign_category = delete_category = None  # type: ignore


def _sample_tx_rows():
    # minimal single transaction
    return [
        {
            "transaction_id": str(uuid.uuid4()),
            "transaction_date": "2025-01-10",
            "description": "Coffee",
            "amount_in": 0.0,
            "amount_out": 3.50,
            "counterparty": "Coffee",
            "category_id": None,
            "source_file": "statement.pdf",
            "source_file_hash": "a" * 64,
            "normalization_hash": str(uuid.uuid4()).replace("-", ""),
            "year": 2025,
            "month": "2025-01",
            "mapping_version": "v1",
            "logic_version": "0.1.0",
        }
    ]


def test_category_crud_and_assignment(tmp_path: Path):
    assert init_db is not None, "init_db missing (Task 32)"
    assert bulk_insert_transactions is not None, "transactions repo missing (Task 34)"
    # Existence checks for Task 35 (expected to fail before implementation of Task 36)
    assert create_category is not None, "create_category not implemented (Task 36 pending)"
    assert list_categories is not None, "list_categories not implemented (Task 36 pending)"
    assert rename_category is not None, "rename_category not implemented (Task 36 pending)"
    assert assign_category is not None, "assign_category not implemented (Task 36 pending)"
    assert delete_category is not None, "delete_category not implemented (Task 36 pending)"

    db_path = tmp_path / "cat.db"
    init_db(str(db_path))

    # Seed a transaction (category None)
    rows = _sample_tx_rows()
    bulk_insert_transactions(str(db_path), rows)
    tx_id = rows[0]["transaction_id"]

    # Create categories
    cat_food = create_category(str(db_path), "Food")
    cat_other = create_category(str(db_path), "Other")
    names = {c["name"] for c in list_categories(str(db_path))}
    assert {"Food", "Other"}.issubset(names)

    # Rename
    rename_category(str(db_path), cat_food, "Food & Drink")
    names2 = {c["name"] for c in list_categories(str(db_path))}
    assert "Food & Drink" in names2

    # Assign to transaction
    assign_category(str(db_path), tx_id, cat_food)
    tx_after = get_transactions(str(db_path))[0]
    assert tx_after["category_id"] == cat_food

    # Prevent delete if still referenced
    with pytest.raises(ValueError):
        delete_category(str(db_path), cat_food)

    # Reassign to other then delete
    assign_category(str(db_path), tx_id, cat_other)
    delete_category(str(db_path), cat_food)
    names3 = {c["name"] for c in list_categories(str(db_path))}
    assert "Food & Drink" not in names3

    # Duplicate name should raise
    with pytest.raises(ValueError):
        create_category(str(db_path), "Other")
