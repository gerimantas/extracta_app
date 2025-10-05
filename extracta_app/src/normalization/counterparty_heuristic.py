"""Deterministic counterparty extraction heuristic (Feature 002).

Functions:
  extract_counterparty_name(description: str) -> str
  get_or_create_counterparty_id(repo_get_or_create, description: str) -> int

Design: Pure string transformations; no external calls; stable ordering.
"""
from __future__ import annotations

import re
from typing import Callable

_STOPWORDS = {"payment", "transfer", "to", "from", "card", "visa", "mastercard", "purchase"}
_CODE_PREFIX = re.compile(r"^(pos|card|trf|transfer|payment)[:\-\s]+", re.IGNORECASE)
_PUNCT = re.compile(r"[^A-Za-z0-9\s\-']+")
_MULTI_SPACE = re.compile(r"\s+")


def _normalize_desc(text: str) -> str:
    txt = text.strip().lower()
    if not txt:
        return ""
    txt = _CODE_PREFIX.sub("", txt)
    txt = _PUNCT.sub(" ", txt)  # keep spaces & internal hyphen/apostrophe
    txt = _MULTI_SPACE.sub(" ", txt).strip()
    return txt


def extract_counterparty_name(description: str) -> str:
    base = _normalize_desc(description)
    if not base:
        return "Unknown"
    tokens = [t for t in base.split(" ") if t and t not in _STOPWORDS]
    if not tokens:
        return "Unknown"
    candidate = " ".join(tokens)
    stripped = re.sub(r"[^A-Za-z0-9]", "", candidate)
    alnum_len = len(stripped)
    alpha_len = len(re.sub(r"[^A-Za-z]", "", stripped))
    # Require at least one alphabetic char and >=3 alphanumeric total
    if alnum_len < 3 or alpha_len == 0:
        return "Unknown"
    # Further split hyphenated composite tokens into separate words for display
    expanded: list[str] = []
    for t in tokens:
        if "-" in t:
            expanded.extend(part for part in t.split("-") if part)
        else:
            expanded.append(t)
    return " ".join(_title_token(t) for t in expanded)


def _title_token(t: str) -> str:
    if len(t) <= 1:
        return t.upper()
    return t[0].upper() + t[1:].lower()


def get_or_create_counterparty_id(repo_get_or_create: Callable[[str, str], int], description: str) -> int:
    name = extract_counterparty_name(description)
    normalized = name.lower()
    return repo_get_or_create(normalized, name)

__all__ = ["extract_counterparty_name", "get_or_create_counterparty_id"]
