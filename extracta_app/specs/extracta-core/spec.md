# Feature Spec: Extracta Core Pipeline

**Feature ID**: 001-extracta-core  
**Status**: Draft  
**Owner**: TBD  
**Related Constitution Version**: 0.1.0  
**Initial Schema Version**: 0.1.0

## 1. Overview
Extracta enables a user to upload heterogeneous financial source documents (PDF statements, images/screenshots) and obtain a unified, queryable, and reportable transaction dataset. The system ingests raw files, extracts text/tabular content (including OCR for images), normalizes records into a canonical Transaction Model, persists them locally (SQLite), supports categorization, and provides an interactive reporting constructor with reusable templates.

## 2. Problem Statement
Personal / small business financial data is fragmented across exported statements, screenshots, and scanned images. Manual consolidation is error-prone, non‑repeatable, and limits analysis flexibility. Extracta automates a deterministic, auditable pipeline from ingestion to custom reporting while preserving source integrity and provenance.

## 3. Goals & Non-Goals
### Goals
1. Deterministic normalization of heterogeneous inputs into a single schema.
2. Local-first processing (no external network calls required for core pipeline).
3. Minimal friction UI (Streamlit) for upload, review, categorize, and report construction.
4. Reusable report templates with persistent storage.
5. Robust observability (counts, checksums, timing) per stage (aligning with Constitution §4).

### Non-Goals (Initial Scope)
1. Multi-user concurrency or authentication.
2. Cloud storage / remote sync.
3. Real-time streaming ingestion (batch only for MVP).
4. Advanced ML auto-categorization (manual first; ML later extension).
5. Document formats beyond .pdf, .png, .jpg (others require design note before inclusion).

## 4. User Stories
1. As a user, I upload one or more financial files (.pdf/.png/.jpg) and see extracted raw rows previewed.
2. As a user, I confirm normalization results and see standardized fields for each transaction.
3. As a user, I assign or create categories for uncategorized transactions.
4. As a user, I construct a custom report using filters (date range, type, categories, counterparty text search), grouping (multi-level), and aggregation (Sum/Avg/Count of chosen numeric field).
5. As a user, I view the report as a table or chart (bar at minimum) and switch formats without redefining the report.
6. As a user, I save a configured report as a named template and later reload it to recreate the same view.
7. As a user, I can re-run the pipeline on new uploads without mutating prior normalized data (versioned artifacts / provenance retained).

## 5. Functional Requirements by Stage
### 5.1 Ingestion & Extraction
- Accept multiple file uploads (.pdf, .png, .jpg) via Streamlit widget.
- Detect file type by extension (and optionally MIME if accessible) and route:
  - PDF: structured text / table extraction (NEEDS CLARIFICATION: library choice — pdfplumber vs PyPDF2 vs Camelot for tables).
  - Image (png/jpg): OCR for text + table heuristics (NEEDS CLARIFICATION: OCR engine — Tesseract local vs easyocr).
- Capture raw extraction artifact per file with metadata: `{source_file, source_file_hash, extracted_at, extraction_method, record_count_raw}`.
- Do NOT mutate original file. Store copy path/hash only.

### 5.2 Validation
- Basic integrity checks: non-empty extraction, column presence heuristics (e.g., at least one amount and a date-like token). 
- Fail fast (halt pipeline for that file) on: unreadable file, zero records, irrecoverable parse errors.
- Soft anomalies (tracked, pipeline continues): invalid date formats convertible by fallback, negative amount in income column, etc.

### 5.3 Normalization
- Map heterogeneous column headers to canonical Transaction Model fields (see §6) using rule set.
- Rule engine order: explicit file-pattern overrides > generic header synonyms > fallback inference (NEEDS CLARIFICATION: config file format; propose YAML mapping file `config/mappings.yml`).
- Compute `amount_in` and `amount_out` such that only one is non-zero per row; infer sign if source uses signed single amount column.
- Enforce deterministic transforms (hash of: source_file_hash + mapping_version + normalization_logic_version) stored as `normalization_hash`.
- All normalized rows tagged with `source_file` and `source_file_hash`.

### 5.4 Data Management (Persistence & Categorization UI)
- Persist normalized transactions to SQLite in `data/extracta.db` (NEEDS CLARIFICATION: exact path & override via env var?).
- Schema migrations versioned (table `schema_version`).
- Categories stored in `categories` table; relation by `transaction.category` (string or FK). (NEEDS CLARIFICATION: prefer FK for referential integrity?).
- UI provides: list uncategorized, bulk assign category, create new category, rename category (cascades), optional delete (block if in use or cascade with confirmation).

### 5.5 Reporting Constructor
- Filters:
  - `date_range` (start inclusive, end inclusive)
  - `transaction_type` derived: expense if `amount_out>0`, income if `amount_in>0`
  - `categories` multi-select
  - `counterparty` substring search (case-insensitive)
- Grouping: multi-select ordered list from allowed fields: `[category, counterparty, month, transaction_date (day), source_file]` (NEEDS CLARIFICATION: include year/month derivations precomputed or computed on query?).
- Aggregations: numeric field select from `[amount_in, amount_out]`; functions `[sum, avg, count]` (NEEDS CLARIFICATION: median / min / max future?).
- Output Modes: Table view (paginated), Chart view (bar; library choice: Streamlit built-in altair). (NEEDS CLARIFICATION: add line chart?).
- Templates: persist JSON blob with: name (unique), filters, grouping array (ordered), aggregation `{field, func}`, visualization preference. Stored in `report_templates` table.

### 5.6 Observability & Audit
- Each stage emits structured log entry (JSON) with: `stage`, `start_time`, `end_time`, `duration_ms`, `in_count`, `out_count`, `error_count`, `source_file(s)`, `hashes`, `status`.
- On error, record `exception_type`, `message`, `stack_excerpt` (NEEDS CLARIFICATION: stack truncation length). 
- Provide in-UI optional diagnostics panel (Phase 2+ enhancement; MVP logs to console/file only).

## 6. Canonical Transaction Model
| Field | Type | Description | Notes |
|-------|------|-------------|-------|
| transaction_id | TEXT (UUID) | Unique id for row | Generated at normalization |
| transaction_date | DATE | Date of transaction | Parse & ISO format (YYYY-MM-DD) |
| description | TEXT | Raw or cleaned description | Preserve original text mostly |
| amount_in | REAL | Incoming amount | 0 if not income |
| amount_out | REAL | Outgoing amount | 0 if not expense |
| counterparty | TEXT | Merchant/payee/payer | Derive from description heuristics (Phase 2+) |
| category | TEXT / FK | User-assigned category | Empty until assigned |
| source_file | TEXT | Original filename | Immutable |
| source_file_hash | TEXT | Hash (e.g., SHA256) | For provenance |
| normalization_hash | TEXT | Transform determinism hash | See §5.3 |
| created_at | TIMESTAMP | Insert time | Default current timestamp |

## 7. Data Flow Summary
```
User Upload → Stage: Ingest/Extract → Raw Artifact (JSON or temp table)
   → Validate → Normalization → SQLite Persist (transactions)
      → Categorization (in-place updates) → Reporting Query Engine
         → Report (table/chart) & Template Save
```

## 8. Non-Functional Requirements
| Aspect | Requirement |
|--------|-------------|
| Determinism | Same input set + config yields identical normalized dataset & hashes |
| Performance | Support up to 1M rows or 1GB single file via chunked processing (stream PDF pages / OCR images sequentially) |
| Memory | Avoid full in-memory load if >100MB; process in batches |
| Security | No plaintext secrets in code/logs; local only; redact potential PII if extended fields added |
| Resilience | Retry transient OCR failures (max 3 with backoff) |
| Logging | Machine-parseable JSON lines; human-readable field order stable |
| Extensibility | Adding a new source format requires only adding an extractor + mapping rules |

## 9. Open Questions / NEEDS CLARIFICATION
| ID | Topic | Question | Impact |
|----|-------|----------|--------|
| Q1 | PDF Extraction Library | pdfplumber vs Camelot vs others? | Table accuracy, dependency weight |
| Q2 | OCR Engine | Tesseract local vs easyocr? | Install complexity, accuracy |
| Q3 | Mapping Config Format | YAML vs JSON vs Python module? | Simplicity vs dynamic logic |
| Q4 | DB Path Override | Env var `EXTRACTA_DB_PATH`? | Deployment flexibility |
| Q5 | Category Storage | Text field or FK table? | Integrity, rename semantics |
| Q6 | Derived Date Parts | Precompute month/year columns? | Query speed vs storage |
| Q7 | Aggregations Scope | Include median/min/max now? | Complexity vs immediate value |
| Q8 | Template Versioning | Track schema changes? | Backward compatibility |
| Q9 | Counterparty Parsing | Simple passthrough vs heuristic extraction? | Data quality/time to implement |
| Q10 | Log Destination | File rotation needed? | Operational stability |

Decisions pending will be resolved in Phase 0 research (`research.md`).

## 10. Risks & Mitigations
| Risk | Description | Mitigation |
|------|-------------|------------|
| OCR Accuracy | Poor extraction from low-quality images | Allow manual recategorization; log confidence (future) |
| Table Structure Variance | PDF tables with merged cells | Choose library with robust edge cases; fallback plain text parse |
| Performance Degradation | Large PDF > 500MB | Page-stream extraction; progress emission |
| Schema Drift | Untracked schema changes break reports | Version tables + migration scripts |
| User Data Loss | Accidental overwrite of DB | Use append-only normalization, backup on startup (copy if exists) |

## 11. Acceptance Criteria
1. Uploading a valid PDF with tabular transactions produces normalized rows visible in SQLite.
2. At least one image (.png or .jpg) with legible text results in parsed transactions (manual mock acceptable for MVP if OCR chosen but not yet integrated—flag recorded).
3. Categorization UI allows creating and assigning a new category to a transaction and persists on reload.
4. Report constructor can: filter by date range + category + income only; group by category; aggregate sum(amount_out); show both table and chart.
5. Saving a report template and reloading it restores identical table output.
6. Logs show structured JSON for each pipeline stage with counts and durations.
7. Re-running ingestion with same file produces identical `normalization_hash` values.

## 12. Out-of-Scope (Document Explicitly per Constitution)
- Multi-user identity & permissions.
- Encryption at rest (local developer environment assumption for MVP; future: optional DB encryption layer).
- Automated category inference (manual only initially).
- Real-time dashboards (on-demand only).

## 13. Implementation Outline (Preview)
High-level module grouping (actual paths finalized in `plan.md`):
```
src/
  ingestion/        # File routing, hashing, raw extraction
  extraction/       # PDF parser(s), OCR adapter(s)
  normalization/    # Mapping engine, validators, hashing
  persistence/      # SQLite gateway, migrations
  categorization/   # Category CRUD services
  reporting/        # Query builder, aggregation logic
  ui/               # Streamlit entrypoints & components
  logging/          # Structured logger utility
tests/
  unit/
  integration/
  contract/
```

## 14. Initial Test Matrix
| Test Type | Coverage |
|-----------|----------|
| Unit | Mapping rule resolution; amount split logic; hash determinism |
| Unit | PDF extraction adapter returns expected raw rows (mocked) |
| Unit | Categorization create + assign path |
| Integration | Full pipeline: upload -> normalized -> categorize -> report |
| Integration | Template save & reload idempotence |
| Contract | Transaction schema invariants (required fields) |

## 15. Logging Schema (JSON Lines)
Example line:
```json
{
  "ts":"2025-10-02T12:34:56.789Z",
  "stage":"normalization",
  "source_file":"statement_oct.pdf",
  "in_count":250,
  "out_count":250,
  "error_count":0,
  "duration_ms":842,
  "normalization_hash":"3fa09d...",
  "status":"success"
}
```

## 16. Data Integrity & Determinism Controls
- Use SHA256 for `source_file_hash` (file bytes) and for `normalization_hash` (concatenate ordered canonical field values + mapping_version + code_version).
- Maintain `NORMALIZATION_LOGIC_VERSION` constant updated when transformation logic changes (bump minor unless breaking schema → major).

## 17. Extension Hooks (Future)
| Hook | Purpose |
|------|---------|
| post_extraction(raw_artifact) | Add custom raw cleaning |
| pre_normalization(raw_row) | Filtering or enrichment |
| post_normalization(tx_row) | Additional derived fields |
| pre_report(query_params) | Policy injection or caching |

## 18. Glossary
| Term | Meaning |
|------|---------|
| Raw Artifact | Unmodified extracted structured data from a file |
| Normalization | Mapping & transformation into canonical fields |
| Categorization | User tagging of transactions with semantic labels |
| Report Template | Named persisted configuration of report constructor |

## 19. Open Decisions Tracking
Decisions from §9 transitioned here once resolved (with timestamps and rationale).

## 20. Approval
- Draft Reviewer(s): TBD
- Ready for Phase 0 Research Trigger: Once Q1-Q10 have owners & due decisions.

---
End of spec.
