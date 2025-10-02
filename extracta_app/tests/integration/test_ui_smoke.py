"""UI smoke test (Task 43).

Simplified test that verifies UI module can be imported and basic structure exists.
"""
import sys
from unittest.mock import MagicMock

# Mock streamlit completely
sys.modules['streamlit'] = MagicMock()

try:
    from src.ui.app import main as app_main  # type: ignore
except ImportError:
    app_main = None  # type: ignore


def test_ui_app_import():
    """Test that UI app module can be imported successfully."""
    assert app_main is not None, "UI app not implemented (Task 44 pending)"

    # Verify it's a callable function
    assert callable(app_main), "app_main should be a callable function"


def test_ui_app_has_expected_sections():
    """Test that UI app contains expected section functions."""
    assert app_main is not None, "UI app not implemented (Task 44 pending)"

    # Import the module to check its contents
    from src.ui import app

    # Check that key functions exist
    expected_functions = ['upload_section', 'transactions_section', 'reports_section', 'templates_section']

    for func_name in expected_functions:
        assert hasattr(app, func_name), f"Missing {func_name} function in UI app"
        assert callable(getattr(app, func_name)), f"{func_name} should be callable"
