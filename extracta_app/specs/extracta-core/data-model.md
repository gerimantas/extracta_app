# Data Model – Feature 001 (Extracta Core Pipeline)

Date: 2025-10-02  
Aligned Spec: `specs/extracta-core/spec.md`  
Research Decisions Hash: `2e9df42f6c805af31e0497de912e5c277ab43aa73a9e1bac085517d660d7b6b8`

## 1. Overview
The data model supports deterministic, auditable financial transaction ingestion, normalization, categorization, reporting, and template persistence. SQLite is used for local single‑user storage with explicit versioning & forward migrations. The canonical Transaction Model is append‑only; user actions (categorization) modify non-hash-affecting fields only.

## 2. Entities
| Entity | Purpose | Notes |
|--------|---------|-------|
| transactions | Canonical normalized transactions | Append-only inserts; category assignment updates FK only |
| categories | User-defined category labels | Single category per transaction (FK) |
| report_templates | Saved report constructor configurations | Includes schema + logic + mapping version references |
| schema_version | Tracks DB schema version integer + semver string | Single-row control table |
| (future) anomalies_log | Soft anomalies emitted during validation | Deferred (not MVP) |

## 3. Canonical Transaction Model (Logical)
| Field | Type (SQLite) | Required | Default | Description | Constraints |
|-------|---------------|----------|---------|-------------|-------------|
| transaction_id | TEXT (UUID) | Yes | gen | Primary key | Length 36 |
| transaction_date | TEXT (YYYY-MM-DD) | Yes | — | ISO date | CHECK valid format (app-level) |
| description | TEXT | Yes | — | Raw/cleaned description | Non-empty |
| amount_in | REAL | Yes | 0.0 | Incoming amount | >=0; mutually exclusive with amount_out |
| amount_out | REAL | Yes | 0.0 | Outgoing amount | >=0; mutually exclusive with amount_in |
| counterparty | TEXT | Yes | '' | Pass-through description (MVP) | May revisit heuristics |
| category_id | TEXT (FK) | No | NULL | Assigned category | FK → categories.id |
| source_file | TEXT | Yes | — | Original filename | Immutable |
| source_file_hash | TEXT | Yes | — | SHA256 of file bytes | 64 hex chars |
| normalization_hash | TEXT | Yes | — | Determinism hash of row | 64 hex chars |
| mapping_version | TEXT | Yes | — | From YAML mapping | Used in hash |
| logic_version | TEXT | Yes | — | NORMALIZATION_LOGIC_VERSION | Used in hash |
| year | INTEGER | Yes | derive | Year extracted from date | 4-digit |
| month | TEXT (YYYY-MM) | Yes | derive | Year-month convenience | 7 chars |
| created_at | TIMESTAMP | Yes | CURRENT_TIMESTAMP | Insert time | — |

### Mutual Exclusivity Constraint
Exactly one of `amount_in` or `amount_out` is > 0 (or both zero if an informational row filtered later). Constraint enforced:
```
CHECK (NOT(amount_in > 0 AND amount_out > 0))
```

Additional app-level validation ensures at least one non-zero for a valid transaction row unless classification marks it ignorable (future enrich stage).

## 4. SQLite DDL (Initial Migration)
```sql
CREATE TABLE IF NOT EXISTS schema_version (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  major INTEGER NOT NULL,
  minor INTEGER NOT NULL,
  patch INTEGER NOT NULL,
  semver TEXT NOT NULL,
  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
  transaction_id TEXT PRIMARY KEY,
  transaction_date TEXT NOT NULL,
  description TEXT NOT NULL,
  amount_in REAL NOT NULL DEFAULT 0.0,
  amount_out REAL NOT NULL DEFAULT 0.0,
  counterparty TEXT NOT NULL DEFAULT '',
  category_id TEXT NULL,
  source_file TEXT NOT NULL,
  source_file_hash TEXT NOT NULL,
  normalization_hash TEXT NOT NULL,
  mapping_version TEXT NOT NULL,
  logic_version TEXT NOT NULL,
  year INTEGER NOT NULL,
  month TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categories(id),
  UNIQUE (normalization_hash),
  CHECK (NOT(amount_in > 0 AND amount_out > 0))
);

CREATE TABLE IF NOT EXISTS report_templates (
  name TEXT PRIMARY KEY,
  payload JSON NOT NULL,
  template_schema_version INTEGER NOT NULL,
  mapping_version TEXT NOT NULL,
  logic_version TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

NOTE: SQLite older versions may not enforce JSON data type—payload accepted as TEXT; validation handled at application layer.

## 5. Index Strategy
| Index | Columns | Purpose |
|-------|---------|---------|
| idx_transactions_date | transaction_date | Range filtering for reports |
| idx_transactions_year_month | year, month | Grouping acceleration |
| idx_transactions_category | category_id | Category filtering |
| idx_transactions_source | source_file | Provenance queries |
| idx_templates_version | template_schema_version | Future migrations / filtering |

Normalization hash uniqueness acts as duplicate prevention (idempotent re-runs).

## 6. Data Integrity & Determinism
### Fields Included in normalization_hash
Ordered field list (exact ordering is critical):
```
[transaction_date, description, amount_in, amount_out, counterparty, source_file, source_file_hash, year, month]
```
Plus appended metadata: `mapping_version`, `logic_version`.

Excluded: `category_id`, `created_at` (user or temporal concerns), template relations.

### Pseudocode: Normalization Hash
```python
def normalization_hash(row, mapping_version: str, logic_version: str) -> str:
    canonical_order = [
        row['transaction_date'],
        row['description'],
        f"{row['amount_in']:.2f}",
        f"{row['amount_out']:.2f}",
        row['counterparty'],
        row['source_file'],
        row['source_file_hash'],
        str(row['year']),
        row['month']
    ]
    base = '|'.join(canonical_order) + f"|{mapping_version}|{logic_version}"
    return sha256_utf8(base)
```
Determinism Requirements:
1. All numeric formatting normalized to fixed decimal string (2 places) before hashing.
2. No locale-dependent formatting.
3. Mapping & logic versions must be stable strings; bump logic_version if transformation semantics change.

## 7. Migration Strategy
| Change Type | Action | Version Bump | Notes |
|-------------|--------|--------------|-------|
| Add non-nullable column (no default) | Two-step: add nullable, backfill, enforce | Minor (if backward compatible reads) or Major | Avoid break by planning backfill |
| Add nullable / optional column | Simple add | Minor | Document in spec |
| Add index | Create concurrently (N/A in SQLite) | Patch | Performance only |
| Change semantics of existing column | New column + deprecate old | Major | Preserve determinism by not rewriting old rows |
| Remove column | Only after deprecation & migration note | Major | Provide migration script |
| Adjust constraint without data rewrite | Evaluate risk | Minor or Major | If might break existing inserts -> Major |

`schema_version.semver` tracks (MAJOR.MINOR.PATCH). Migration script inserts/updates row id=1.

## 8. Validation Rules (App-Level)
1. `transaction_date` must parse to valid date; reject rows failing parse.
2. Exactly one of `amount_in`, `amount_out` > 0 (or both zero only if flagged anomaly – not persisted by normalization engine unless rule updated).
3. `amount_in` and `amount_out` must be finite (not NaN/inf).
4. `source_file_hash` must be 64 hex characters.
5. `normalization_hash` uniqueness enforced; duplicate normalization attempt results in skip (log event with status `duplicate`).
6. Category assignment must reference existing category id.

## 9. Reporting Query Assumptions
Aggregation limited to `sum`, `avg`, `count` over `amount_in` or `amount_out` (never both simultaneously in same value expression). Grouping fields allowed: `category_id`, `counterparty`, `month`, `year`, `source_file`. Post-query layer may map `category_id` to category name via join.

## 10. Template Payload (Logical JSON Shape)
```json
{
  "filters": {
    "date_range": {"start": "2025-01-01", "end": "2025-02-01"},
    "transaction_type": "expense|income|all",
    "categories": ["<category_id>", "..."] ,
    "counterparty": "<substring>"
  },
  "grouping": ["category_id", "month"],
  "aggregation": {"field": "amount_out", "func": "sum"},
  "view_mode": "table|chart",
  "template_schema_version": 1
}
```

## 11. JSON Schemas (To Be Produced in Tasks 5–7)
Paths (planned):
- `contracts/transaction.schema.json`
- `contracts/log-event.schema.json`
- `contracts/report-request.schema.json`

Transaction schema will mirror table fields excluding internal fields: may omit `mapping_version`, `logic_version` if considered implementation metadata in external outputs (TBD—tests will specify expected exposure). For determinism testing, internal test fixture will include them.

## 12. Open Future Extensions (Non-Blocking)
| Extension | Approach | Impact |
|-----------|---------|--------|
| anomalies_log table | Store soft anomalies with foreign key to transaction hash | Improves auditability |
| enrichment stage | Add `enrichment_version`, derived merchant category codes | Expand normalization_hash inputs (major bump) |
| multi-tag categories | Add join table `transaction_tags` | Changes reporting grouping logic |

## 13. Rejection Log (Why Not ORM?)
Explicit SQL chosen over full ORM (e.g., SQLAlchemy) to reduce abstraction overhead and maintain deterministic control over schema & migrations (Constitution: Simplicity & Determinism). Could revisit if complexity in query builder escalates.

## 14. Determinism Verification Hooks
1. After normalization: recompute hash; assert equality (self-check safeguard).
2. On duplicate insert attempt (same `normalization_hash`): log and skip; do not update existing row.
3. End-to-end test will snapshot sorted list of `(normalization_hash, amount_in, amount_out)` across two runs.

---
End of data model.
