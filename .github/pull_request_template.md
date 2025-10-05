# Pull Request

## Title
(Use conventional commits) e.g. `feat(002): document & counterparty management UI`

## Summary
Explain the intent and scope. Link to spec folder: `specs/<feature-id>-.../`.

## Traceability Checklist
- [ ] Spec updated / locked
- [ ] Plan updated / locked
- [ ] Tasks updated (delta section if needed)
- [ ] Traceability matrix updated (`traceability.md`)
- [ ] All task IDs referenced at least once (CI will run `validate_traceability.py`)

## Quality Gates
| Gate | Status | Notes |
|------|--------|-------|
| Lint (ruff) |  |  |
| Types (mypy) |  |  |
| Tests (pytest) |  |  |
| Contract Schemas |  |  |
| Determinism Guard |  |  |
| Logging Events Schema |  |  |
| Migrations Idempotent |  |  |

## Changes
- (bullet list of key code changes)

## New / Updated Log Events
- (list event_type if added/modified)

## Determinism Impact
Explain if normalization hash or canonical ordering changed (and why). If none: `No impact`.

## Deferred / Follow-ups
List any deferred tasks (with task IDs) and planned follow-up issues.

## Screenshots (optional)
(Attach relevant UI or report artifacts.)

## Acceptance Evidence
Paste or attach excerpt from generated acceptance report (if applicable).

## Checklist
- [ ] I confirm no secrets or sensitive data were added
- [ ] I ran `python scripts/validate_traceability.py` locally (or CI passed)
- [ ] I reviewed diff for accidental large file additions

---
*This template enforces spec → plan → tasks → code → tests → quality → acceptance traceability.*
