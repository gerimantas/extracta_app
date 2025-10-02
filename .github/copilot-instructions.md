# Extracta Financial Data Pipeline - AI Agent Instructions

## Architecture Overview
Extracta is a **deterministic, local-first financial data normalization pipeline** that transforms heterogeneous financial documents (PDFs, images) into a unified, queryable transaction dataset. The system follows strict **Constitution principles**: data integrity, determinism, simplicity, and observability.

### Core Pipeline Flow
```
Raw Files → Ingestion → Extraction → Validation → Normalization → SQLite → Categorization → Reporting
```

## Project Structure & Conventions

### Module Organization
- `src/ingestion/`: File routing and raw extraction orchestration
- `src/extraction/`: PDF (pdfplumber) and image (OCR) text extraction
- `src/normalization/`: Validation, mapping, and deterministic hash computation
- `src/persistence/`: SQLite repository layer with migration support
- `src/categorization/`: User-defined transaction categorization
- `src/reporting/`: Query builder and template persistence
- `src/common/`: Shared utilities (hashing, mapping loaders)
- `src/logging/`: JSON line logging with schema compliance

### Critical Data Model
**Canonical Transaction Model** (see `extracta_app/contracts/transaction.schema.json`):
- Immutable fields: `source_file_hash`, `normalization_hash`, `mapping_version`, `logic_version`
- Mutual exclusivity: Only one of `amount_in` OR `amount_out` can be > 0
- Deterministic hashing follows specific field ordering in `src/common/hashing.py`

## Development Patterns

### Testing Strategy
- **Contract-first**: JSON schemas in `contracts/` with validation tests in `tests/contract/`
- **TDD approach**: Failing tests before implementation (see `specs/extracta-core/tasks.md`)
- **Test categories**: unit, integration, contract (use appropriate subdirectory)

### Hashing & Determinism
All normalization must be **deterministic**. Use `src/common/hashing.py`:
```python
# CANONICAL_FIELDS order MUST match data-model.md specification
CANONICAL_FIELDS = ("transaction_date", "description", "amount_in", "amount_out", ...)
```

### Import Patterns
```python
# Tests use this pattern (see tests/conftest.py)
from src.common.hashing import normalization_hash
from src.ingestion.pipeline import ingest_file

# Module imports for mocking in tests
from src.extraction import pdf_extractor, image_extractor
```

## Developer Workflows

### Testing Commands
```bash
# Quick tests (preferred for TDD cycles)
.venv\Scripts\python.exe -m pytest -q

# Verbose output for debugging
.venv\Scripts\python.exe -m pytest -vv

# Or use VS Code tasks: "tests:quick", "tests:verbose"
```

### Key Dependencies
- **pdfplumber**: PDF table/text extraction
- **pytesseract**: OCR for images  
- **jsonschema**: Contract validation
- **streamlit**: UI layer (thin, business logic in src/)

## Architecture Decisions

### File Type Routing
`src/ingestion/router.py` enforces supported formats: `.pdf` → PDF extractor, `.png/.jpg/.jpeg` → image extractor. Unsupported extensions raise `ValueError` (explicit design decision).

### Normalization Engine
Two-stage process in `src/normalization/engine.py`:
1. **Validation**: Required columns, date parsing, anomaly collection
2. **Mapping**: Header mapping via YAML config, canonical field transformation

### Append-Only Transactions
SQLite `transactions` table is append-only. Categorization updates only the `category_id` FK field, preserving immutable normalization hashes.

### JSON Logging
`src/logging/json_logger.py` emits schema-compliant log lines with auto-timestamping and configurable stack trace truncation (default: 20 lines).

## Working with This Codebase

1. **Follow the task list**: `extracta_app/specs/extracta-core/tasks.md` provides TDD sequence
2. **Check contracts first**: Validate against JSON schemas in `contracts/`
3. **Maintain determinism**: Any changes to normalization logic require hash verification
4. **Test categories**: Use appropriate test subdirectory (unit/integration/contract)
5. **Schema alignment**: Keep data model, JSON schemas, and database DDL synchronized

### Common Commands
```bash
# Run specific test categories
python -m pytest tests/unit/ tests/contract/
python -m pytest tests/integration/ -v

# Schema validation during development
python -c "import jsonschema; ..."  # See contract tests for examples
```

## Key Files for Context
- `specs/extracta-core/spec.md`: Complete feature specification
- `specs/extracta-core/data-model.md`: Database schema and constraints  
- `specs/extracta-core/tasks.md`: Development task sequence (TDD)
- `contracts/*.schema.json`: Data contracts and validation rules
- `src/common/hashing.py`: Deterministic hash implementation (critical for integrity)