# 📂 Education, Institute, Branch of Study

**Module 2** — Identifies each employee's highest non-training educational qualification and enriches it with branch of study text.

---

## Files

### `IKP_IT0022.xlsx` — Education Records (SAP IT0022)
- **Export source:** SAP Infotype IT0022
- **Key column:** `Personnel number`
- **Join key:** `Educational est.` (e.g., `"2"`, `"7"`) — zero-padded to `"02"`, `"07"` before lookup
- **Other used columns:** `Branch of Study 1`, `Department`, `Final Grade`, `Institute/location`
- An employee may have **multiple rows** (one per education record). The module keeps only the **highest** qualification.

### `Order_IKP_IT0022.xlsx` — Education Ranking Table
- **Role:** Maps education codes to a sortable order rank and a display text
- **Key column:** `Key` (format: `"01"` to `"20"`)
- **Value columns:** `Order` (numeric rank), `Text` (e.g., `"University/S1"`)
- **Training exclusion:** `Key = "10"` (Training) and `Order = 11` are **excluded** from highest education selection

| Key | Order | Text |
|-----|-------|------|
| 01 | 1 | Elementary School |
| 02 | 2 | Junior High School |
| 03 | 3 | Senior High School |
| 07 | 8 | University/S1 |
| 08 | 9 | University/S2 |
| 09 | 10 | University/S3 |
| **10** | **11** | **Training** ← excluded |

### `IKP_Branch of Study.xlsx` — Branch of Study Lookup
- **Role:** Maps 5-digit branch codes to their display text
- **Key column:** `Branch of Study` (format: `"00040"`, `"00097"` — 5-digit zero-padded)
- **Value column:** `Branch of Study Text`
- `Branch of Study 1` from IT0022 is zero-padded to 5 digits (`"97"` → `"00097"`) before lookup

---

## Output

`output/intermediate/IKP_IT0022_HighestOrder_IgnoreTraining_WithBranchText.xlsx`

Added/computed columns:
- **`Key`** — Zero-padded education code (`"07"`)
- **`Order`** — Numeric rank used for sorting
- **`Text`** — Education level name (e.g., `"University/S1"`)
- **`BranchCodeNorm`** — 5-digit normalized branch code
- **`Branch of Study Text`** — Branch of study description

---

## Logic Summary

1. Normalize `Educational est.` → `zfill(2)` → join to Order table on `Key`
2. Exclude training records (`Key = "10"` or `Order = 11`)
3. Per employee: sort by `Order` descending, keep row with **highest** Order value
4. Normalize `Branch of Study 1` → `zfill(5)` → lookup `Branch of Study Text`
