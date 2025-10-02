# Quickstart – Feature 001 (Extracta Core Pipeline)

Date: 2025-10-02  
Related Spec: `specs/extracta-core/spec.md`  
Research Hash: `2e9df42f6c805af31e0497de912e5c277ab43aa73a9e1bac085517d660d7b6b8`

## 1. Prerequisites
| Component | Requirement | Notes |
|-----------|------------|-------|
| Python | 3.11 (assumed) | Confirm with `python --version` |
| Tesseract OCR | Installed & in PATH | Windows: choco install tesseract; mac: brew install tesseract |
| Virtual Env | Recommended | Isolate deps |
| SQLite | Built-in | No action needed |

## 2. Install Dependencies
Current `requirements.txt` is minimal (only `streamlit`). Additional packages to be appended during implementation per plan: `pdfplumber`, `pytesseract`, `Pillow`, `pyyaml` (and possibly `pandas`, `ruff`, `pytest`).

Example (after dependencies added):
```bash
pip install -r requirements.txt
```

## 3. Directory Layout (After Implementation)
```
src/
  ingestion/
  extraction/
  normalization/
  persistence/
  categorization/
  reporting/
  ui/
  logging/
  common/
config/
  mappings.yml
data/
logs/
```

## 4. First Run (End-to-End)
1. Place one sample statement PDF in a temporary folder (`samples/statement1.pdf`).
2. (Optional) Add an image file (`samples/receipt1.jpg`).
3. Launch the UI (after `app.py` exists):
   ```bash
   streamlit run src/ui/app.py
   ```
4. Upload the files via the Upload section.
5. Wait for extraction & normalization summary (record counts) to display.
6. Navigate to Transactions tab → assign a category (create new category if needed).
7. Navigate to Reports tab → set filters (e.g., date range), group by `category` & `month`, aggregate `amount_out` with `sum`.
8. Toggle between Table and Chart view.
9. Save as a template (name: `Monthly Expenses`).
10. Switch filters randomly, then load the template and confirm identical results reappear.

## 5. Determinism Verification
1. Re-run the app and re-upload the exact same files.
2. Open logs (`logs/pipeline.log`), verify same `normalization_hash` values for all rows (no duplicates inserted; duplicates should be logged as skipped).
3. (Future script) Run deterministic check:
   ```bash
   python scripts/check_determinism.py --file samples/statement1.pdf
   ```

## 6. Normalization Mapping Configuration
Example `config/mappings.yml` skeleton (to be filled):
```yaml
version: v1
synonyms:
  amount_out: ["debit", "money out", "withdrawal"]
  amount_in: ["credit", "money in", "deposit"]
file_overrides: []
rules:
  # precedence: explicit file_overrides > rules > synonyms
```

## 7. Category Workflow
1. Initially transactions have `category_id = NULL`.
2. User selects rows & assigns or creates a category.
3. FK update does NOT change `normalization_hash`.
4. Reports can group by category; internal join resolves name.

## 8. Logging Format
Each pipeline stage emits JSON lines with: `ts, stage, duration_ms, in_count, out_count, error_count, source_file, normalization_hash? (when per-row), status`.

Example (normalization stage aggregate entry):
```json
{
  "ts":"2025-10-02T12:34:56Z",
  "stage":"normalization",
  "source_file":"statement1.pdf",
  "in_count":250,
  "out_count":250,
  "error_count":0,
  "duration_ms":812,
  "status":"success"
}
```

## 9. Environment Overrides
| Variable | Purpose | Default |
|----------|---------|---------|
| EXTRACTA_DB_PATH | SQLite DB path | `data/extracta.db` |
| EXTRACTA_LOG_PATH | Log file path | `logs/pipeline.log` |

## 10. Troubleshooting
| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| OCR returns blank | Tesseract not installed or path missing | Install & ensure in PATH |
| Duplicate rows skipped | Same file re-uploaded | Expected; view log entries |
| Report empty | Filters exclude all | Reset filters or date range |
| Template load mismatch | Underlying schema changed | Increment template schema version & migrate |

## 11. Next Steps After MVP
1. Add anomaly log table for soft validation issues.
2. Introduce enrichment step (merchant heuristics).
3. Optional CLI for batch ingestion without UI.

---
End of quickstart.
