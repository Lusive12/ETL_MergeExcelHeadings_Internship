# 📂 General Cost Center & Cost Center Text

**Module 4** — Enriches each employee's IT0027 cost center assignment with the cost center description text.

---

## Files

### `IKP_IT0027.xlsx` — Cost Center Assignments (SAP IT0027)
- **Export source:** SAP Infotype IT0027
- **Key column:** `Personnel number`
- **Contains:** Multiple cost center columns per record (salary + general expense split)
- An employee may have multiple IT0027 records; the module picks the **most valid** one based on date ranges.

### `IKP_CSKT.xlsx` — Cost Center Master Lookup
- **Role:** Maps cost center codes to their descriptions
- **Key column:** `Cost Center` (or equivalent)
- **Value column:** Cost Center description text
- **Selection rule:** For employees with multiple date-range records, the entry with the **maximum Valid To date** is selected.

---

## Output

`output/intermediate/IT0027_Enriched_CostCenterDesc.xlsx`

Added columns:
- **`Salary Cost Center (S4)`** — Salary cost center code
- **`Salary Cost Center Desc (S4)`** — Salary cost center description
- **`General Expense Cost Center`** — General expense cost center code
- **`General Expense Cost Center Desc`** — General expense cost center description
