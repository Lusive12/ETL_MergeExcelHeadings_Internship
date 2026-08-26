"""
Automation: Contract Type & Contract End Date
============================================================
Input:  input/Contract Type & Contract End Data/IKP_PA0016.xlsx
        input/Contract Type & Contract End Data/IKP_Contract Type.xlsx
Output: output/intermediate/IKP_PA0016_With_ContractType_Description.xlsx

Logic:
  - Load PA0016 and IKP_Contract Type.
  - Normalize Contract Type ID.
  - Lookup Contract Type Description from lookup table.
  - Keep 'Contract Type' description and 'Contract End Date'.
  - Row preservation check & export to intermediate folder.
"""
import logging
from pathlib import Path
import pandas as pd

from src.common import (normalize_id, load_excel, get_required_column_ci,
                        find_column_ci)
from src.validator import (validate_file_exists, validate_columns,
                            validate_row_count)
from src.excel_export import export_df

INPUT_DIR   = Path("input/Contract Type & Contract End Data")
PA0016_FILE = INPUT_DIR / "IKP_PA0016.xlsx"
LOOKUP_FILE = INPUT_DIR / "IKP_Contract Type.xlsx"
OUTPUT_FILE = Path("output/intermediate/IKP_PA0016_With_ContractType_Description.xlsx")

PA0016_REQUIRED = ["Personnel number", "Contract Type"]
LOOKUP_REQUIRED = ["Contract Type", "Contract type text"]


def run(logger: logging.Logger) -> dict:
    module = "Contract Type & Contract End Date"
    result = {
        "Module": module, "Input Rows": 0, "Output Rows": 0,
        "Matched": 0, "Unmatched": 0,
        "Status": "FAILED", "Output File": OUTPUT_FILE.name,
    }

    try:
        validate_file_exists(PA0016_FILE, logger)
        validate_file_exists(LOOKUP_FILE, logger)

        pa0016 = load_excel(PA0016_FILE)
        lookup = load_excel(LOOKUP_FILE)
        input_rows = len(pa0016)
        result["Input Rows"] = input_rows
        logger.info(f"[ContractType] PA0016: {input_rows:,} rows | Lookup: {len(lookup):,} rows")

        validate_columns(pa0016, ["Personnel number", "Contract Type"], "IKP_PA0016.xlsx", logger)
        validate_columns(lookup, ["Contract Type", "Contract type text"], "IKP_Contract Type.xlsx", logger)

        pno_col   = get_required_column_ci(pa0016, "Personnel number")
        ctype_col = get_required_column_ci(pa0016, "Contract Type")

        lookup_key = get_required_column_ci(lookup, "Contract Type")
        lookup_val = get_required_column_ci(lookup, "Contract type text")

        # Build lookup dict
        lookup["_key_norm"] = normalize_id(lookup[lookup_key])
        ct_lookup = (
            lookup.drop_duplicates(subset=["_key_norm"], keep="first")
                  .set_index("_key_norm")[lookup_val]
        )

        result_df = pa0016.copy()
        result_df["_ct_norm"] = normalize_id(result_df[ctype_col])
        result_df["Contract Type Description"] = result_df["_ct_norm"].map(ct_lookup)

        # Detect Contract End Date column if available
        end_date_col = find_column_ci(result_df, "Contract End Date") or find_column_ci(result_df, "Contract end") or find_column_ci(result_df, "End Date")
        if end_date_col and end_date_col != "Contract End Date":
            result_df["Contract End Date"] = result_df[end_date_col]

        matched = int((result_df["Contract Type Description"].notna() & (result_df["_ct_norm"] != "")).sum())
        unmatched = int((result_df["Contract Type Description"].isna() & (result_df["_ct_norm"] != "")).sum())

        result_df = result_df.drop(columns=["_ct_norm"], errors="ignore")

        validate_row_count(input_rows, len(result_df), module, logger)
        export_df(result_df, OUTPUT_FILE, logger)

        result.update({
            "Output Rows": len(result_df), "Matched": matched,
            "Unmatched": unmatched, "Status": "SUCCESS",
        })
        logger.info(f"[ContractType] Completed successfully. Matched={matched:,}, Unmatched={unmatched:,}")

    except Exception as e:
        logger.error(f"[ContractType] FAILED: {e}")

    return result
