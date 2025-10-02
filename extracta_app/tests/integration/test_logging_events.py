"""
Integration test for logging events across pipeline stages.

Tests that each pipeline stage emits schema-valid log lines according to
the log-event.schema.json contract.
"""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import jsonschema

from src.ingestion.pipeline import ingest_file


class TestLoggingEvents:
    
    def test_pipeline_stages_emit_schema_valid_logs(self):
        """Test that each pipeline stage emits schema-valid log lines."""
        # Load log event schema
        schema_path = Path("contracts/log-event.schema.json")
        with open(schema_path) as f:
            log_schema = json.load(f)
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"dummy pdf content")
            tmp_path = tmp.name
        
        # Clear existing log file
        log_file = Path("logs/pipeline.log")
        if log_file.exists():
            log_file.unlink()
        
        try:
            # Run pipeline - this should create log entries
            ingest_file(tmp_path)
            
            # Read log events from actual log file
            log_events = []
            if log_file.exists():
                with open(log_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            log_events.append(json.loads(line.strip()))
            
            # Verify log events were captured
            assert len(log_events) > 0, "No log events were captured"
            
            # Verify each log event is schema-valid
            for log_event in log_events:
                jsonschema.validate(log_event, log_schema)
            
            # Verify expected pipeline stages are logged
            logged_stages = {event.get('stage') for event in log_events}
            expected_stages = {'ingestion'}
            
            assert expected_stages.issubset(logged_stages), f"Missing stages: {expected_stages - logged_stages}"
            
        finally:
            # Cleanup
            Path(tmp_path).unlink()
    
    def test_log_events_contain_required_fields(self):
        """Test that log events contain all required schema fields."""
        # Run the main test to verify logging integration works
        self.test_pipeline_stages_emit_schema_valid_logs()