# 📂 Shared — Master Reference Files

This folder contains the **core master files** used across all pipeline modules.

> Every module reads from this folder. These files must always be present before running the pipeline.

---

## Files

### `IKP_PQAH.xlsx` — Master Employee List
- **Role:** Primary dataset and join key source for all modules
- **Key column:** `Personnel No.` (unique per employee)
- **Used by:** All 6 modules + Assembler
- **Contains:** Name, position, org unit, company code, job, gender, birth date, nationality, religion, marital status, etc.

### `IKP_Headings.xlsx` — Report Template
- **Role:** Defines the exact 45-column layout of the final output report
- **Used by:** Assembler only
- **How it works:** Row 1 contains the target column names. The Assembler maps all enriched data to this exact column order.
- **⚠️ Do not add or remove columns** — any change to this file changes the final report structure.

### `IKP_Direct_Spv.xlsx` — Direct Supervisor Lookup
- **Role:** Maps each employee's Personnel No. to their direct supervisor's NIK and name
- **Output columns:** `Superior NIK`, `Superior Name`
- **Used by:** Assembler (columns 35–36)

### `IKP_PA0105.xlsx` — Email Addresses
- **Role:** Maps Personnel No. to corporate email address
- **Output column:** `Email`
- **Used by:** Assembler (column 41)

### `IKP_Job_Layer.xlsx` — Job Layer Classification
- **Role:** Maps job codes to organizational layer levels
- **Output column:** `Layer`
- **Used by:** Assembler (column 34)

---

## Notes for HR

- These files are exported from SAP or maintained as master data by the HR team.
- **Monthly files** (`IKP_PQAH.xlsx`, `IKP_PA0105.xlsx`) should be refreshed every month with a fresh SAP export.
- **Static master files** (`IKP_Headings.xlsx`, `IKP_Job_Layer.xlsx`, `IKP_Direct_Spv.xlsx`) only need to be updated when the underlying business data changes.
