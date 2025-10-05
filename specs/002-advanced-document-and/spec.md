# Feature Spec: Advanced Document and Entity Management

**Feature ID**: 002-advanced-document-and-entity-management  
**Status**: Draft  
**Owner**: TBD  
**Related Constitution Version**: 0.1.0  
**Depends On**: Core pipeline (ingestion, extraction, normalization, persistence) already implemented.

## 1. Overview & Goal
As an active user, I want richer control over uploaded documents and extracted transactional entities so I can manage heterogeneous financial sources, classify them consistently, and standardize counterparties.

## 2. Scope Summary
1. Document Management Panel (UI tab listing documents + cascade delete)  
2. Document Classification (assign document_type at upload)  
3. Counterparties Database (auto-derive + manage + merge)

## 3. In-Scope Features
### 3.1 Document Management Panel
- New Streamlit tab: "Document Management".
- Table columns: filename, upload_date, status (Uploaded|Processing|Success|Error), document_type.
- Delete action: removes document record and ALL associated transactions (deterministic cascade).

### 3.2 Document Classification
- On upload, user selects type from fixed list: [Bank Statement, Accounting Ledger, Purchase Receipt, Other].
- Stored with document metadata (persisted in DB).
- If user omits selection, default = "Other" (subject to clarification).

### 3.3 Counterparties Database
- Deterministic heuristic extraction from transaction description to propose counterparty.
- Separate `counterparties` table storing unique canonical names.
- Each transaction links to a counterparty id (nullable until resolved or placeholder?).
- UI management: list, rename, merge duplicates; merging re-links associated transactions.

## 4. User Stories
1. As a user, I view all uploaded documents in a dedicated management tab.
2. As a user, I delete an obsolete document and all its derived transactions disappear from reports.
3. As a user, I classify a newly uploaded file with a defined document type to improve filtering.
4. As a user, I see transactions automatically tagged with a proposed counterparty.
5. As a user, I standardize messy counterparty variants by merging them into a single canonical name.
6. As a user, I rename a counterparty and all linked transactions reflect the new canonical name.

## 5. Acceptance Criteria (Initial Draft)
- Document tab lists all previously ingested files with required columns.
- Deleting a document removes it and its transactions; those transactions no longer appear in any report query.
- Upload flow shows document_type selector; persisted value retrievable in document list.
- Counterparty auto-derivation runs without external network calls and is deterministic given same description.
- Counterparty merge updates all linked transactions; only one canonical record remains; no orphan references.
- Normalization hash of existing transactions remains unchanged by this feature (hash inputs not extended).

## 6. Non-Goals
- No ML or probabilistic/NLP models (strictly rule-based heuristics).
- No user authentication or permissions layer.
- No external API enrichment for counterparties.
- No soft-delete audit trail unless later justified.

## 7. Risks & Mitigations (Preliminary)
| Risk | Impact | Mitigation |
|------|--------|------------|
| Over-aggressive deletion | Data loss | Confirm prompt (future); start with irreversible but logged action |
| Incorrect counterparty merge | Misattributed history | Provide dry-run diff (future enhancement) / deterministic merge order |
| Performance on bulk merge | Slow UI | Batched SQL updates & indexing |
| Hash contamination | Break determinism | Keep counterparty & doc meta outside canonical hash scope |

## 8. Clarifications (Resolved)
**Q1 Deletion semantics**: Hard delete only in this phase. No soft delete table; each deletion emits a structured log entry with document id/hash and counts of removed transactions. Future audit table optional.

**Q2 Status lifecycle**: States are exactly `Uploaded -> Processing -> (Success | Error)`. "Processing" covers extraction + normalization. No extra granular states for MVP.

**Q3 Counterparty extraction operations**: Deterministic heuristic pipeline: (1) lowercase; (2) strip punctuation; (3) collapse whitespace; (4) remove leading transaction codes (regex for common bank prefixes); (5) pick longest remaining alphanumeric token sequence excluding stopwords (e.g. 'payment','transfer'); (6) normalize multiple spaces to single. No ML, no external calls.

**Q4 Fallback for unidentified counterparty**: Use canonical placeholder `Unknown` and create (or reuse) a single counterparty record for aggregation consistency (not NULL).

**Q5 Merge conflict resolution**: Winning name = longest non-placeholder canonical name. Tie → lexicographically smallest. All losing ids remapped; result logged with mapping list.

**Q6 Scale expectations**: Up to 10k documents, up to 50k distinct counterparties, up to ~1M transactions. Requires index on `counterparty_id` and (counterparty name UNIQUE) plus document table index on (upload_date).

**Q7 Deletion concurrency**: Deletion executes in a transaction with FK cascade. Concurrent report queries may momentarily return stale data; acceptable—next query sees removal. No partial deletes due to transactional boundary.

**Q8 Document types extensibility**: Fixed list for this feature. Later extensibility via configuration or admin UI is out-of-scope.

**Q9 Logging obligations**: MUST log: document create, document delete (with removed tx count), counterparty auto-derive failure (with reason), counterparty rename, counterparty merge (old_ids, new_id, reassigned_tx_count), merge conflict resolution rule applied. Exclude raw PII; log canonical counterparty value only.

**Q10 Transaction linkage timing**: Transactions assigned a counterparty during post-normalization derivation pass. Placeholder `Unknown` assigned immediately if heuristic yields nothing—no NULLs persisted.

**Q11 Merge audit**: Phase 1: log-only (JSON line) with mapping. No dedicated audit table yet; future enhancement may add table if needed.

**Q12 Default document_type**: If user omits selection, default = `Other` (explicit). No blocking prompt in MVP.

**Q13 Merge performance target**: Re-link up to 100k transactions in <5 seconds on commodity dev machine (SSD). Use indexed batch UPDATEs.

**Q14 Orphan counterparties after document deletion**: Do NOT delete automatically. Keep counterparties (even if temporarily unreferenced) for historical continuity and potential re-upload linking. Future cleanup task possible.

Clarification Cycle Status: All clarification questions answered. No further clarifications required for Feature 002 prior to implementation.

## 9. Open Decisions (Deferred / Out-of-Scope for Feature 002)
1. Whether to introduce a formal `counterparty_merge_audit` table (currently log-only). (Deferred)
2. Potential future UI to extend document types dynamically. (Deferred)
3. Policy & tooling for orphan counterparty cleanup (threshold, retention time). (Deferred)
4. Refine stopword list & regex patterns—store centrally or inline? (Deferred; current plan uses constant module.)

## 10. Determinism Statement
This feature MUST NOT alter the canonical normalization hash algorithm or its field set. Counterparty IDs and document types are auxiliary metadata and excluded from hash computation.

## 11. Next Steps
Proceed with clarification cycle (/clarify answers), then generate implementation plan (/plan) ensuring sections: Data Model Changes, Determinism & Hashing Impact, Migration Strategy, Counterparty Heuristic Algorithm, Cascade Deletion Workflow, Merge Algorithm, Test Matrix, Logging & Observability.

---
End of initial draft spec.
