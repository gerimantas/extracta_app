# Traceability Matrix

Šis dokumentas suteikia atsekamumą tarp: Specifikacijų (spec.md), plano (plan.md), užduočių (tasks.md), kodo (source), testų ir papildomų kokybės / deterministinių / logging įrodymų.

Formatas: lietuviški paaiškinimai, anglų kalba – failų / testų pavadinimai.

Legenda:
- Status: Planned | Implemented | Deferred | Removed
- Determinism: Yes = aiškus hash / deterministinis guard testas; n/a = netaikoma
- Logging: išvardinti pagrindiniai event_type ar stage reikšmės
- Notes: papildomos pastabos (idempotency, fallback, edge cases)

---
## 1. Feature 001 – Core Pipeline

| Feature | Spec Section | Plan Ref | Task ID(s) | Code (Primary) | Tests (Key) | Determinism | Logging | Status | Notes |
|---------|--------------|----------|------------|----------------|-------------|-------------|---------|--------|-------|
| 001 Research decisions | §9 Open Questions | research.md | 1 | specs/extracta-core/research.md | (implicit referenced) | n/a | n/a | Implemented | Q1–Q10 resolved (pdfplumber, Tesseract, YAML, etc.) |
| 001 Data model + hash algo | §6 Canonical Model | data-model.md | 2 | specs/extracta-core/data-model.md | tests/unit/test_hashing.py | Yes | n/a | Implemented | Field ordering stable |
| 001 Quickstart | §11 Acceptance | quickstart.md | 3 | specs/extracta-core/quickstart.md | tests/tooling/test_readme.py | n/a | n/a | Implemented | Documents end-to-end flow |
| 001 Transaction schema | §6 | plan Schema | 5,8 | contracts/transaction.schema.json | tests/contract/test_transaction_schema.py | n/a | n/a | Implemented | Required + invalid cases |
| 001 Log event schema | §5.6 | plan Observability | 6,9 | contracts/log-event.schema.json | tests/contract/test_log_event_schema.py | n/a | ingestion/normalization/etc. | Implemented | Counts & error fields validated |
| 001 Report request schema | §5.5 | plan Reporting | 7,10 | contracts/report-request.schema.json | tests/contract/test_report_request_schema.py | n/a | n/a | Implemented | Aggregations validation |
| 001 Hash utilities | §8 NFR Determinism | plan Common Utils | 11–12 | src/common/hashing.py | tests/unit/test_hashing.py | Yes | n/a | Implemented | normalization_hash composite |
| 001 JSON logger | §5.6 Observability | plan Logging | 13–14 | src/logging/json_logger.py | tests/integration/test_logging_events.py | n/a | stage based | Implemented | Stack trace truncation |
| 001 Mapping loader | §5.3 Normalization | plan Mapping | 15–16 | src/common/mapping_loader.py | tests/unit/test_mapping_loader.py | n/a | n/a | Implemented | Synonym precedence |
| 001 Ingestion router | §5.1 Ingestion | plan Ingestion | 17–18 | src/ingestion/router.py | tests/unit/test_ingestion_router.py | n/a | ingestion | Implemented | Rejects unsupported ext |
| 001 PDF extractor | §5.1 | plan Extraction | 19–20 | src/extraction/pdf_extractor.py | tests/unit/test_pdf_extractor.py | n/a | ingestion | Implemented | pdfplumber stub logic |
| 001 Image OCR extractor | §5.1 | plan Extraction | 21–22 | src/extraction/image_extractor.py | tests/unit/test_image_ocr_extractor.py | n/a | ingestion | Implemented | pytesseract adapter |
| 001 Raw artifact orchestration | §5.1 | plan Ingestion Orchestration | 23–24 | src/ingestion/pipeline.py | tests/integration/test_raw_artifact_structure.py | n/a | ingestion | Implemented | Metadata correctness |
| 001 Validation rules | §5.2 Validation | plan Validation | 25–26 | src/normalization/validation.py | tests/unit/test_validation_rules.py | n/a | n/a | Implemented | Soft vs hard failures |
| 001 Mapping + sign inference | §5.3 | plan Mapping | 27–28 | src/normalization/mapping.py | tests/unit/test_normalization_mapping.py | n/a | n/a | Implemented | amount_in/out exclusivity |
| 001 Normalization engine | §5.3 | plan Engine | 29–30 | src/normalization/engine.py | tests/unit/test_normalization_determinism.py | Yes | normalization | Implemented | Wraps validation+mapping |
| 001 DB migrations (v1) | §5.4 Persistence | plan Persistence | 31–32 | src/persistence/migrations.py | tests/unit/test_persistence_schema.py | n/a | n/a | Implemented | Idempotent init_db |
| 001 Transactions repository | §5.4 | plan Persistence | 33–34 | src/persistence/transactions_repository.py | tests/unit/test_transaction_insert.py | n/a | n/a | Implemented | Append-only |
| 001 Category CRUD | §5.4 | plan Categorization | 35–36 | src/categorization/service.py | tests/unit/test_category_crud.py | n/a | n/a | Implemented | Rename preserved |
| 001 Reporting query builder | §5.5 Reporting | plan Query Builder | 37–38 | src/reporting/query_builder.py | tests/unit/test_report_query_builder.py | n/a | n/a | Implemented | Multi-group support |
| 001 Reporting executor | §5.5 | plan Executor | 39–40 | src/reporting/executor.py | tests/unit/test_report_execution.py | n/a | n/a | Implemented | Aggregations sum/avg/count |
| 001 Templates persistence | §5.5 | plan Templates | 41–42 | src/reporting/templates.py | tests/unit/test_template_store.py | n/a | n/a | Implemented | JSON serialization |
| 001 Streamlit UI core | §5.* | plan UI | 43–44 | src/ui/app.py | tests/integration/test_ui_smoke.py | n/a | n/a | Implemented | Thin layer pattern |
| 001 End-to-end pipeline | §11 Acceptance | plan E2E | 45 | (multiple modules) | tests/integration/test_end_to_end_pipeline.py | Yes (implicit) | ingestion/normalization | Implemented | Cross-module flow |
| 001 Logging integration | §5.6 | plan Observability | 47–48 | src/logging/json_logger.py | tests/integration/test_logging_events.py | n/a | stage events | Implemented | Schema compliance |
| 001 Repeat determinism | §8 | plan Determinism | 49–50 | src/common/hashing.py | tests/integration/test_repeat_run_determinism.py | Yes | n/a | Implemented | Stable hashes |
| 001 Large file simulation | §8 Performance | plan Performance | 51–52 | (ingestion paths) | tests/integration/test_large_file_simulation.py | n/a | n/a | Implemented (or skipped) | Memory guard |
| 001 Tooling (ruff/mypy) | §8 NFR | plan Tooling | 53–54 | pyproject.toml, mypy.ini | tests/tooling/test_lint_config_present.py | n/a | n/a | Implemented | Quality gates |
| 001 Versioning + README | §11 Acceptance | plan Release | 55–56 | VERSION, README.md | tests/tooling/test_readme.py | n/a | n/a | Implemented | SemVer validated |
| 001 Release notes | §11 | plan Release | 61 | RELEASE_NOTES.md | (review) | n/a | n/a | Implemented | v0.1.0 base |

---
## 2. Feature 002 – Advanced Document & Entity Management

| Feature | Spec Section | Plan Ref | Task ID(s) | Code (Primary) | Tests (Key) | Determinism | Logging | Status | Notes |
|---------|--------------|----------|------------|----------------|-------------|-------------|---------|--------|-------|
| 002 Schema v2 (tables) | §2 Data Model | plan §§2,4 | 0.1–0.4 | src/persistence/migrations.py | tests/integration/test_migration_documents_counterparties.py | n/a | n/a | Implemented | documents, counterparties, FK |
| 002 Documents backfill | §2 Backfill | plan §2 | 0.3 | migrations.py | test_migration_documents_counterparties.py | n/a | document_create | Implemented | Distinct file hashes |
| 002 Counterparty heuristic | §5 Heuristic | plan §5 | 1.1–1.5 | src/normalization/counterparty_heuristic.py | tests/unit/test_counterparty_heuristic.py | Yes | counterparty_autoderive_fail | Implemented | Stopwords + longest token |
| 002 Heuristic token normalization | §5 Heuristic | plan §5 | 1.2 | src/normalization/counterparty_heuristic.py | tests/unit/test_counterparty_heuristic.py | Yes | n/a | Implemented | Lowercase + strip |
| 002 Heuristic filtering & selection | §5 Heuristic | plan §5 | 1.3 | src/normalization/counterparty_heuristic.py | tests/unit/test_counterparty_heuristic.py | Yes | n/a | Implemented | Longest contiguous tokens |
| 002 Heuristic fallback Unknown | §5 Heuristic | plan §5 | 1.4 | src/normalization/counterparty_heuristic.py | tests/unit/test_counterparty_heuristic.py | Yes | n/a | Implemented | <3 chars → Unknown |
| 002 Documents repository | §2 Persistence | plan §2 | 2.1–2.2 | src/persistence/documents_repository.py | tests/unit/test_repositories_documents_counterparties.py | n/a | document_create/delete | Implemented | Cascade delete count |
| 002 Counterparties get_or_create | §2 Persistence | plan §7 | 2.3 | src/persistence/counterparties_repository.py | tests/unit/test_repositories_documents_counterparties.py | n/a | n/a | Implemented | Case-insensitive |
| 002 Counterparties rename | §2 Persistence | plan §7 | 2.4 | src/persistence/counterparties_repository.py | tests/unit/test_repositories_documents_counterparties.py | n/a | counterparty_rename | Implemented | Collision raises |
| 002 Counterparties repository | §2 Persistence | plan §7 | 2.1–2.5 | src/persistence/counterparties_repository.py | tests/unit/test_repositories_documents_counterparties.py | n/a | counterparty_merge/rename | Implemented | Merge reassigns |
| 002 Upload doc_type selector | §1 Upload Flow | plan §1 | 3.1–3.2 | src/ui/app.py | tests/unit/test_upload_document_type_selector.py | n/a | document_create | Implemented | Default 'Other' |
| 002 Document create log | §8 Logging | plan §8 | 3.3 | documents_repository.py | tests/integration/test_logging_document_create.py | n/a | document_create | Implemented | Fields validated |
| 002 Counterparty derivation integration | §5 Integration | plan §5 | 4.1–4.3 | src/normalization/counterparty_derivation.py | tests/integration/test_counterparty_derivation_pipeline.py | Yes | counterparty_autoderive_fail | Implemented | Idempotent run |
| 002 Derivation assignment | §5 Integration | plan §5 | 4.2 | src/normalization/counterparty_derivation.py | tests/integration/test_counterparty_derivation_pipeline.py | Yes | n/a | Implemented | Skip if already assigned |
| 002 Document Management UI | §6 UI | plan §6 | 5.1–5.4 | src/ui/app.py (document_management_section) | tests/integration/test_ui_document_tab.py | n/a | document_delete | Implemented | Delete cascade |
| 002 Counterparty Management UI | §7 UI | plan §§7,8 | 6.1–6.5 | src/ui/app.py (counterparty_management_section) | tests/integration/test_ui_counterparty_management.py | n/a | counterparty_merge/rename | Implemented | Filter, rename, merge |
| 002 Counterparty list & filter | §7 UI | plan §7 | 6.2 | src/ui/app.py | tests/integration/test_ui_counterparty_management.py | n/a | n/a | Implemented | Text filter |
| 002 Counterparty rename action | §7 UI | plan §7 | 6.3 | src/ui/app.py | tests/integration/test_ui_counterparty_management.py | n/a | counterparty_rename | Implemented | Refresh after rename |
| 002 Counterparty merge action | §7 UI | plan §7 | 6.4 | src/ui/app.py | tests/integration/test_ui_counterparty_management.py | n/a | counterparty_merge | Implemented | Reassign losing IDs |
| 002 Merge & rename integrity | §7 Edge Cases | plan §7 | 7.3 | counterparties_repository.py | tests/unit/test_repositories_documents_counterparties.py | n/a | counterparty_merge | Implemented | Second merge no-op |
| 002 Perf placeholder | §7 Performance | plan §7 | 7.1–7.2 | tests/performance/test_counterparty_merge_perf.py | (skipped) | n/a | n/a | Deferred | Benchmark future |
| 002 Logging contract (new events) | §8 Logging | plan §8 | 8.1–8.2 | logging/json_logger usage | tests/contract/test_logging_new_events.py | n/a | all new events | Implemented | Key presence |
| 002 Log ordering test (optional) | §8 Optional | plan §8 | 8.3 | (none) | (none) | n/a | n/a | Deferred | Marked optional |
| 002 Determinism guard stable | §9 Determinism | plan §9 | 9.1–9.2 | tests/integration/test_hash_determinism_guard.py | tests/integration/test_hash_determinism_guard.py | Yes | n/a | Implemented | Stable before/after |
| 002 Determinism negative control | §9 Determinism | plan §9 | 9.3 | test_hash_determinism_guard.py | same | Yes | n/a | Implemented | Active (not skipped) |
| 002 Acceptance test | §12 Acceptance | plan §12 | 10.1 | tests/integration/test_acceptance_feature_002.py | tests/integration/test_acceptance_feature_002.py | Yes (indirect) | all feature events | Implemented | Consolidated |
| 002 Acceptance report artifact | §12 Reporting | plan §12 | 10.2 | scripts/generate_feature_002_report.py | artifact generation | n/a | n/a | Implemented | `artifacts/feature_002_acceptance_report.txt` |

---
## 3. Determinism Coverage Santrauka
- Feature 001: `tests/integration/test_repeat_run_determinism.py` + hashing unit tests.
- Feature 002: Stabilumo guard + neigiamas kontrolinis (`test_hash_changes_when_input_changes`).

## 4. Deferred Items
| Item | Feature | Priežastis | Galimas Follow-up |
|------|---------|-----------|-------------------|
| Perf benchmark (real dataset) | 002 | MVP scope + laiko sąnaudos | Sukurti synthetic generator + matuoti <5s tikslą |
| Log field ordering assertion | 002 | Maža rizika | Pridėti paprastą raktų seka testą |
| OCR retry strategija | 001 | Ne kritinė MVP | Feature 003 (Resilience) |

## 5. Keitimo Politika
- Naują eilutę pridėti PR'e su nauju Feature ID / Task ID.
- Esamų eilučių NETRINTI – pakeisti Status (pvz. → Removed) jei nebenaudojama.
- Po migracijų – atnaujinti atitinkamą schema/feature bloką.

## 6. Validacijos Idėja (pasirinktina CI)
Python skriptas (pseudo): surinkti Task ID iš `tasks.md` failų ir patikrinti, ar kiekvienas ID egzistuoja šioje matricoje; jei ne – CI blokas.

---
*(Generated traceability matrix for Features 001 & 002 – keep updated with future features.)*
