from pathlib import Path

try:
    from src.persistence.migrations import init_db  # type: ignore
except ImportError:
    init_db = None  # type: ignore

try:
    from src.reporting.templates import get_template_by_name, list_templates, save_template  # type: ignore
except ImportError:
    save_template = get_template_by_name = list_templates = None  # type: ignore


def test_template_save_and_load(tmp_path: Path):
    assert init_db is not None, "init_db missing (persistence)"
    assert save_template is not None, "save_template not implemented (Task 42 pending)"
    assert get_template_by_name is not None, "get_template_by_name not implemented (Task 42 pending)"
    assert list_templates is not None, "list_templates not implemented (Task 42 pending)"

    db_path = tmp_path / "tpl.db"
    init_db(str(db_path))

    definition = {
        "filters": {"date_from": "2025-01-01", "date_to": "2025-12-31"},
        "grouping": ["month"],
        "aggregations": [{"field": "amount_out", "func": "sum", "alias": "total_out"}],
    }

    tid = save_template(str(db_path), "Monthly Outflow", definition)
    assert isinstance(tid, int)

    loaded = get_template_by_name(str(db_path), "Monthly Outflow")
    assert loaded is not None, "Template not found after save"
    assert loaded["name"] == "Monthly Outflow"
    assert loaded["definition"] == definition

    # Idempotent save (same definition) should not create duplicate rows
    tid2 = save_template(str(db_path), "Monthly Outflow", definition)
    assert tid2 == tid, "Idempotent re-save should return same template_id"
    all_tpls = list_templates(str(db_path))
    assert len(all_tpls) == 1, f"Expected 1 template, found {len(all_tpls)}"

    # Update with changed definition should keep same ID but change definition
    new_def = {
        "filters": {"date_from": "2025-02-01", "date_to": "2025-12-31"},
        "grouping": ["month"],
        "aggregations": [{"field": "amount_out", "func": "sum", "alias": "total_out"}],
    }
    tid3 = save_template(str(db_path), "Monthly Outflow", new_def)
    assert tid3 == tid, "Updated template should keep same ID"
    loaded2 = get_template_by_name(str(db_path), "Monthly Outflow")
    assert loaded2["definition"] == new_def, "Definition not updated"


def test_template_not_found(tmp_path: Path):
    assert init_db is not None
    db_path = tmp_path / "tpl2.db"
    init_db(str(db_path))
    assert get_template_by_name is not None, "get_template_by_name not implemented (Task 42 pending)"
    missing = get_template_by_name(str(db_path), "Unknown")
    assert missing is None
