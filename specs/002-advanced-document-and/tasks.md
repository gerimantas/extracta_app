# Tasks: Advanced Document and Entity Management (Feature 002)

Completion Note (post-implementation): Phases 0–9 implemented; Phase 10 acceptance test added (see tests/integration/test_acceptance_feature_002.py). Performance benchmark placeholder added (tests/performance/test_counterparty_merge_perf.py, skipped). Remaining enhancements (ordering assertions, richer UI tests) deferred.

Status: Draft  
Strategy: Strict TDD ordering (write or scaffold tests before implementation).  
Determinism Guard: Any change impacting canonical hash fields is forbidden (plan §3).

Commit Message Convention: Use `feat(002): task <ID> <short-description>` for each implemented task; use `test(002):` for pure test additions; `refactor(002):` only if no behavior change.

Legend:
- [parallel] Task may be executed in parallel with prior phase tasks marked likewise.
- Test refs use suggested file paths (they will be created if missing).
- Validation = manual or scripted check (logs, sqlite schema, hash comparison).

---
## Phase 0: Migrations & Schema Setup (plan §§2,4, data-model)
0.1 Write migration test spec for new tables/columns (failing first): create test that asserts absence then expects creation of `documents`, `counterparties`, and `transactions.counterparty_id`.  
    Test: `tests/integration/test_migration_documents_counterparties.py`
0.2 Implement forward-only migration logic adding `documents` & `counterparties` tables + `counterparty_id` column + indices.  
    Validation: Re-run test 0.1 (green) + SQLite pragma checks.
0.3 Backfill `documents` table from distinct existing `transactions.source_file` (status=Success, document_type=Other).  
    Test: extend 0.1 test with backfill assertion (# of distinct file hashes == # documents).
0.4 Add schema version bump & idempotency check (calling migration twice unchanged).  
    Test: Idempotent invocation assertion in same integration test.

## Phase 1: Counterparty Heuristic Core (plan §5)
1.1 Create unit test skeletons for heuristic edge cases: empty description, numeric-only, punctuation, stopword-only, mixed tokens, tie-break scenario.  
    Test: `tests/unit/test_counterparty_heuristic.py` (RED)
1.2 Implement normalization + tokenization + stopword filtering function (pure).  
    Test: run 1.1 (GREEN subset for implemented steps).
1.3 Implement code-removal regex step + longest contiguous sequence selection.  
    Test: add cases asserting deterministic tie resolution.
1.4 Add placeholder fallback logic (<3 chars -> Unknown) & title casing.  
    Test: new cases Unknown placeholder.
1.5 Integrate lookup/insert wrapper (mock repository) ensuring deterministic duplicate handling.  
    Test: patch repository mock verifying single insert on duplicate calls.

## Phase 2: Persistence Layer Extensions (plan §§2,7)
2.1 Add repository abstractions: DocumentsRepo (create/list/delete), CounterpartiesRepo (get_or_create, rename, merge, list).  
    Test: `tests/unit/test_repositories_documents_counterparties.py` (initial failing stubs)
2.2 Implement DocumentsRepo methods with transactional delete returning removed tx count.  
    Test: repository test asserts count + deletion cascade.
2.3 Implement CounterpartiesRepo.get_or_create (case-insensitive).  
    Test: ensure second call returns same id.
2.4 Implement rename logic (collision triggers merge path exception).  
    Test: rename conflict scenario.
2.5 Implement merge algorithm (winner selection rule) with losing id deletion.  
    Test: merge test asserts reassigned tx count & only winner remains.

## Phase 3: Upload Flow Integration (plan §§1,2) [parallel with Phase 1 late tasks]
3.1 Add unit test (UI layer stub) expecting document_type selector default=Other when omitted.  
    Test: `tests/unit/test_upload_document_type_selector.py`
3.2 Wire selector value into document creation call (mock persistence).  
    Test: same test verifies persisted type.
3.3 Emit `document_create` log event on successful record creation.  
    Test: `tests/integration/test_logging_document_create.py` (assert JSON line fields).

## Phase 4: Counterparty Derivation Integration (plan §§1,5) [parallel with 3.2+]
4.1 Integration test skeleton: ingest sample transactions with various descriptions → expect counterparty assignment or Unknown.  
    Test: `tests/integration/test_counterparty_derivation_pipeline.py`
4.2 Hook heuristic post-normalization (batch process unassigned).  
    Test: pipeline test passes; counters for Unknown vs known.
4.3 Ensure rerun idempotency (second pass does not create duplicates).  
    Test: same integration test asserts stable counts after second invocation.

## Phase 5: Document Management UI Tab (plan §§1,6)
5.1 UI test skeleton: expect new tab label "Document Management" available.  
    Test: `tests/integration/test_ui_document_tab.py`
5.2 Implement listing adapter (query documents, show columns).  
    Test: asserts all required columns present.
5.3 Implement delete action invoking cascade repo call; show confirmation message.  
    Test: simulate delete then assert transactions absent (reuse reporting query fixture).
5.4 Emit `document_delete` log event; assert removed_tx_count correct.  
    Test: extend logging integration test.

## Phase 6: Counterparty Management UI (plan §§1,7,8)
6.1 UI test skeleton: expect management view listing counterparts & showing merge / rename actions placeholders.  
    Test: `tests/integration/test_ui_counterparty_management.py`
6.2 Implement list rendering & simple search/filter.  
    Test: ensure known seeded counterparties show.
6.3 Implement rename action (updates repository, refresh view).  
    Test: rename reflected in listing & transactions updated.
6.4 Implement merge workflow (select multiple -> merge into winner).  
    Test: merge reflects winner only, transactions reassigned.
6.5 Emit `counterparty_rename` and `counterparty_merge` log events.  
    Test: logging test extended with event field assertions.

## Phase 7: Merge & Rename Integrity Tests (plan §§7,10)
7.1 Add large synthetic dataset generation helper (not committed to prod path) for performance test.  
    Test: `tests/performance/test_counterparty_merge_perf.py` (skipped by default marker)
7.2 Validate performance target (<5s for 100k reassignment) or mark skip with measured time note.  
    Validation: timing assertion or recorded metrics.
7.3 Edge case: merging already merged (losing id missing) gracefully no-op.  
    Test: new case in repositories test.

## Phase 8: Logging Events Validation (plan §8)
8.1 Define logging schema expectations for new events (fields & types) inside test constants.  
    Test: `tests/contract/test_logging_new_events.py`
8.2 Generate events via integration fixture (create/delete/merge/rename + one autoderive fail).  
    Test: same file parses lines JSON schema-like assertions.
8.3 Ensure field ordering stable (optional) or at least presence.  
    Test: assertion on key set.

## Phase 9: Determinism Guard Test (plan §§3,9)
9.1 Snapshot baseline normalization_hash values pre-feature (use existing test fixtures).  
    Test: `tests/integration/test_hash_determinism_guard.py` (store list in memory)
9.2 Re-run pipeline with feature enabled & no counterparty merges altering data; compare hashes identical.  
    Test: same file asserts equality.
9.3 Add negative control: purposely change stopword list (simulated) to show test would fail (skipped by default).  
    Test: marked skip (non-blocking documentation of guard sensitivity; NEVER unskip in CI).

## Phase 10: Acceptance Checklist Verification Task (plan §12)
10.1 Create acceptance test consolidating criteria (doc listing, cascade delete, classification persistence, auto-derivation, merge effect, hash unchanged).  
     Test: `tests/integration/test_acceptance_feature_002.py`
10.2 Manual review script/output summary (log event counts & sample rows) to attach to PR.  
     Validation: generated summary file `artifacts/feature_002_acceptance_report.txt`.

---
## Parallelization Notes
- Phase 1 tasks (1.1–1.3) can run while migrations (0.2+) finalize. Mark 1.1–1.3 [parallel].
- Phase 3 UI skeleton (3.1) can start after 0.1 & 0.2 (schema baseline). Mark 3.1 [parallel].
- Phase 4 integration hooking waits until heuristic core (1.x) & repository (2.x) minimal methods exist.
- Heavy merges (7.x) deferred until UI + core stable to avoid churn.

(Explicit tags already placed in narrative—developers may annotate commit messages with task IDs.)

## Acceptance Criteria Mapping (Spec §5 → Tasks)
Criterion | Tasks Covering | Notes
---------|----------------|------
Document tab lists metadata | 5.1, 5.2 | UI presence + required columns
Cascade delete removes doc + tx | 5.3, 5.4 | Deletion + logging removed count
Document type selector persists value | 3.1, 3.2 | Default "Other" & persistence
Deterministic counterparty auto-derive | 1.1–1.5, 4.1–4.3 | Unit + integration coverage
Merge updates all linked transactions | 2.5, 6.4, 6.5, 7.3 | Repo, UI, logging, edge case
Normalization hash unchanged | 9.1, 9.2 | Guard snapshot & compare
Placeholder Unknown fallback | 1.4, 4.1 | Explicit fallback tests
Logging of key events | 3.3, 5.4, 6.5, 8.1–8.2 | Contract & integration tests
Performance merge target (<5s) | 7.1, 7.2 | Benchmark / skip annotation

All acceptance criteria are mapped; no gaps.

## Orphan Task Analysis
No orphan tasks detected. Negative-control task 9.3 intentionally demonstrates guard robustness (skipped / xfail) and traces to determinism assurance.

## Determinism Guard Confirmation
Tasks 9.1–9.2 validate canonical `normalization_hash` stability. Task 9.3 (negative control) confirms test sensitivity.

## Gap Report
No immediate gaps. Open Decisions (spec §9) intentionally deferred (will spawn future tasks if prioritized).

Gate | Required Passing Tasks
-----|-----------------------
Schema Ready | 0.1–0.4
Heuristic Stable | 1.1–1.5
Repo Layer | 2.1–2.5
Upload Integration | 3.1–3.3
Derivation Integrated | 4.1–4.3
Management UI | 5.1–5.4
Counterparty UI | 6.1–6.5
Integrity & Perf | 7.1–7.3
Logging Contract | 8.1–8.3
Determinism Guard | 9.1–9.2
Acceptance | 10.1–10.2

---
End of tasks.
