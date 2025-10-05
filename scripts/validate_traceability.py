"""Validate that all task IDs from feature task lists appear at least once in traceability.md.

Exit codes:
 0 - all good
 1 - missing IDs
 2 - traceability file not found or other IO error

Usage:
  python scripts/validate_traceability.py

Optional env:
  TRACEABILITY_PATH (default: ./traceability.md)
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Iterable

# Known task file paths (extend if more features added)
TASK_FILES = [
    Path("extracta_app/specs/extracta-core/tasks.md"),
    Path("specs/002-advanced-document-and/tasks.md"),
]

TASK_ID_PATTERN = re.compile(r"^(\d+\.\d+)")


def iter_task_ids(path: Path) -> Iterable[str]:
    if not path.exists():
        return []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = TASK_ID_PATTERN.match(line.strip())
        if m:
            yield m.group(1)


def main() -> int:
    traceability_path = Path(os.getenv("TRACEABILITY_PATH", "traceability.md"))
    if not traceability_path.exists():
        print(f"ERROR: traceability file not found: {traceability_path}")
        return 2

    trace_text = traceability_path.read_text(encoding="utf-8")

    missing_total: list[str] = []
    all_ids: list[str] = []
    for task_file in TASK_FILES:
        ids = list(iter_task_ids(task_file))
        all_ids.extend(ids)
        for tid in ids:
            if tid not in trace_text:
                missing_total.append(tid)

    if missing_total:
        print("TRACEABILITY CHECK FAILED")
        print("Missing task IDs (not found in traceability.md):")
        for tid in sorted(missing_total):
            print(f" - {tid}")
        print(f"Total missing: {len(missing_total)} / {len(set(all_ids))}")
        return 1

    print("TRACEABILITY CHECK OK - all task IDs present.")
    print(f"Total task IDs validated: {len(set(all_ids))}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
