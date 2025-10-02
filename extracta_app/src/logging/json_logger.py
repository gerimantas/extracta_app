"""JSON line logger with schema alignment, rotation, and stack truncation.

Avoids shadowing stdlib logging usage by being explicitly imported via
`from src.logging.json_logger import JsonLogger`.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


def emit_log_event(event_data: Dict[str, Any]) -> None:
    """Emit a log event using the default logger instance."""
    logger = JsonLogger(Path("logs/pipeline.log"))
    logger.emit(event_data)


@dataclass
class JsonLogger:
    path: Path
    rotation_bytes: int = 10_000_000  # 10MB default
    stack_lines: int = 20

    def __post_init__(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: Dict[str, Any]) -> None:
        evt = dict(event)  # shallow copy
        # Auto timestamp if missing
        evt.setdefault("ts", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        # Truncate stack excerpt if present
        if isinstance(evt.get("stack_excerpt"), str) and self.stack_lines > 0:
            lines = evt["stack_excerpt"].splitlines()
            if len(lines) > self.stack_lines:
                evt["stack_excerpt"] = "\n".join(lines[: self.stack_lines])
        line = json.dumps(evt, separators=(",", ":"), ensure_ascii=False)
        self._rotate_if_needed(len(line) + 1)  # + newline
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    # Simple size-based single-level rotation
    def _rotate_if_needed(self, incoming_len: int) -> None:
        try:
            if self.path.exists() and self.path.stat().st_size + incoming_len > self.rotation_bytes:
                # rename to .1 (overwrite previous)
                rotated = self.path.with_suffix(self.path.suffix + ".1")
                if rotated.exists():
                    rotated.unlink()
                self.path.rename(rotated)
        except OSError:
            # Fail silently; logging should not break pipeline
            pass

__all__ = ["JsonLogger"]
