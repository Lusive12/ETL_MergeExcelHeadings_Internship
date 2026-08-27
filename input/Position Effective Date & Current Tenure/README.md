# 📂 Position Effective Date & Current Tenure

**Module 6** — Determines when each employee entered their current position and calculates how long they have held it.

---

## Files

### `IKP_HRP1001.xlsx` — Position History (SAP HRP1001)
- **Export source:** SAP HRP1001 (Organization & Staffing)
- **Key column:** Composite key = `Object ID` (position) + personnel identifier
- **Used columns:** `ID of` (Object ID), `Start Date` (when the person was placed in this position)
- The record with the employee's **current position** is matched via Object ID lookup against `IKP_PQAH.xlsx`.

---

## Output

`output/intermediate/PQAH_Enriched_PositionTenure.xlsx`

Added/computed columns:
- **`Position Effective Date`** — The date the employee started in their current position
- **`Current Tenure`** — Calculated as `(today - Position Effective Date).years`

---

## Notes

- The join is performed on `Object ID` from HRP1001 matching the `Position` column in PQAH.
- If no matching HRP1001 record is found, Position Effective Date will be blank.
- Current Tenure is recalculated fresh on every pipeline run.
