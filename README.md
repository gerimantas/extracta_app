# Extracta Financial Data Pipeline

**Version:** 0.1.0  
Status: Core pipeline + Advanced Document & Counterparty Management (Feature 002) integrated.

Extracta is a deterministic, local-first financial data normalization pipeline that transforms heterogeneous financial documents (PDFs, images) into a unified, queryable transaction dataset.

## Architecture

Extracta follows strict **Constitution principles**: data integrity, determinism, simplicity, and observability.

### Core Pipeline Flow
```
Raw Files → Ingestion → Extraction → Validation → Normalization → SQLite → Categorization → Reporting
```

## Features

- **Deterministic Processing**: Identical input files always produce identical normalized outputs
- **Local-First**: No external services required, all processing happens locally
- **Multi-Format Support**: PDF documents and images (PNG, JPG, JPEG)
- **Streamlit UI**: User-friendly interface for file upload, transaction management, and reporting
- **Document Registry (v2)**: Persistent `documents` table with source file hashing & idempotent backfill
- **Counterparty Derivation (v2)**: Deterministic heuristic to extract counterparties (merge/rename support)
- **Categorization**: Assign custom categories to transactions
- **Reporting**: Flexible query builder with grouping and aggregation
- **Template System**: Save and reuse report configurations

## Quick Start

### Prerequisites

- Python 3.12+
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd extracta
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Unix/MacOS:
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

Start the Streamlit UI:
```bash
streamlit run extracta_app/src/ui/app.py
```

Navigate to `http://localhost:8501` in your browser.

## Usage Workflow

### 1. Upload Documents
- Use the **Upload** section to upload PDF or image files
- View raw extraction preview
- Files are processed immediately upon upload

### 2. Review Transactions
	- Counterparty column (if derived) indicates heuristic result; unknowns can be renamed/merged later
- Navigate to **Transactions** section
- Review normalized transaction data
- Assign categories to transactions
- Create new categories as needed

### 3. Generate Reports
- Use **Reports** section to build custom queries
- Apply filters (date range, amount, description)
- Group by categories or time periods
- Choose aggregation functions (sum, count, average)

### 4. Save Templates
- Save frequently used report configurations as templates
- Access saved templates in **Templates** section
- Reload and modify existing templates

## Deterministic Re-run Guarantee

Extracta guarantees **deterministic processing**:

1. **Same Input → Same Output**: Processing the same file multiple times produces identical results
2. **Reproducible Hashes**: Each transaction gets a deterministic normalization hash
3. **Stable Ordering**: Results are consistently ordered across runs
4. **Version Tracking**: Mapping and logic versions ensure hash stability

### Verification Process

To verify deterministic behavior:

1. Process a file and note the transaction hashes
2. Process the same file again
3. Compare the results - they should be identical

The pipeline tracks:
- `source_file_hash`: SHA256 of the original file
- `normalization_hash`: Deterministic hash of normalized transaction data
- `mapping_version`: Version of field mapping rules
- `logic_version`: Version of normalization logic

## Data Model

### Core Transaction Schema

Each normalized transaction contains:

- `transaction_id`: Unique identifier (UUID)
- `transaction_date`: ISO date (YYYY-MM-DD)
- `description`: Transaction description
- `amount_in`: Positive amount (income) or 0.00
- `amount_out`: Positive amount (expense) or 0.00
- `category_id`: Optional category reference
- `source_file`: Original filename
- `source_file_hash`: File integrity hash
- `normalization_hash`: Data integrity hash
- `mapping_version`: Schema version
- `logic_version`: Processing version

**Constraint**: Only one of `amount_in` OR `amount_out` can be greater than 0.

## Testing

Run the test suite:

```bash
# Quick tests
python -m pytest -q

# Verbose output
python -m pytest -vv

# Specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/contract/
```

## Development

### Project Structure

```
extracta_app/
├── src/                      # Source code
│   ├── ingestion/            # File processing pipeline
│   ├── extraction/           # PDF and image extractors
│   ├── normalization/        # Validation, mapping, counterparty heuristic (v2)
│   ├── persistence/          # SQLite repositories & migrations (idempotent)
│   ├── document_management/  # (Future) extended doc ops placeholder
│   ├── categorization/       # Transaction categorization
│   ├── reporting/            # Query builder and execution
│   ├── ui/                   # Streamlit interface (includes document & counterparty sections)
│   ├── logging/              # JSON logging system
│   └── common/               # Shared utilities
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests (incl. determinism & derivation)
│   ├── contract/             # Schema validation tests
│   └── tooling/              # Development tool tests
├── contracts/                # JSON schemas
└── specs/                    # Documentation and specifications
```

### Code Quality

The project uses:
- **ruff**: Code linting and formatting
- **mypy**: Static type checking
- **pytest**: Testing framework
- **JSON Schema**: Contract validation

Run quality checks:
```bash
ruff check extracta_app/
mypy extracta_app/src/
```

### Runtime Artifacts & Local State
The SQLite DB and pipeline logs are intentionally NOT tracked in Git. They are ignored via `.gitignore`.

Reset local database (non-destructive to code):
```bash
rm data/extracta.db  # or del on Windows
python -c "from extracta_app.src.persistence.migrations import init_db; init_db()"
```
All migrations are idempotent; re-running `init_db()` will create missing structures only.

## License

[Add license information]

## Contributing

[Add contribution guidelines]