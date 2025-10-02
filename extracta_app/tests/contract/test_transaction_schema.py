import json
from pathlib import Path

import jsonschema

SCHEMA_PATH = Path(__file__).parents[2] / 'contracts' / 'transaction.schema.json'


def load_schema():
    with SCHEMA_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)


def test_transaction_schema_minimal_valid():
    schema = load_schema()
    sample = {
        "transaction_id": "uuid-123",
        "transaction_date": "2025-01-15",
        "description": "Test row",
        "amount_in": 0,
        "amount_out": 10.5,
        "counterparty": "Test row",
        "source_file": "statement1.pdf",
        "source_file_hash": "a" * 64,
        "normalization_hash": "b" * 64,
        "mapping_version": "v1",
        "logic_version": "0.1.0",
        "year": 2025,
        "month": "2025-01",
        "created_at": "2025-10-02T12:00:00Z"
    }
    jsonschema.validate(instance=sample, schema=schema)


def test_transaction_schema_invalid_date():
    schema = load_schema()
    bad = {
        "transaction_id": "uuid-123",
        "transaction_date": "15-01-2025",  # wrong format
        "description": "Bad date",
        "amount_in": 0,
        "amount_out": 5,
        "counterparty": "Bad",
        "source_file": "statement1.pdf",
        "source_file_hash": "a" * 64,
        "normalization_hash": "b" * 64,
        "mapping_version": "v1",
        "logic_version": "0.1.0",
        "year": 2025,
        "month": "2025-01",
        "created_at": "2025-10-02T12:00:00Z"
    }
    try:
        jsonschema.validate(instance=bad, schema=schema)
    except jsonschema.ValidationError:
        return
    raise AssertionError('Expected validation error for invalid date format')


def test_transaction_schema_both_amounts_positive_disallowed():
    schema = load_schema()
    both = {
        "transaction_id": "uuid-123",
        "transaction_date": "2025-01-15",
        "description": "Both amounts",
        "amount_in": 10.0,
        "amount_out": 5.0,
        "counterparty": "X",
        "source_file": "statement1.pdf",
        "source_file_hash": "a" * 64,
        "normalization_hash": "b" * 64,
        "mapping_version": "v1",
        "logic_version": "0.1.0",
        "year": 2025,
        "month": "2025-01",
        "created_at": "2025-10-02T12:00:00Z"
    }
    try:
        jsonschema.validate(instance=both, schema=schema)
    except jsonschema.ValidationError:
        return
    raise AssertionError('Expected validation error when both amount_in and amount_out > 0')