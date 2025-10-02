import json
from pathlib import Path

import jsonschema

SCHEMA_PATH = Path(__file__).parents[2] / 'contracts' / 'log-event.schema.json'


def load_schema():
    with SCHEMA_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)


def test_log_event_valid():
    schema = load_schema()
    evt = {
        "ts": "2025-10-02T12:00:00Z",
        "stage": "normalization",
        "status": "success",
        "in_count": 10,
        "out_count": 10,
        "error_count": 0,
        "duration_ms": 123
    }
    jsonschema.validate(instance=evt, schema=schema)


def test_log_event_negative_counts_invalid():
    schema = load_schema()
    bad = {
        "ts": "2025-10-02T12:00:00Z",
        "stage": "extraction",
        "status": "success",
        "in_count": -1,
        "out_count": 10,
        "error_count": 0,
        "duration_ms": 10
    }
    try:
        jsonschema.validate(instance=bad, schema=schema)
    except jsonschema.ValidationError:
        return
    raise AssertionError('Expected validation error for negative in_count')