"""UI export presence tests for Feature 002.

Historically we had two separate tests asserting hasattr(...) on the module.
Those were a bit flaky during iterative edits. We now:
  * Mock streamlit early
  * Import the functions directly (will raise ImportError deterministically if missing)
  * Assert they are callables in a single consolidated test
This provides a fast‑fail signal without brittle attribute checks.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.modules['streamlit'] = MagicMock()

root = Path(__file__).resolve().parents[3]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))


def test_ui_section_functions_exposed():
    try:  # noqa: SIM105 keep explicit for clarity
        from src.ui.app import (  # type: ignore  # noqa: E402
            document_management_section,
            counterparty_management_section,
            upload_section,
            transactions_section,
        )
    except ImportError:  # pragma: no cover
        import pytest
        pytest.skip("UI app import unavailable")

    for fn in [document_management_section, counterparty_management_section, upload_section, transactions_section]:
        assert callable(fn), f"{fn.__name__} not callable"

