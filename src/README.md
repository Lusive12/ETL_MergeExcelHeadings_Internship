# 🐍 src/ — Pipeline Source Modules

This folder contains all Python source modules for the HR Report Automation pipeline.

---

## Module Overview

| File | Role | Key Logic |
|------|------|-----------|
| `run.py` _(root)_ | **Orchestrator** | Loads settings, runs each module in order, writes summary |
| `assembler.py` | **Final assembler** | Merges all 6 intermediate outputs → 45-column Topic Report |
| `common.py` | **Shared utilities** | `find_column_ci()`, `normalize_id()`, `load_excel()` |
| `contract_type.py` | Module 1 | PA0016 + contract type lookup; `zfill(2)` key normalization |
| `education.py` | Module 2 | IT0022 highest non-training education + Branch of Study lookup |
| `entity_division.py` | Module 3 | ZHR_MAP_ENTITY + ZHR_MASTER_DIVISION lookup |
| `cost_center.py` | Module 4 | IT0027 + CSKT cost center description lookup |
| `join_date.py` | Module 5 | PA0041 Date Type 01 → Join Date + Years of Service |
| `position_tenure.py` | Module 6 | HRP1001 Object ID + Start Date → Position Tenure |
| `validator.py` | Guard layer | `validate_file_exists()`, `validate_columns()`, `validate_row_count()` |
| `excel_export.py` | Safe writer | Detects open Excel files; raises clear error instead of corrupting |
| `logger.py` | Logging setup | Writes timestamped logs to `logs/YYYYMMDD_HHMMSS.log` |
| `summary.py` | Audit writer | Produces `00_processing_summary.xlsx` after each run |

---

## Shared Utilities (`common.py`)

### `find_column_ci(df, name) → str | None`
Searches a DataFrame for a column matching `name` using **exact case-insensitive, whitespace-trimmed** matching.
Returns the actual column name as it appears in the DataFrame, or `None` if not found.

> ⚠️ No aliasing — `"Personnel No."` and `"Personnel Number"` are **never** treated as the same column.

### `get_required_column_ci(df, name) → str`
Same as `find_column_ci`, but **raises a `KeyError`** if the column is not found.
Use this when the column is mandatory for the module to function.

### `normalize_id(series) → pd.Series`
Strips whitespace, removes trailing `.0` (from Excel float parsing), and returns a clean string Series.
Does **not** apply zero-padding — callers must apply `.str.zfill(n)` explicitly when needed.

### `load_excel(path) → pd.DataFrame`
Reads an Excel file with all columns as `dtype=str` (prevents auto-conversion of numeric codes to floats).

---

## Key Normalization Pattern

A common issue across SAP exports is that numeric codes appear without zero-padding:
- `"2"` in PA0016 must match `"02"` in the lookup
- `"40"` in IT0022 must match `"00040"` in Branch of Study

**Pattern used throughout the codebase:**
```python
series.apply(lambda x: x.zfill(2) if x.isdigit() else x)  # 2-digit codes
series.apply(lambda x: x.zfill(5) if x.isdigit() else x)  # 5-digit codes
```

---

## Adding a New Module

1. Create `src/your_module.py` with a `run(logger) -> dict` function
2. Return a result dict with keys: `Module`, `Input Rows`, `Output Rows`, `Matched`, `Unmatched`, `Status`, `Output File`
3. Add `"your_module": true` to `config/settings.json`
4. Import and call it in `run.py` following the existing pattern
5. Add the merge logic to `assembler.py` if its columns appear in the final report
