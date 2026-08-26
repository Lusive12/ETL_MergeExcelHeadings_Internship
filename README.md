# HR Data Automation Suite — Full Topic Report

Monthly HR data ETL pipeline that ingests raw SAP exports, performs multi-level validations, enriches 6 core domains, and outputs a unified Topic Report mapped against `IKP_Headings.xlsx`.

---

## 🚀 How to Run

1. Place your SAP export files in the designated folders inside `input/`.
2. Double-click **`RUN_ME.bat`** (or run `python run.py` via virtual environment).
3. Collect your deliverables from the `output/` folder.

---

## 📁 Input Folder Architecture

```
input/
├── Shared/
│   ├── IKP_PQAH.xlsx           <- Master employee file (base dataset, primary key: Personnel No.)
│   ├── IKP_Headings.xlsx       <- Final report column layout template (45 columns)
│   ├── IKP_Direct_Spv.xlsx     <- Direct supervisor lookup (Superior NIK & Name)
│   ├── IKP_PA0105.xlsx         <- Email source
│   └── IKP_Job_Layer.xlsx      <- Job Layer lookup
│
├── Contract Type & Contract End Data/
│   ├── IKP_PA0016.xlsx         <- Contract records
│   └── IKP_Contract Type.xlsx  <- Contract type master lookup
│
├── Education, Institute, Branch of Study/
│   ├── IKP_IT0022.xlsx         <- Education records
│   ├── Order_IKP_IT0022.xlsx   <- Education ranking hierarchy (excluding training)
│   └── IKP_Branch of Study.xlsx<- Branch of study description master
│
├── Entity, Division, Area, Function/
│   ├── ZHR_MAP_ENTITY.xlsx     <- Entity / Area / Function mapping
│   └── ZHR_MASTER_DIVISION.xlsx<- Division master lookup
│
├── General Cost Center & Cost Center Text/
│   ├── IKP_IT0027.xlsx         <- Cost Center assignments
│   └── IKP_CSKT.xlsx           <- Cost Center master (MAX Valid To lookup)
│
├── Join Date & Year of Service/
│   └── IKP_PA0041.xlsx         <- Date types (filtered for Date Type 01)
│
└── Position Effective Date & Current Tenure/
    └── IKP_HRP1001.xlsx        <- Position history (Object ID & Start Date)
```

---

## 📦 Output Deliverables

| Output File | Description |
|---|---|
| **`FINAL_HR_Topic_Report_YYYYMMDD.xlsx`** | **Final consolidated report** with all 45 columns matching `IKP_Headings.xlsx` layout. |
| **`00_processing_summary.xlsx`** | Executive audit summary: row counts, matched/unmatched statistics, and module status. |
| **`intermediate/`** | Enriched output files from each individual module. |
| **`logs/YYYYMMDD_HHMMSS.log`** | Detailed runtime logs with timestamped diagnostics. |

---

## ⚙️ Module Toggles (`config/settings.json`)

You can enable or disable individual modules at any time:

```json
{
    "run_modules": {
        "contract_type":    true,
        "education":        true,
        "entity_division":  true,
        "cost_center":      true,
        "join_date":        true,
        "position_tenure":  true,
        "assembler":        true
    }
}
```
