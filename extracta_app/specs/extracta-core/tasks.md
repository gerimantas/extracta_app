# Tasks: Feature 001 – Extracta Core Pipeline

Origin: `specs/main/plan.md` (Phase 2 task generation)  
Principles: Follow Constitution (data integrity, determinism, simplicity, observability)  
Ordering: TDD (tests & schemas before implementation)  
Tag Legend: [P] = Can be executed in parallel (no dependency on earlier unfinished tasks)

> NOTE: If any prerequisite artifact (research.md, data-model.md, schemas) is missing, create it in the related task before proceeding. Do not skip failing tests—they must fail first, then be made to pass.

## A. Foundational Decisions & Documentation
1. Create/Finalize `specs/extracta-core/research.md` resolving Q1–Q10 with Decisions, Rationale, Alternatives. Output summary hash. (Fail if any unresolved.)
2. Create `specs/extracta-core/data-model.md` with: canonical Transaction Model, migration strategy, index plan, field constraints, normalization hash algorithm pseudo-code.
3. Create `specs/extracta-core/quickstart.md` describing end-to-end run (upload → normalize → categorize → report → template save/load) including deterministic re-run check.
4. Update wrapper spec summary hash (`SPEC_SUMMARY_SHA_PLACEHOLDER`) after decisions locked. (Dependent on Task 1.)

## B. Contracts (Schemas) – Tests First
5. Write JSON Schema draft for Transaction: `contracts/transaction.schema.json` (include required fields, type constraints, regex for date). [P]
6. Write JSON Schema draft for Log Event: `contracts/log-event.schema.json` (stage, timestamps, counts, hashes). [P]
7. Write JSON Schema draft for Report Request: `contracts/report-request.schema.json` (filters, grouping[], aggregation{field,func}, view_mode). [P]
8. Add failing contract test `tests/contract/test_transaction_schema.py` validating a minimal valid & several invalid samples (missing field, wrong date format). (After Task 5)
9. Add failing contract test `tests/contract/test_log_event_schema.py` (missing stage, negative counts). (After Task 6)
10. Add failing contract test `tests/contract/test_report_request_schema.py` (invalid aggregation func, empty grouping allowed?). (After Task 7)

## C. Core Utilities (Hashing, Logging, Config) – Tests Then Impl
11. Add failing unit test for hashing utility (`tests/unit/test_hashing.py`): asserts deterministic SHA256 for file bytes + normalization hash composition ordering.
12. Implement `src/common/hashing.py` with `file_sha256(path)` + `normalization_hash(row_dict, mapping_version, logic_version)` to satisfy test.
13. Add failing unit test for JSON logger format (`tests/unit/test_logging_format.py`) referencing log schema (no implementation yet).
14. Implement `src/logging/json_logger.py` producing schema-compliant lines + stack trace truncation (configurable; default 20 lines).
15. Add failing unit test for mapping config loader (`tests/unit/test_mapping_loader.py`) expecting YAML parse + synonym resolution order.
16. Implement `src/common/mapping_loader.py` with precedence: file-pattern overrides > explicit header map > synonyms fallback.

## D. Ingestion & Extraction Pipeline
17. Add failing unit test `tests/unit/test_ingestion_router.py` verifying file type detection (.pdf/.png/.jpg) and rejection of unsupported extensions.
18. Implement `src/ingestion/router.py` returning extractor strategy tokens (e.g., `pdf`, `image`).
19. Add failing unit test `tests/unit/test_pdf_extractor.py` mocking pdfplumber to return sample rows; assert structure.
20. Implement `src/extraction/pdf_extractor.py` using pdfplumber (graceful fallback if tables absent → textual row parse stub).
21. Add failing unit test `tests/unit/test_image_ocr_extractor.py` mocking pytesseract to return sample tabular lines.
22. Implement `src/extraction/image_extractor.py` (basic OCR pass + rudimentary row splitting; mark confidence TODO comment).
23. Add failing integration-ish test `tests/integration/test_raw_artifact_structure.py` asserting raw artifact metadata (source_file_hash, extraction_method, record_count_raw).
24. Implement `src/ingestion/pipeline.py` orchestrating: hash file -> route -> extract -> return raw artifact (no DB writes yet).

## E. Validation & Normalization
25. Add failing unit test `tests/unit/test_validation_rules.py` for: non-empty rows, date parse fallback, amount column presence.
26. Implement `src/normalization/validation.py` raising on hard failures, collecting soft anomalies.
27. Add failing unit test `tests/unit/test_normalization_mapping.py` verifying header mapping to canonical fields and single-amount sign inference.
28. Implement `src/normalization/mapping.py` to transform raw rows to canonical dicts (no DB yet), zeroing opposite amount field.
29. Add failing unit test `tests/unit/test_normalization_determinism.py` ensuring identical input + mapping_version yields identical hashes.
30. Implement `src/normalization/engine.py` (wraps validation + mapping + hash computation) returning normalized rows list/iterator.

## F. Persistence & Categorization
31. Add failing unit test `tests/unit/test_persistence_schema.py` asserting tables (transactions, categories, report_templates, schema_version) not present yet (expect failure until created) then will pass after migration.
32. Implement `src/persistence/migrations.py` with `init_db()` creating tables (idempotent) & schema version record.
33. Add failing unit test `tests/unit/test_transaction_insert.py` (inserts normalized rows; asserts row count & fields). (Depends on Task 32)
34. Implement `src/persistence/transactions_repository.py` with bulk insert (append-only) + fetch by filters.
35. Add failing unit test `tests/unit/test_category_crud.py` (create, list, rename, assign to tx, prevent delete if in use / or cascade confirm TBD—decide in research). (After Task 32)
36. Implement `src/categorization/service.py` with CRUD + assignment logic.

## G. Reporting Engine
37. Add failing unit test `tests/unit/test_report_query_builder.py` building SQL (or Pandas pipeline) for filters + grouping + aggregation; snapshot expected structure.
38. Implement `src/reporting/query_builder.py` supporting multi-level grouping and sum/avg/count on amount fields.
39. Add failing unit test `tests/unit/test_report_execution.py` (seed small dataset -> run report request -> validate aggregated numbers).
40. Implement `src/reporting/executor.py` executing built queries, returning rows + metadata (for chart/table).
41. Add failing unit test `tests/unit/test_template_store.py` (save template, reload by name, idempotent load).
42. Implement `src/reporting/templates.py` persisting templates (SQLite table) with JSON serialization + version field.

## H. Streamlit UI (Thin Layer)
43. Add failing UI smoke test (headless) `tests/integration/test_ui_smoke.py` (import app module -> assert constructs layout sections). (Can be minimal.)
44. Implement `src/ui/app.py` pages/sections: Upload, Transactions (categorize), Reports (constructor), Templates (save/load).
45. Add failing integration test `tests/integration/test_end_to_end_pipeline.py` (simulate: ingest fixture PDF -> normalize -> insert -> categorize -> build report -> create template -> reload template). Use in-memory or temp DB path.
46. Provide minimal fixture sample files under `tests/fixtures/` (one PDF stub, one image stub) + fallback mocks if binary heavy.

## I. Logging & Observability Integration
47. Add failing integration test `tests/integration/test_logging_events.py` ensuring each pipeline stage emits a schema-valid log line.
48. Integrate logger calls across ingestion, normalization, persistence, reporting modules (update existing code only after test added).

## J. Determinism & Performance
49. Add failing determinism test `tests/integration/test_repeat_run_determinism.py` (two runs same file produce identical normalization hashes & row counts).
50. Implement minor adjustments (sorting order, stable field ordering) to satisfy determinism test.
51. Add performance smoke test `tests/integration/test_large_file_simulation.py` (simulate large dataset in memory generator; assert streaming path prevents > X memory usage via rough sample). (May mark as skipped if environment constrained.)
52. Optimize any hotspots identified (only if needed to pass performance assertions) & document in research addendum.

## K. Tooling & Quality Gates
53. Add `ruff` config + (optional) `mypy` basic config; introduce failing lint test stage script (`tests/tooling/test_lint_config_present.py`).
54. Apply lint fixes / minimal type hints until tooling test passes.
55. Add `VERSION` file and `src/common/version.py`; unit test verifying SemVer pattern & alignment with docs.
56. Add `README.md` minimal usage & deterministic re-run section; doc test (regex check) in `tests/tooling/test_readme.py`.

## L. Final Integration & Cleanup
57. Run full test suite; address failures; ensure all schema references synchronized.
58. Post-Design Constitution Check: review code vs Constitution; update `plan.md` gate checkbox.
59. Add optional `cli.py` entrypoint (if justified) AFTER confirming not adding unnecessary complexity (skip if UI sufficient). [P]
60. Update agent context file via provided script (record new libs & resolved decisions Q1–Q10).
61. Prepare release notes draft (0.1.0) summarizing implemented features & constraints.

## Parallelization Guidance
- Tasks marked [P] (5,6,7,59) can proceed concurrently once their direct predecessors exist.
- Avoid parallel edits to the same module directory to reduce merge complexity.

## Completion Criteria
- All tests green (unit + contract + integration + tooling).
- Determinism test stable across two consecutive full runs.
- Logging lines validate against schema with zero schema violations.
- No unresolved NEEDS CLARIFICATION entries in research file.

---
End of tasks.
