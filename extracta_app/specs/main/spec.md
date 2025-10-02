# Main Specification Wrapper

This file serves as the canonical spec reference for the /plan command. The detailed feature specification for the initial core pipeline lives at:

`../extracta-core/spec.md`

For planning purposes, the scope is the "Extracta Core Pipeline" (Feature ID: 001-extracta-core) encompassing:
1. File upload (pdf/png/jpg) via Streamlit
2. Extraction (text/table + OCR)
3. Validation & normalization into the Canonical Transaction Model
4. Persistence to SQLite
5. Categorization UI
6. Reporting constructor (filters, grouping, aggregation, table/chart)
7. Report templates (save/load)

All functional and non-functional requirements, open questions (Q1–Q10), acceptance criteria, risks, and model definitions are defined in the core spec. Any amendments should be reflected in BOTH this wrapper (summary only) and the core spec.

---
Summary Hash Anchor (for determinism tracking):

`2e9df42f6c805af31e0497de912e5c277ab43aa73a9e1bac085517d660d7b6b8` (Summary hash of resolved decisions JSON.)

---
End of wrapper.
