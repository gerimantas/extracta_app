# Data Model: Advanced Document and Entity Management

## 1. Overview
This document specifies the relational schema additions and changes required to support document management, classification, and counterparties.

## 2. Existing Core Tables (Context)
- `transactions` (append-only normalized rows)
- `categories` (category definitions)

## 3. New / Extended Tables
### 3.1 documents
Tracks uploaded file metadata distinct from transaction rows (enables deletion + status management).

Column | Type | Constraints | Notes
-------|------|-------------|------
id | INTEGER | PRIMARY KEY AUTOINCREMENT | Surrogate key
filename | TEXT | NOT NULL | Original filename; not guaranteed unique
file_hash | TEXT | NOT NULL | SHA256 of file bytes; uniqueness candidate
upload_date | TIMESTAMP | NOT NULL | Ingestion timestamp (UTC)
status | TEXT | NOT NULL | Enum: Uploaded, Processing, Success, Error
document_type | TEXT | NOT NULL | Enum (Bank Statement, Accounting Ledger, Purchase Receipt, Other)
created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation

Indexes:
- UNIQUE(file_hash)
- INDEX on (upload_date)
- (Optional future) INDEX(filename)

### 3.2 counterparties
Canonical counterparty names.

Column | Type | Constraints | Notes
-------|------|-------------|------
id | INTEGER | PRIMARY KEY AUTOINCREMENT | Surrogate key
name | TEXT | NOT NULL | Original display (Title Case)
name_normalized | TEXT | NOT NULL | Lowercase normalized; UNIQUE
created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time

Indexes:
- UNIQUE(name_normalized)

### 3.3 transactions (Alter)
Add column:

Column | Type | Constraints | Notes
-------|------|-------------|------
counterparty_id | INTEGER | NULLABLE initially, then filled | FK → counterparties.id (ON DELETE SET NULL not needed if we never delete; we keep rows)

NOTE: We do not remove existing free-text `description`; counterparty extraction uses it as input.

Foreign Key Behavior:
- We do NOT cascade delete counterparties when no transactions reference them.
- If a counterparty is deleted due to merge logic (loser rows), transactions will have been reassigned first.

## 4. Relationships
- `documents` (1) → `transactions` (N) via matching `file_hash` OR (optional future) store `document_id` in `transactions` for direct FK.
- `counterparties` (1) → `transactions` (N) via `counterparty_id`.

## 5. Deletion Semantics
- Document deletion: remove all `transactions` with that document reference, then remove `documents` row. Counterparties untouched.
- Counterparty merge: update transactions to winning id, delete losing rows.

## 6. Migration Steps (Forward Only)
1. Create `documents` (if absent).
2. Backfill from distinct transaction `source_file` & file hash (if those fields are available) setting status=Success, document_type=Other (fallback).
3. Create `counterparties`.
4. Add `counterparty_id` column to `transactions` (nullable).
5. Create indices and unique constraints.
6. Update schema_version table.

## 7. Determinism Notes
- None of the new columns are included in normalization hash computation.
- Counterparty assignment logic deterministic and repeatable.

## 8. Future Extensions
- Add `document_id` FK column to `transactions` for explicit relational binding (avoid relying on filename/hash join).
- Add audit tables: `document_deletions`, `counterparty_merges`.
- Add `last_used_at` to `counterparties` for cleanup heuristics.

End of data model.
