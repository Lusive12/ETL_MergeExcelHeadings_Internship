# 📂 Entity, Division, Area, Function

**Module 3** — Maps each employee to their organizational Entity, Division, Area, and Function using SAP master data.

---

## Files

### `ZHR_MAP_ENTITY.xlsx` — Entity / Area / Function Mapping
- **Role:** Maps organizational codes to Entity, Area, and Function labels
- **Used by:** Assembler (columns 1, 3, 4)

### `ZHR_MASTER_DIVISION.xlsx` — Division Master Lookup
- **Role:** Maps division codes to their full Division name
- **Used by:** Assembler (column 2)

---

## Output

`output/intermediate/IKP_PQAH_With_Entity_DivisionDesc_Area_Function.xlsx`

Added columns:
- **`Entity`** — Company entity classification
- **`Division`** — Organizational division
- **`Area`** — Geographic or business area
- **`Function`** — Functional grouping (e.g., Finance, Operations)
