# 📂 Contract Type & Contract End Data

**Module 1** — Enriches each employee's contract record with a human-readable contract type description.

---

## Files

### `IKP_PA0016.xlsx` — Contract Records (SAP PA0016)
- **Export source:** SAP Infotype PA0016
- **Key column:** `Personnel number`
- **Join key:** `Contract Type` (values: `"1"`, `"2"` — bare integer, zero-padded to `"01"`, `"02"` before lookup)
- **Used for:** Contract Type code, Valid Until date (→ Contract End Date)

### `Contract Type_IKP_IT0016.xlsx` — Contract Type Master Lookup
- **Role:** Maps 2-digit contract type codes to their descriptions
- **Key column:** `Contract Type` (format: `"01"`, `"02"`, ..., `"98"`)
- **Value column:** `Contract Type Text`
- **Example mapping:**

| Contract Type | Contract Type Text |
|---------------|--------------------|
| 01 | unlimited |
| 02 | Limited contract |
| 11 | Probation |
| 18 | Contract I |
| 19 | Contract II |

---

## Output

`output/intermediate/IKP_PA0016_With_ContractType_Description.xlsx`

Added columns:
- **`Contract Type Description`** — The text name of the contract type
- **`Contract End Date`** — Sourced from the `Valid Until` column in PA0016

---

## Logic Notes

- `Contract Type` in PA0016 stores values without zero-padding (e.g., `"2"`).
  The pipeline applies `zfill(2)` before joining to match the lookup format (`"02"`).
- One row per employee is expected in the output (matching PA0016 input).
