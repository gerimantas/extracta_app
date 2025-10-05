"""Normalization package: validation, mapping, engine composition.

Includes optional counterparty heuristic module (feature 002). The import is
wrapped to avoid hard failure if the module is absent in earlier feature sets.
"""

__all__: list[str] = []

try:  # pragma: no cover - optional feature module
    from . import counterparty_heuristic as _counterparty_heuristic  # type: ignore  # noqa: F401
    __all__.append("counterparty_heuristic")
except ImportError:  # pragma: no cover
    # Module may not exist before feature 002 is merged
    pass
try:
    from .counterparty_derivation import derive_counterparties  # noqa: F401
    __all__.append("derive_counterparties")
except ImportError:  # pragma: no cover
    pass
