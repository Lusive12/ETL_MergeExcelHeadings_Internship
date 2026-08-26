# HR Data Automation Suite

Monthly HR report automation converts raw SAP exports into enriched Excel reports automatically.

## How to use (for HR staff)

1. Export your data from SAP
2. Place the files in the correct folder inside `input/`

   | File | Place in folder |
   |------|----------------|
   | `IKP_IT0027.xlsx` | `input/GENERAL_COST_CENTER/` |
   | `IKP_CSKT.xlsx`   | `input/GENERAL_COST_CENTER/` |
   | `IKP_PQAH.xlsx`   | `input/JOIN_DATE/` |
   | `IKP_PA0041.xlsx` | `input/JOIN_DATE/` |
   | `IKP_PQAH.xlsx`   | `input/POSITION_TENURE/` |
   | `IKP_HRP1001.xlsx`| `input/POSITION_TENURE/` |

3. Double-click **RUN_ME.bat**
4. Wait for the green "COMPLETED SUCCESSFULLY" message
5. Collect your results from the `output/` folder

## Output files

| File | Contents |
|------|---------|
| `00_processing_summary.xlsx` | Overview of all modules: matched/unmatched counts, status |
| `01_general_cost_center_result.xlsx` | IT0027 with Cost Center Descriptions added |
| `02_join_date_years_of_service_result.xlsx` | PQAH with Join Date and Years of Service |
| `03_position_effective_date_current_tenure_result.xlsx` | PQAH with Earliest Start Date and Current Tenure |

## Rules

- **Do not rename** the input files â€” names must match exactly.
- **Close any open Excel files** before running. Output files cannot be overwritten if open.
- Check the `logs/` folder if something goes wrong.

## For developers

- All business logic is in `src/`
- Module toggles: edit `config/settings.json`
- Add a new module: create `src/your_module.py` with a `run(logger) -> dict` function, then register it in `run.py`
