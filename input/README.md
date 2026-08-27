# 📥 Input Folder — File Placement Guide

This folder contains all source data files required by the HR Report Automation pipeline.

> ⚠️ **Important:** Do not rename any files. The pipeline searches for files by their exact names.
> All files must be in `.xlsx` format (Excel Workbook).

---

## Folder Structure

```
input/
├── Shared/                             ← Master reference files — used by ALL modules
├── Contract Type & Contract End Data/  ← Module 1 inputs
├── Education, Institute, Branch of Study/ ← Module 2 inputs
├── Entity, Division, Area, Function/   ← Module 3 inputs
├── General Cost Center & Cost Center Text/ ← Module 4 inputs
├── Join Date & Year of Service/        ← Module 5 inputs
└── Position Effective Date & Current Tenure/ ← Module 6 inputs
```

---

## Monthly Refresh Checklist

Before every run, ensure all files below are present and up to date:

| Folder | File | Export Source | Refresh Frequency |
|--------|------|--------------|-------------------|
| Shared | `IKP_PQAH.xlsx` | SAP PQAH report | Monthly |
| Shared | `IKP_Headings.xlsx` | Template (static) | As needed |
| Shared | `IKP_Direct_Spv.xlsx` | SAP Direct Supervisor report | Monthly |
| Shared | `IKP_PA0105.xlsx` | SAP PA0105 (email) | Monthly |
| Shared | `IKP_Job_Layer.xlsx` | Master data (static) | As needed |
| Contract Type... | `IKP_PA0016.xlsx` | SAP PA0016 | Monthly |
| Contract Type... | `Contract Type_IKP_IT0016.xlsx` | Master data (static) | As needed |
| Education... | `IKP_IT0022.xlsx` | SAP IT0022 | Monthly |
| Education... | `Order_IKP_IT0022.xlsx` | Master data (static) | As needed |
| Education... | `IKP_Branch of Study.xlsx` | Master data (static) | As needed |
| Entity... | `ZHR_MAP_ENTITY.xlsx` | Master data | As needed |
| Entity... | `ZHR_MASTER_DIVISION.xlsx` | Master data | As needed |
| Cost Center... | `IKP_IT0027.xlsx` | SAP IT0027 | Monthly |
| Cost Center... | `IKP_CSKT.xlsx` | Master data | As needed |
| Join Date... | `IKP_PA0041.xlsx` | SAP PA0041 | Monthly |
| Position Tenure... | `IKP_HRP1001.xlsx` | SAP HRP1001 | Monthly |

> 📌 **Static / master files** are reference tables that rarely change. Only refresh them when the business adds new codes or entries.
