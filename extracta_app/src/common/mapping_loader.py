"""Mapping configuration loader for normalization header resolution.

Resolution order (highest precedence first):
1. File-specific overrides (pattern match)
2. Explicit rules mapping (case-insensitive exact header key)
3. Synonym lists (case-insensitive membership)

If no match: return None for that header.
"""
from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass
class MappingConfig:
    version: str
    synonyms: Dict[str, List[str]]  # canonical -> synonym list
    rules: Dict[str, str]  # original header -> canonical
    file_overrides: List[dict]


def load_mapping_config(path: Path) -> MappingConfig:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    version = data.get("version")
    if not version:
        raise ValueError("Mapping config missing required 'version'")
    synonyms = data.get("synonyms", {}) or {}
    rules = data.get("rules", {}) or {}
    file_overrides = data.get("file_overrides", []) or []
    return MappingConfig(version=version, synonyms=synonyms, rules=rules, file_overrides=file_overrides)


def _build_synonym_lookup(cfg: MappingConfig) -> Dict[str, str]:
    lookup: Dict[str, str] = {}
    for canonical, syns in cfg.synonyms.items():
        for s in syns:
            lookup[s.lower()] = canonical
    return lookup


def resolve_headers(headers: List[str], source_file: str, config: MappingConfig) -> Dict[str, Optional[str]]:
    """Resolve a list of headers to canonical names using precedence rules."""
    result: Dict[str, Optional[str]] = {h: None for h in headers}
    lower_rules = {k.lower(): v for k, v in config.rules.items()}
    synonym_lookup = _build_synonym_lookup(config)

    # 1. File overrides
    for entry in config.file_overrides:
        pattern = entry.get("pattern")
        if pattern and fnmatch(source_file, pattern):
            for hdr, canonical in (entry.get("headers") or {}).items():
                for original in headers:
                    if original.lower() == hdr.lower():
                        result[original] = canonical

    # 2. Rules (if not already set)
    for original in headers:
        if result[original] is None:
            key = original.lower()
            if key in lower_rules:
                result[original] = lower_rules[key]

    # 3. Synonyms
    for original in headers:
        if result[original] is None:
            val = synonym_lookup.get(original.lower())
            if val:
                result[original] = val

    return result


__all__ = ["MappingConfig", "load_mapping_config", "resolve_headers"]
