# Extracta Constitution

Minimal guiding rules for the Extracta data extraction & analysis application. If a practice is not written here, default to: keep it simple, make it testable, protect the data.

## Core Principles

### 1. Data Integrity First
Raw source data must never be mutated in-place. All transformations produce new, versioned artifacts with provenance (source id, timestamp, transform hash).

### 2. Reproducibility & Determinism
Given the same input snapshot + configuration, the system must produce byte‑equivalent outputs. All processing steps declare: inputs, outputs, assumptions, failure modes.

### 3. Privacy & Minimum Access
Only the minimal fields required for a step may be loaded/decrypted. Secrets & credentials live outside source control. PII is masked or tokenized before persistence beyond staging layers.

### 4. Observability & Auditability
Every extraction + transform emits: start/end time, record counts (in/out/error), checksum, version, and structured error detail. Logs are machine‑parseable (JSON) and human‑readable.

### 5. Simplicity & Extensibility
Prefer small pure functions / composable pipelines over frameworks. Add dependencies only with a clear payoff (performance, correctness, security). Remove dead code quickly.

## Operational & Security Requirements

1. Supported Sources: Local files (.pdf, .png, .jpg). Additional formats (e.g., .docx, .tiff, .json) require a brief design note before inclusion.
2. Data Flow Stages: ingest → validate → normalize → enrich (optional) → analyze → export. Each stage explicit, testable, and skippable via flags.
3. Schema Contracts: All structured outputs (normalized, enriched, analytics) declare a versioned schema; breaking change requires major schema version bump + migration note.
4. Error Handling: Fail fast on schema or integrity violations; soft‑count and report non-critical content anomalies (e.g., missing optional fields) but continue.
5. Performance Baseline: Single run must handle 1M rows or 1GB source file within memory limits using streaming / chunking (no full in‑memory materialization unless <100MB).
6. Security: No plaintext secrets in code or logs. Hash or redact sensitive values. Network calls time out and are retried with backoff (max 3 attempts).

## Development Workflow & Quality Gates

1. Tests: Each new module requires: (a) happy path unit test, (b) one failure path, (c) a minimal pipeline integration test (can be synthetic data subset).
2. Lint & Type Gates: Code must pass linting + type checks before merge (tooling TBD; initial baseline: flake8/ruff + mypy if types introduced).
3. Review: At least one reviewer confirms: principle adherence, test coverage, no unnecessary complexity, clear naming, logging fields present.
4. Documentation: Public functions & pipeline stages need a one‑sentence purpose + parameter/return description; transformation stages list input & output field sets.
5. Release Versioning: Semantic Versioning (MAJOR.MINOR.PATCH). Breaking schema or CLI changes bump MAJOR. New additive features bump MINOR. Fixes/patches bump PATCH.

## Governance

1. This constitution overrides undocumented practices.
2. Amendments require: rationale, impact summary (risk, migration), version bump, and reviewer approval.
3. Any deviation (temporary exception) must include an expiry note (date + condition) and is removed or codified within two release cycles.
4. CI (when added) enforces: tests green, lint/type clean, version updated for user-visible changes.
5. Security or data integrity incidents trigger immediate post‑mortem with remediation tasks tracked.

**Version**: 0.1.0 | **Ratified**: 2025-10-02 | **Last Amended**: 2025-10-02

End of constitution.