
# Implementation Plan: Extracta Core Pipeline (Feature 001)

**Branch**: `001-extracta-core` | **Date**: 2025-10-02 | **Spec**: `specs/main/spec.md` (wraps `specs/extracta-core/spec.md`)
**Input**: Consolidated feature specification (core pipeline + reporting + templates)

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Implement a deterministic local-first financial data pipeline that ingests PDF/Image source documents, extracts tabular transaction data (OCR for images), validates and normalizes into a canonical Transaction Model, persists to SQLite, supports manual categorization, and provides an interactive reporting constructor (filters, multi-level grouping, aggregation) with persistent report templates. Technical approach favors minimal dependencies (pdfplumber + pytesseract tentative), batch/stream extraction for large files, rule-based normalization via YAML mapping, and structured JSON logging for each pipeline stage.

## Technical Context
**Language/Version**: Python 3.11 (ASSUMPTION; confirm interpreter)  
**Primary Dependencies** (proposed minimal set):
- pdfplumber (PDF table/text extraction) (Q1)
- pytesseract + Tesseract OCR binary (image OCR) (Q2)
- Pillow (image pre-processing)
- pandas (intermediate tabular handling; ensure streaming-friendly usage)
- pyyaml (mapping config)
- sqlite3 (stdlib) OR SQLAlchemy (TBD – simplicity vs migration) (Q5)
- streamlit (UI)
- hashlib (stdlib) for hashing
- logging / json (stdlib)
**Storage**: SQLite local file `data/extracta.db` (Q4: env override)  
**Testing**: pytest + hypothesis (optional future) (NEEDS CLARIFICATION: hypothesis inclusion)  
**Target Platform**: Local desktop (Windows/Mac/Linux) single-user  
**Project Type**: Single project (CLI/Streamlit hybrid)  
**Performance Goals**: Handle up to 1M rows or 1GB PDF via page/row streaming; < 300MB peak RSS for large file  
**Constraints**: Deterministic output hashes; no network dependency for core; avoid full materialization of large tables  
**Scale/Scope**: Single user, tens of source files per session, cumulative DB up to a few million rows

**Open Clarifications (Phase 0 Targets)**: Q1–Q10 from spec (libraries, config format, DB path override, FK strategy, derived date parts, aggregation expansion, template versioning, counterparty parsing approach, log destination, stack trace truncation length).

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Requirement | Plan Alignment | Risk / Mitigation |
|-------------------------|----------------|-------------------|
| Data Integrity First | Raw files never modified; store SHA256 + only read operations | Ensure copy avoidance—hash before processing to avoid accidental writes |
| Reproducibility & Determinism | `normalization_hash = sha256(source_file_hash + mapping_version + logic_version + ordered_fields)` | Pin dependency versions in `requirements.txt`; record `NORMALIZATION_LOGIC_VERSION` constant |
| Privacy & Minimum Access | Only required columns parsed; no secrets stored; future PII masking hook | Review extraction for accidental retention of extraneous metadata |
| Observability & Auditability | JSON structured logs per stage with counts, durations, hashes | Provide log schema & lightweight logger utility early (Phase 1) |
| Simplicity & Extensibility | Minimal libs (pdfplumber, pytesseract); modular stage directories | Avoid premature framework (no ORM unless needed) |
| Supported Sources | Limit to pdf/png/jpg initial | Additional types require design note; gate in ingestion registry |
| Data Flow Stages | ingest→validate→normalize→(optional enrich future)→analyze (report)→export (report outputs) | Keep enrich dormant placeholder only (no implementation yet) |
| Schema Contracts | Canonical Transaction Model v0.1.0 documented + JSON Schema file | Migration script template in Phase 1 |
| Error Handling | Fail fast on integrity; soft anomaly counters | Central exception wrapper per stage |
| Performance Baseline | Streaming page & row iteration; chunk normalization | Add memory guard in large file processing |
| Security | No plaintext secrets; local only | If OCR cache path used, ensure not logging sensitive temp names |
| Tests Requirement | Each module to add happy/failure & pipeline integration | Enforce via initial test stubs + CI later |
| Lint & Type | Introduce ruff + (optional) mypy once types added | Add config early to avoid drift |
| Release Versioning | SemVer; initial 0.1.0 | Add `VERSION` file & bump policy in quickstart |

Result: INITIAL GATE PASS (no unjustified violations). No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->
```
src/
   ingestion/
   extraction/
   normalization/
   persistence/
   categorization/
   reporting/
   ui/
   logging/
   common/          # utils (hashing, schema load)

tests/
   unit/
   integration/
   contract/

config/
   mappings.yml     # normalization header mapping rules

data/              # SQLite db (gitignored)
logs/              # JSONL logs (gitignored)
```

**Structure Decision**: Single-project modular directory grouping per pipeline stage to maximize clarity & test isolation while keeping import paths shallow.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate Contracts (Non-HTTP for MVP)**:
   - Define JSON Schema for Transaction Model (`contracts/transaction.schema.json`).
   - Define logging event schema (`contracts/log-event.schema.json`).
   - Define report request schema (`contracts/report-request.schema.json`).
   - (No external REST API endpoints in MVP—UI calls internal functions.)

3. **Generate contract tests**:
   - Validate sample transaction JSON against schema (initially failing due to missing implementation loader).
   - Validate log event structure.
   - Validate report request builder serialization.

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot`
   - Add only NEW tech decisions (pdfplumber, pytesseract) & resolved Q* decisions
   - Keep under 150 lines

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P] 
- Each user story → integration test task
- Implementation tasks to make tests pass

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 28-34 numbered tasks in `tasks.md` (includes schema + logging + test scaffolds)

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [ ] Phase 0: Research complete (/plan command)
- [ ] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PASS
- [ ] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v0.1.0 - See `.specify/memory/constitution.md`*
