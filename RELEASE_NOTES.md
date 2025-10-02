# Extracta v0.1.0 Release Notes

## Overview

Extracta 0.1.0 is the initial release of a **deterministic, local-first financial data normalization pipeline** that transforms heterogeneous financial documents (PDFs, images) into a unified, queryable transaction dataset.

## Architecture & Principles

This release is built on the **Constitution principles**:
- **Data Integrity**: Immutable normalization hashes and append-only transaction storage
- **Determinism**: Reproducible results across runs with stable hash computation
- **Simplicity**: Clean separation of concerns across pipeline stages
- **Observability**: Comprehensive JSON line logging with schema compliance

## Core Features

### 📄 Document Processing Pipeline
- **PDF Extraction**: Text and table extraction using pdfplumber
- **Image OCR**: Optical character recognition via pytesseract/Tesseract
- **File Routing**: Automatic format detection and appropriate extractor assignment
- **Raw Data Preservation**: Complete audit trail of original extractions

### 🔄 Data Normalization Engine
- **Two-Stage Process**: Validation followed by field mapping
- **YAML Configuration**: Human-readable mapping configurations
- **Canonical Model**: Standardized transaction schema with mutual exclusivity constraints
- **Version Tracking**: Logic and mapping version embedded in normalization hashes

### 💾 SQLite Persistence Layer
- **Local Database**: No external dependencies, file-based storage
- **Migration Support**: Schema evolution with automated migration tracking
- **Append-Only Design**: Immutable transaction records with categorization updates
- **Performance Optimization**: Precomputed year/month columns for efficient queries

### 🏷️ Transaction Categorization
- **User-Defined Categories**: Flexible category management with CRUD operations
- **Foreign Key Design**: Clean separation between transactions and categories
- **Category Updates**: Non-destructive categorization changes

### 📊 Reporting & Query System
- **Template-Based Reports**: Reusable query templates with parameter substitution
- **Aggregation Support**: Sum, average, and count operations
- **Date Range Filtering**: Efficient temporal queries using precomputed date fields
- **Export Capabilities**: Multiple output formats for analysis

### 🖥️ Streamlit Web Interface
- **File Upload**: Drag-and-drop document processing
- **Transaction Management**: Browse, search, and categorize transactions
- **Report Generation**: Interactive report creation and template management
- **Real-Time Processing**: Live pipeline execution with progress feedback

## Technical Specifications

### Technology Stack
- **Runtime**: Python 3.12
- **PDF Processing**: pdfplumber (table/text extraction)
- **OCR Engine**: pytesseract + Tesseract (local image processing)
- **Database**: SQLite 3 with environment path override
- **Web UI**: Streamlit (thin presentation layer)
- **Configuration**: YAML mappings for human readability
- **Validation**: JSON Schema contracts for all data structures

### Quality Assurance
- **Test Coverage**: 81 passing tests across unit/integration/contract categories
- **Schema Validation**: All pipeline data validated against JSON contracts
- **Code Quality**: Ruff linting and mypy type checking
- **Determinism Testing**: Repeat-run verification for stable hash computation
- **Performance Testing**: Memory-bounded processing for large file support

### Logging & Observability
- **JSON Lines Format**: Machine-readable log entries with schema compliance
- **Log Rotation**: 10MB file rotation with configurable retention
- **Stack Trace Truncation**: 20-line limit for readable error reporting
- **Pipeline Events**: Complete audit trail of all processing stages

## Data Model & Constraints

### Canonical Transaction Schema
```json
{
  "transaction_date": "YYYY-MM-DD",
  "description": "string",
  "amount_in": "decimal (>=0)",
  "amount_out": "decimal (>=0)",
  "source_file_hash": "SHA-256",
  "normalization_hash": "SHA-256",
  "mapping_version": "semver",
  "logic_version": "semver"
}
```

### Key Constraints
- **Mutual Exclusivity**: Only one of `amount_in` OR `amount_out` can be > 0
- **Immutable Fields**: Hash fields and versions never change after creation
- **Deterministic Hashing**: Canonical field ordering ensures reproducible hashes
- **Append-Only Storage**: Transaction records are never modified, only categorized

## Research-Driven Decisions

This release incorporates solutions to 10 key architectural questions:

1. **PDF Library**: pdfplumber chosen for simpler dependencies vs Camelot
2. **OCR Strategy**: Local pytesseract for privacy and offline capability
3. **Config Format**: YAML mappings for human readability and maintenance
4. **Database Path**: Environment variable override (`EXTRACTA_DB_PATH`) with sensible default
5. **Category Model**: Foreign key design with dedicated categories table
6. **Date Optimization**: Precomputed year/month columns for query performance
7. **Aggregation Scope**: Limited to sum/avg/count for MVP simplicity
8. **Template Versioning**: Schema version tracking with migration support
9. **Counterparty Parsing**: Pass-through strategy (description field) for MVP
10. **Logging Format**: JSON Lines with rotation and structured error reporting

## File Structure

```
extracta/
├── src/                    # Core pipeline modules
│   ├── ingestion/         # File routing and orchestration
│   ├── extraction/        # PDF and image text extraction
│   ├── normalization/     # Validation and field mapping
│   ├── persistence/       # SQLite repository layer
│   ├── categorization/    # User-defined transaction categories
│   ├── reporting/         # Query builder and templates
│   ├── common/           # Shared utilities and hashing
│   └── logging/          # JSON line logging infrastructure
├── contracts/            # JSON schema validation contracts
├── tests/               # Comprehensive test suite
│   ├── unit/           # Module-level tests
│   ├── integration/    # End-to-end pipeline tests
│   └── contract/       # Schema validation tests
└── data/               # SQLite database and processed artifacts
```

## Usage Examples

### Command Line (Development)
```bash
# Install dependencies
pip install -r requirements.txt

# Run test suite
python -m pytest -q

# Start web interface
streamlit run extracta_app/src/ui/app.py
```

### Web Interface Workflow
1. **Upload Documents**: Drag PDF or image files to the upload area
2. **Review Extractions**: Verify raw text extraction quality
3. **Process Transactions**: Apply normalization and validation
4. **Categorize**: Assign transactions to user-defined categories
5. **Generate Reports**: Create and save query templates for analysis

## Limitations & Constraints

### Current Scope (v0.1.0)
- **File Formats**: PDF and image files only (no CSV, Excel, or API imports)
- **OCR Quality**: Dependent on image clarity and Tesseract accuracy
- **Mapping Complexity**: Simple field mapping (no complex transformations)
- **Aggregations**: Basic sum/avg/count only (no advanced analytics)
- **UI Complexity**: Streamlit limitations for advanced interactions

### Performance Characteristics
- **Memory Usage**: Streaming processing with configurable memory bounds
- **File Size Limits**: Tested with files up to moderate size (exact limits TBD)
- **Database Scale**: SQLite suitable for personal/small business use
- **Concurrent Users**: Single-user application (no multi-tenancy)

## Security & Privacy

### Data Protection
- **Local Processing**: All data remains on local machine
- **No External Calls**: No cloud services or external API dependencies
- **File-Based Storage**: SQLite database under user control
- **Hash-Based Integrity**: Cryptographic verification of data consistency

### Audit Trail
- **Immutable Records**: Original extractions preserved alongside normalized data
- **Version Tracking**: All processing logic versions recorded
- **Complete Logging**: Full pipeline execution history with timestamps
- **Deterministic Results**: Reproducible processing for compliance verification

## Development Status

### Implemented Features ✅
- Complete end-to-end pipeline from document upload to report generation
- All Constitution principles verified and enforced
- Comprehensive test coverage with passing integration tests
- Production-ready logging and error handling
- Full schema validation and contract compliance
- Deterministic processing with stable hash computation

### Future Enhancements (Post-0.1.0)
- Additional file format support (CSV, Excel, QIF, OFX)
- Advanced OCR preprocessing and accuracy improvements
- Complex field transformations and business rule engine
- Multi-user support with authentication and data isolation
- Advanced analytics and visualization capabilities
- API endpoints for programmatic access

## Installation & Setup

### Prerequisites
- Python 3.12+
- Tesseract OCR (for image processing)
- Git (for source installation)

### Quick Start
1. Clone repository: `git clone <repository-url>`
2. Create virtual environment: `python -m venv .venv`
3. Activate environment: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix)
4. Install dependencies: `pip install -r requirements.txt`
5. Run tests: `python -m pytest -q`
6. Start application: `streamlit run extracta_app/src/ui/app.py`

### Configuration
- **Database Path**: Set `EXTRACTA_DB_PATH` environment variable (default: `data/extracta.db`)
- **Log Level**: Configurable via Python logging configuration
- **Mapping Files**: YAML configurations in `config/` directory

## Support & Documentation

### Key Documentation
- **Specification**: `specs/extracta-core/spec.md` - Complete feature specification
- **Data Model**: `specs/extracta-core/data-model.md` - Database schema and constraints
- **Constitution**: `specs/extracta-core/constitution.md` - Architecture principles
- **Development Tasks**: `specs/extracta-core/tasks.md` - Implementation sequence

### Development Environment
- **Linting**: Ruff configuration in `pyproject.toml`
- **Type Checking**: mypy configuration in `mypy.ini`
- **Testing**: pytest with fixtures and contract validation
- **Version Management**: Automated SemVer in `VERSION` file

---

**Extracta v0.1.0** represents a solid foundation for local financial data processing with a focus on data integrity, deterministic behavior, and user control. The architecture supports extensibility while maintaining simplicity and reliability.