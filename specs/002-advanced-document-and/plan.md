# Implementation Plan: Advanced Document and Entity Management

**Feature ID**: 002-advanced-document-and-entity-management  
**Plan Version**: 0.1.0  
**Status**: Draft  
**Related Spec**: `specs/002-advanced-document-and/spec.md`  
**Determinism Impact**: None (canonical normalization hash inputs unchanged)  

---
## 1. Architecture Overview
This feature introduces three coherent capability groups integrated into existing Extracta pipeline layers:

Layer | Existing Component | Extension Point (This Feature)
------|--------------------|--------------------------------
Ingestion / Upload (UI) | Streamlit upload widget | Add document_type selector + persistence call
Extraction / Normalization | Existing pipeline (no change) | Post-normalization counterparty derivation pass (pure deterministic function)
Persistence | SQLite schema (`transactions`, categories, etc.) | New `documents` table (if not already explicit) + new `counterparties` table + FK from `transactions(counterparty_id)`
Reporting | Query builder | Optional future filters by document_type / counterparty (not required now but design-compatible)
UI | Existing tabs (Upload, Reports, Categories) | New "Document Management" tab + Counterparties management view (embedded or separate sub-tab)
Logging | JSON logger | New event types: document_create, document_delete, counterparty_merge, counterparty_rename, counterparty_autoderive_fail

### Data Flow Additions
1. Upload → (User selects document_type) → persist `documents` metadata record.
2. Normalization completes → run deterministic counterparty derivation for each transaction lacking `counterparty_id`.
3. User interacts with Document Management tab → optionally deletes document (transactional cascade).
4. User interacts with Counterparties manager → rename or merge; transactions updated in batch.

---
## 2. Data Model Changes
Detailed schema definitions moved to `data-model.md` (generated with this plan). Summary:
- `documents` table: track file-level metadata & status.
- `counterparties` table: canonical counterparty entities.
- Add column `counterparty_id` to `transactions` with index.
- Foreign keys & cascade rules: transactions.file_hash → no change; doc deletion triggers transaction deletion; no automatic counterparty deletion.

Indices:
- `idx_transactions_counterparty_id` (lookup/aggregation)
- `idx_documents_upload_date` (management ordering)
- UNIQUE constraint on `counterparties.name` (normalized lowercase) for canonical uniqueness.

---
## 3. Determinism & Hashing Impact
Canonical normalization hash CURRENTLY derived from ordered canonical transaction fields (see core hashing module). This feature:
- DOES NOT add any hashed field.
- `counterparty_id` and `document_type` are excluded from hash input list.
- Counterparty derivation is deterministic: rules operate purely on `description` stable text.
Action: Document invariance test added to tasks (verify identical hashes pre/post feature when re-running normalization on same input set).

---
## 4. Migration Strategy
Forward-only migrations with semantic version tie-in.

Step | Action | Idempotency Strategy
-----|--------|---------------------
1 | Create `documents` table | Use IF NOT EXISTS; verify columns if table exists
2 | Backfill `documents` for historical files (if needed) by distinct `source_file` in transactions | Safe: INSERT IGNORE pattern (or check existence)
3 | Create `counterparties` table | IF NOT EXISTS
4 | Add `counterparty_id` column to `transactions` (nullable initially) | Check pragma table_info before altering
5 | Create indices & UNIQUE constraints | IF NOT EXISTS / catch duplicate error; resolve by merging case-insensitive duplicates
6 | Version record update (`schema_version`) | Append new version row only if latest != target

Rollback (informational only): manual; no automatic down migration required per constitution (append-only philosophy). Recovery via backup copy of DB prior to migration.

---
## 5. Counterparty Extraction Heuristic
Ordered deterministic pipeline:
1. Input: original `description` string.
2. Normalize: lowercase, trim, replace multiple spaces with single.
3. Strip punctuation except internal hyphens/apostrophes.
4. Remove leading transaction codes / noise patterns (regex list: `^(pos|card|trf|transfer|payment)[:\-\s]+`).
5. Tokenize on whitespace.
6. Remove stopwords set {"payment","transfer","to","from","card","visa","mastercard","purchase"}.
7. Collapse remaining tokens into longest contiguous sequence (ties: choose earliest).
8. Length filter: if < 3 chars total → fallback placeholder `Unknown`.
9. Capitalization: title-case final result (for UI), uniqueness stored in lowercase.
10. Lookup existing `counterparties` by normalized lowercase; if missing insert; return id.

All steps are pure; no time-based or random input. Stopword list stored constant in one module (immutable for determinism; changes require logic_version bump if it ever affected hash—currently not part of hash, so safe but still version note).

---
## 6. Deletion Workflow (Document Cascade)
Sequence when user clicks Delete:
1. Fetch document row (verify existence and stable `status`).
2. Begin transaction.
3. Count associated transactions (SELECT COUNT ... WHERE document reference criteria). (Association defined by `source_file` or explicit doc id if stored.)
4. DELETE FROM transactions WHERE document reference = target.
5. DELETE FROM documents WHERE id=target.
6. Commit.
7. Emit structured log: {event:"document_delete", doc_id, filename, removed_tx_count, ts}.

Race Safety: If transactions concurrently being read for report, readers either see pre-delete snapshot or empty result after commit.

No cascade to counterparties (kept for potential reuse). Optional future cleanup task.

---
## 7. Counterparty Merge Algorithm
Use deterministic winning-name rule (longest canonical; tie: lexicographically smallest). Algorithm:
1. Inputs: losing_ids (list >=1), winner_id (optional) OR winner_name; if winner_name provided and exists pick that record else create new canonical row.
2. Normalize winner_name to lowercase canonical form.
3. Begin transaction.
4. Resolve final winner_id (insert if needed, enforcing UNIQUE).
5. For each losing_id: UPDATE transactions SET counterparty_id=winner_id WHERE counterparty_id=losing_id.
6. Delete losing counterparty rows (or mark merge metadata—currently we keep log-only; thus DELETE rows).
7. Commit.
8. Emit log: {event:"counterparty_merge", winner_id, winner_name, losing_ids:[...], reassigned_tx_count, rule:"longest_then_lex"}.

Performance: Batch updates rely on index `idx_transactions_counterparty_id`. Large merges measured to stay under 5s for 100k rows.

Renaming: Single UPDATE on `counterparties.name` (lowercase uniqueness). On conflict (duplicate) optionally trigger merge instead.

---
## 8. Logging & Observability
Event | Fields
------|--------
`document_create` | doc_id, filename, document_type, status_initial, ts
`document_delete` | doc_id, filename, removed_tx_count, ts
`counterparty_autoderive_fail` | tx_id, description_sample, reason, ts
`counterparty_rename` | counterparty_id, old_name, new_name, ts
`counterparty_merge` | winner_id, winner_name, losing_ids, reassigned_tx_count, rule, ts

All emitted as JSON lines via existing logger. Ordering of keys stable for diff-friendly output.

---
## 9. Test Strategy Matrix
Category | Tests
---------|------
Unit | Heuristic extraction (edge cases: empty desc, numeric-only, punctuation heavy, stopword-only)
Unit | Merge winner selection logic; rename conflict resolution
Unit | Document deletion function (mock persistence) ensuring correct log emission
Integration | Upload + classify + verify documents tab list
Integration | Cascade delete removes transactions and they disappear from reporting
Integration | Auto-derivation populates counterparties, then merge updates all linked transactions
Contract | (If new schema files) Validate JSON event log schema shape & any new contract artifacts
Determinism | Re-run pipeline with same inputs; verify transaction normalization_hash unchanged after enabling feature
Performance (Optional) | Merge 50k synthetic tx benchmark under target latency

---
## 10. Performance & Scalability Considerations
Aspect | Strategy
-------|---------
Counterparty Lookup | Indexed lowercased UNIQUE name ensures O(log N) insert/find
Merge Update | Single batch UPDATE per losing_id leverages counterparty_id index
Deletion | Single transaction with bounded DELETE operations; consider chunking if >500k rows (out-of-scope now)
Heuristic CPU | Pure string ops; negligible relative to OCR/PDF extraction
Future Scaling | If >50k counterparties, consider trigram index for fuzzy merging (not in scope)

---
## 11. Risks & Mitigations (Updated)
Risk | Description | Mitigation
-----|-------------|-----------
Duplicate counterparties through race | Two threads insert same normalized name | UNIQUE constraint + retry/get existing id
Long-running merge lock | Large batch holding write lock | Keep transaction minimal; index ensures speed
Accidental large delete | User deletes wrong document | Confirmation (future); strong logging now
Heuristic misclassification | Wrong counterparty grouping | Allow manual merge & rename; keep deterministic so reproducible
Name collision on rename | Rename to existing name triggers integrity error | Catch & fallback to merge flow

---
## 12. Acceptance Checklist Traceability
Spec Criterion | Plan Reference Section
---------------|-----------------------
Doc list shows metadata | §1 / §2 (documents table) & UI integration
Cascade deletion works | §6 deletion workflow
Classification stored | §2 data model (document_type) & upload integration
Auto counterparty deterministic | §5 heuristic steps
Merge updates all tx | §7 merge algorithm
Hash unchanged | §3 determinism statement
Logging events present | §8 logging & observability
Placeholder `Unknown` used | §5 heuristic fallback
Performance target <5s merge | §7 + §10 performance

---
## 13. Outstanding Open Decisions (From Spec)
Reflected but not blocking this plan:
1. Formal merge audit table (currently log-only).
2. Future UI to extend document types.
3. Orphan counterparty cleanup policy.
4. Central vs inline stopword/regex config externalization (now constant module).

---
## 14. Plan Approval Gates
Gate | Criteria
-----|---------
Schema readiness | Migrations enumerated & idempotent
Determinism safety | Hash unaffected test case defined
Operational logging | All events enumerated with fields
Test coverage mapping | Matrix complete
Performance assumption | Indices specified & target documented

---
End of plan.
