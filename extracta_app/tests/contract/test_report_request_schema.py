import json
from pathlib import Path

import jsonschema

SCHEMA_PATH = Path(__file__).parents[2] / 'contracts' / 'report-request.schema.json'


def load_schema():
    with SCHEMA_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)


def base_request():
    return {
        "filters": {
            "date_range": {"start": "2025-01-01", "end": "2025-02-01"},
            "transaction_type": "expense",
            "categories": [],
            "counterparty": ""
        },
        "grouping": ["category_id", "month"],
        "aggregation": {"field": "amount_out", "func": "sum"},
        "view_mode": "table"
    }


def test_report_request_valid():
    schema = load_schema()
    jsonschema.validate(instance=base_request(), schema=schema)


def test_report_request_invalid_agg_func():
    schema = load_schema()
    bad = base_request()
    bad["aggregation"]["func"] = "median"
    try:
        jsonschema.validate(instance=bad, schema=schema)
    except jsonschema.ValidationError:
        return
    raise AssertionError('Expected validation error for unsupported aggregation func "median"')


def test_report_request_invalid_missing_required_field():
    schema = load_schema()
    bad = base_request()
    del bad['filters']['date_range']
    try:
        jsonschema.validate(instance=bad, schema=schema)
    except jsonschema.ValidationError:
        return
    raise AssertionError('Expected validation error for missing date_range')