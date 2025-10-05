"""(Deprecated) Previous counterparty management UI existence test.

Left in place but marked skipped because consolidated test now lives in
`test_ui_document_tab.py`. Keeping file (instead of deleting) preserves
historical context and avoids surprising test removals in active branch.
"""
from __future__ import annotations

import pytest


@pytest.mark.skip(reason="Consolidated into test_ui_document_tab.test_ui_section_functions_exposed")
def test_counterparty_management_section_exists_deprecated():
    pass

