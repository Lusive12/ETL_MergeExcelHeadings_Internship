# 📊 Monthly HR Report Automation Suite

> **Automated ETL pipeline** that transforms raw SAP exports into a unified, structured HR Topic Report — in seconds, not hours.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas)](https://pandas.pydata.org)
[![License: Internal](https://img.shields.io/badge/License-Internal%20Use-lightgrey)]()

---

## 🚀 Quick Start (HR Users)

> No coding experience required. Just follow these 3 steps.

**Step 1 — Place your SAP export files** into the correct subfolders inside `input/`
_(See the [Input Folder Guide](#-input-folder-architecture) below)_

**Step 2 — Double-click `RUN_ME.bat`**
The pipeline runs automatically in the background.

**Step 3 — Collect your report** from the `output/` folder
Look for `FINAL_HR_Topic_Report_YYYYMMDD.xlsx`

---

## 📁 Project Structure

```
Monthly HR Report Automation/
│
├── 📂 input/                          ← Place all SAP export files here
│   ├── Shared/                        ← Master files used across all modules
│   ├── Contract Type & Contract End Data/
│   ├── Education, Institute, Branch of Study/
│   ├── Entity, Division, Area, Function/
│   ├── General Cost Center & Cost Center Text/
│   ├── Join Date & Year of Service/
│   └── Position Effective Date & Current Tenure/
│
├── 📂 output/                         ← All outputs land here
│   ├── FINAL_HR_Topic_Report_YYYYMMDD.xlsx   ← ✅ Your final report
│   ├── 00_processing_summary.xlsx            ← Audit summary
│   └── intermediate/                         ← Per-module enriched outputs
│
├── 📂 src/                            ← Pipeline source code (Python)
│   ├── assembler.py                   ← Final report builder (45-column merge)
│   ├── common.py                      ← Shared utilities & column helpers
│   ├── contract_type.py               ← Module 1: Contract Type & End Date
│   ├── education.py                   ← Module 2: Education, Institute, Branch
│   ├── entity_division.py             ← Module 3: Entity, Division, Area, Function
│   ├── cost_center.py                 ← Module 4: General Cost Center
│   ├── join_date.py                   ← Module 5: Join Date & Years of Service
│   ├── position_tenure.py             ← Module 6: Position Effective Date & Tenure
│   ├── validator.py                   ← Row-count & column guards
│   ├── excel_export.py                ← Safe Excel writer (detects open files)
│   ├── logger.py                      ← Timestamped logging
│   └── summary.py                     ← Audit summary writer
│
├── 📂 config/
│   └── settings.json                  ← Toggle modules on/off
│
├── 📂 logs/                           ← One log file per run (timestamped)
├── run.py                             ← Main pipeline entry point
├── RUN_ME.bat                         ← One-click launcher for HR users
└── requirements.txt                   ← Python dependencies
```

---

## 📥 Input Folder Architecture

Each subfolder maps to one pipeline module. Place the **exact files** listed below in each folder.

> ⚠️ **Do not rename the files.** The pipeline locates files by their exact names (case-insensitive).

```
input/
│
├── Shared/                             ← Used by ALL modules
│   ├── IKP_PQAH.xlsx                  ← Master employee list (primary key: Personnel No.)
│   ├── IKP_Headings.xlsx              ← Final report template (defines 45-column layout)
│   ├── IKP_Direct_Spv.xlsx            ← Direct supervisor lookup (Superior NIK & Name)
│   ├── IKP_PA0105.xlsx                ← Employee email addresses
│   └── IKP_Job_Layer.xlsx             ← Job layer classification
│
├── Contract Type & Contract End Data/
│   ├── IKP_PA0016.xlsx                ← SAP PA0016 contract records
│   └── Contract Type_IKP_IT0016.xlsx  ← Contract type code → description lookup
│
├── Education, Institute, Branch of Study/
│   ├── IKP_IT0022.xlsx                ← SAP IT0022 education records
│   ├── Order_IKP_IT0022.xlsx          ← Education ranking (Key → Order → Text)
│   └── IKP_Branch of Study.xlsx       ← Branch of study code → text lookup
│
├── Entity, Division, Area, Function/
│   ├── ZHR_MAP_ENTITY.xlsx            ← Entity / Area / Function mapping
│   └── ZHR_MASTER_DIVISION.xlsx       ← Division master lookup
│
├── General Cost Center & Cost Center Text/
│   ├── IKP_IT0027.xlsx                ← SAP IT0027 cost center assignment records
│   └── IKP_CSKT.xlsx                  ← Cost center code → description lookup
│
├── Join Date & Year of Service/
│   └── IKP_PA0041.xlsx                ← SAP PA0041 date records (filtered: Date Type = 01)
│
└── Position Effective Date & Current Tenure/
    └── IKP_HRP1001.xlsx               ← SAP HRP1001 position history (Object ID & Start Date)
```

---

## 📤 Output Files

| File | Location | Description |
|------|----------|-------------|
| `FINAL_HR_Topic_Report_YYYYMMDD.xlsx` | `output/` | **Main deliverable.** 45-column report matching the `IKP_Headings.xlsx` template. One row per employee. |
| `00_processing_summary.xlsx` | `output/` | Audit table: module status, row counts, matched/unmatched per module. |
| `IKP_PA0016_With_ContractType_Description.xlsx` | `output/intermediate/` | PA0016 enriched with Contract Type Description. |
| `IKP_IT0022_HighestOrder_IgnoreTraining_WithBranchText.xlsx` | `output/intermediate/` | Highest non-training education per employee + Branch of Study Text. |
| `IKP_PQAH_With_Entity_DivisionDesc_Area_Function.xlsx` | `output/intermediate/` | PQAH enriched with Entity, Division, Area, and Function. |
| `IT0027_Enriched_CostCenterDesc.xlsx` | `output/intermediate/` | IT0027 enriched with cost center descriptions. |
| `PQAH_Enriched_JoinDate_YoS.xlsx` | `output/intermediate/` | PQAH with Join Date and Years of Service. |
| `PQAH_Enriched_PositionTenure.xlsx` | `output/intermediate/` | PQAH with Position Effective Date and Current Tenure. |
| `logs/YYYYMMDD_HHMMSS.log` | `logs/` | Full timestamped execution log for every run. |

---

## ⚙️ Pipeline Architecture

The pipeline runs **6 independent enrichment modules** in sequence, then a final **Assembler** step that merges all results into the 45-column Topic Report.

```
                    ┌──────────────────────┐
                    │  run.py  (Orchestrator)│
                    └──────────┬───────────┘
                               │
            ┌──────────────────▼──────────────────┐
            │          IKP_PQAH.xlsx               │
            │     (Master employee dataset)         │
            └──────────────────┬──────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                     ▼
   [Module 1]            [Module 2]            [Module 3]
 Contract Type          Education             Entity/Division
 PA0016 + IT0016        IT0022 + Order        ZHR_MAP_ENTITY
 lookup → Desc          + Branch lookup       + MASTER_DIVISION

          ▼                    ▼                     ▼
   [Module 4]            [Module 5]            [Module 6]
  Cost Center            Join Date            Pos. Tenure
  IT0027 + CSKT          PA0041               HRP1001
  lookup → Desc          Date Type 01         Object ID match

          └────────────────────┬────────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │   ASSEMBLER           │
                    │ Merges all 6 outputs  │
                    │ Maps → 45 columns     │
                    │ FINAL_HR_Topic_Report │
                    └──────────────────────┘
```

---

## 🔧 Module Toggle (`config/settings.json`)

Selectively enable or disable individual modules without changing any code:

```json
{
    "run_modules": {
        "contract_type":   true,
        "education":       true,
        "entity_division": true,
        "cost_center":     true,
        "join_date":       true,
        "position_tenure": true,
        "assembler":       true
    }
}
```

> 💡 Set any module to `false` to skip it — useful when a specific input file is not yet ready or when debugging a single module.

---

## 🛠️ Developer Setup

```bash
# 1. Clone the repository
git clone https://github.com/Lusive12/ETL_MergeExcelHeadings_Internship.git
cd ETL_MergeExcelHeadings_Internship

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the pipeline
python run.py
```

---

## 🔑 Key Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Zero aliases** | Column lookups use exact case-insensitive matching via `find_column_ci()`. `"Personnel No."` and `"Personnel Number"` are always treated as **distinct** columns |
| **Key normalization** | Numeric codes are zero-padded before joining: `"2"` → `"02"` (2-digit), `"40"` → `"00040"` (5-digit) to prevent silent lookup mismatches |
| **Row preservation** | Every module validates output row count == input row count — no accidental drops allowed |
| **File lock protection** | `excel_export.py` detects open Excel files and raises a descriptive error instead of corrupting data |
| **Modular & toggleable** | Each domain is a fully isolated module; `config/settings.json` controls which modules run |
| **Audit trail** | Every run produces a timestamped log and a processing summary Excel file |

---

## 📊 Output Column Reference (All 45 Columns)

| # | Column | Primary Source |
|---|--------|----------------|
| 1 | Entity | `ZHR_MAP_ENTITY.xlsx` |
| 2 | Division | `ZHR_MASTER_DIVISION.xlsx` |
| 3 | Area | `ZHR_MAP_ENTITY.xlsx` |
| 4 | Function | `ZHR_MAP_ENTITY.xlsx` |
| 5 | Personnel No. | `IKP_PQAH.xlsx` |
| 6 | Personnel Number | `IKP_PQAH.xlsx` |
| 7 | Lvl | `IKP_PQAH.xlsx` |
| 8 | CoCd | `IKP_PQAH.xlsx` |
| 9 | Company Name | `IKP_PQAH.xlsx` |
| 10 | ESgrp | `IKP_PQAH.xlsx` |
| 11 | Name of EE Subgroup | `IKP_PQAH.xlsx` |
| 12 | PArea | `IKP_PQAH.xlsx` |
| 13 | Personnel Area Text | `IKP_PQAH.xlsx` |
| 14 | Subarea | `IKP_PQAH.xlsx` |
| 15 | P. SubArea Text | `IKP_PQAH.xlsx` |
| 16 | Position | `IKP_PQAH.xlsx` |
| 17 | Position Name | `IKP_PQAH.xlsx` |
| 18 | Org. Unit | `IKP_PQAH.xlsx` |
| 19 | Name of Organizational Unit | `IKP_PQAH.xlsx` |
| 20 | Join Date | `IKP_PA0041.xlsx` (Date Type 01) |
| 21 | Year of Service | Calculated from Join Date → today |
| 22 | Job | `IKP_PQAH.xlsx` |
| 23 | Job Title | `IKP_PQAH.xlsx` |
| 24 | Gender | `IKP_PQAH.xlsx` |
| 25 | Birth Date | `IKP_PQAH.xlsx` |
| 26 | Age | Calculated from Birth Date → today |
| 27 | Nationality | `IKP_PQAH.xlsx` |
| 28 | Birthplace | `IKP_PQAH.xlsx` |
| 29 | Education | `IKP_IT0022.xlsx` + `Order_IKP_IT0022.xlsx` (highest non-training qualification) |
| 30 | Institute | `IKP_IT0022.xlsx` (Institute/location column) |
| 31 | Branch Study | `IKP_IT0022.xlsx` + `IKP_Branch of Study.xlsx` (code lookup) |
| 32 | Religion | `IKP_PQAH.xlsx` |
| 33 | Marital Status | `IKP_PQAH.xlsx` |
| 34 | Layer | `IKP_Job_Layer.xlsx` |
| 35 | Superior NIK | `IKP_Direct_Spv.xlsx` |
| 36 | Superior Name | `IKP_Direct_Spv.xlsx` |
| 37 | Salary Cost Center (S4) | `IKP_IT0027.xlsx` |
| 38 | Salary Cost Center Desc (S4) | `IKP_CSKT.xlsx` |
| 39 | General Expense Cost Center | `IKP_IT0027.xlsx` |
| 40 | General Expense Cost Center Desc | `IKP_CSKT.xlsx` |
| 41 | Email | `IKP_PA0105.xlsx` |
| 42 | Contract Type | `IKP_PA0016.xlsx` + `Contract Type_IKP_IT0016.xlsx` |
| 43 | Contract End Date | `IKP_PA0016.xlsx` (Valid Until) |
| 44 | Position Effective Date | `IKP_HRP1001.xlsx` |
| 45 | Current Tenure | Calculated from Position Effective Date → today |

---

## 🔭 Future Development Suggestions

### 📌 For HR / Business Users
- **📅 Scheduled automation** — Run automatically every 1st of the month via Windows Task Scheduler so reports are always ready without manual steps.
- **📧 Email delivery** — Auto-send the final report to a distribution list immediately after the pipeline completes.
- **📋 Validation dashboard** — A simple web or Excel dashboard showing matched/unmatched statistics per month, flagging anomalies (e.g., employees with no education record or contract type).
- **🌐 Multi-language support** — Add Indonesian-language column headers and error messages.

### 💻 For Developers
- **🐍 CLI flags** — Add `argparse` so specific modules can be toggled from the command line: `python run.py --only education cost_center`.
- **🧪 Unit tests** — Add a `pytest` test suite for each module using small fixture Excel files to catch regressions automatically on every commit.
- **🗄️ Database support** — Replace Excel inputs with direct SAP HANA / PostgreSQL queries via `pyodbc` to eliminate the manual export step entirely.
- **📦 Docker containerization** — Package the pipeline into a Docker image so it runs identically on any machine without environment setup.
- **📈 Incremental processing** — Detect changed rows and only process deltas each month (critical as headcount grows beyond thousands of employees).
- **🔗 REST API** — Expose the pipeline as a FastAPI endpoint so other systems (HRIS, BI tools) can trigger it programmatically via HTTP.
- **📊 Power BI / Tableau connector** — Output directly to a live database table instead of Excel, enabling real-time HR dashboards without manual refresh.
- **🔔 Slack / Teams notification** — Post a run summary card to a team channel automatically when the pipeline completes or fails.
- **🔐 Column schema versioning** — Lock the 45-column schema in a JSON schema file so accidental heading changes in `IKP_Headings.xlsx` are detected and flagged before the run starts.

---

## 📋 Requirements

```
pandas>=2.0
openpyxl>=3.1
```

Install with:
```bash
pip install -r requirements.txt
```

---

## 👥 Contributors

| Role | Contributor |
|------|-------------|
| ETL Pipeline — Topic Report | [@Lusive12](https://github.com/Lusive12) |
| Monthly Data Module | [@andromedaar](https://github.com/andromedaar) |

---

*Monthly HR Report Automation Suite — built for speed, accuracy, and zero manual copy-paste.*
