# 📂 Join Date & Year of Service

**Module 5** — Extracts each employee's join date from SAP PA0041 and calculates their total years of service.

---

## Files

### `IKP_PA0041.xlsx` — Date Records (SAP PA0041)
- **Export source:** SAP Infotype PA0041
- **Key column:** `Personnel number`
- **Filter:** Only records where `Date type` = `"01"` (Join Date) are used
- An employee may have multiple PA0041 rows for different date types; only `01` is selected.

---

## Output

`output/intermediate/PQAH_Enriched_JoinDate_YoS.xlsx`

Added/computed columns:
- **`Join Date`** — The employee's official start date (Date Type 01)
- **`Year of Service`** — Calculated as `(today - Join Date).years` using full-year rounding

---

## Notes

- If an employee has no Date Type `01` record, the Join Date will be blank.
- Years of Service is recalculated fresh on every pipeline run (always reflects today's date).
