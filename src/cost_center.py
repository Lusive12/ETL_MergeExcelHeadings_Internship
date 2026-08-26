"""
Automation 1: General Cost Center Enrichment
============================================================
Input:  input/General Cost Center & Cost Center Text/IKP_IT0027.xlsx
        input/General Cost Center & Cost Center Text/IKP_CSKT.xlsx
Output: output/intermediate/IT0027_Enriched_CostCenterDesc.xlsx

Logic:
  - Auto-detect all Cost Center columns by name (regex: ^Cost Center([.]\d+)?$)
  - Build CSKT lookup: per Cost Center, keep row with MAX(Valid To)
  - For each CC column, LEFT JOIN -> get Description by column NAME
  - Insert Description column immediately after its CC column
  - Preserve all rows (LEFT JOIN, no row loss)
"""
import re
import logging
import pandas as pd
from pathlib import Path

from src.common import normalize_id, load_excel, get_required_column_ci
from src.validator import (validate_file_exists, validate_columns,
                            validate_row_count)
from src.excel_export import export_df

INPUT_DIR   = Path("input/General Cost Center & Cost Center Text")
IT0027_FILE = INPUT_DIR / "IKP_IT0027.xlsx"
CSKT_FILE   = INPUT_DIR / "IKP_CSKT.xlsx"
OUTPUT_FILE = Path("output/intermediate/IT0027_Enriched_CostCenterDesc.xlsx")

CSKT_REQUIRED = ["Cost Center", "Valid To", "Description"]
CC_PATTERN    = re.compile(r"^cost\s*center(\.\d+)?$", re.IGNORECASE)


def run(logger: logging.Logger) -> dict:
    module = "General Cost Center"
    result = {
        "Module": module, "Input Rows": 0, "Output Rows": 0,
        "Matched": 0, "Unmatched": 0,
        "Status": "FAILED", "Output File": OUTPUT_FILE.name,
    }

    try:
        validate_file_exists(IT0027_FILE, logger)
        validate_file_exists(CSKT_FILE,   logger)

        it0027 = load_excel(IT0027_FILE)
        cskt   = load_excel(CSKT_FILE)
        input_rows = len(it0027)
        result["Input Rows"] = input_rows
        logger.info(f"[CostCenter] IT0027: {input_rows:,} rows | CSKT: {len(cskt):,} rows")

        validate_columns(cskt, CSKT_REQUIRED, "IKP_CSKT.xlsx", logger)

        cskt_cc_col    = get_required_column_ci(cskt, "Cost Center")
        cskt_valto_col = get_required_column_ci(cskt, "Valid To")
        cskt_desc_col  = get_required_column_ci(cskt, "Description")

        # Build lookup: per Cost Center, keep row with MAX Valid To
        cskt["_cc_norm"] = normalize_id(cskt[cskt_cc_col])
        cskt["_val_to"]  = pd.to_datetime(cskt[cskt_valto_col], errors="coerce")
        cskt_lookup = (
            cskt.sort_values("_val_to", ascending=False)
                .drop_duplicates(subset=["_cc_norm"], keep="first")
                .set_index("_cc_norm")[cskt_desc_col]
        )
        logger.info(f"[CostCenter] Lookup built: {len(cskt_lookup):,} unique CCs")

        # Auto-detect Cost Center columns by name case-insensitively
        cc_cols = [c for c in it0027.columns if CC_PATTERN.match(str(c).strip())]
        if not cc_cols:
            raise ValueError("[CostCenter] No 'Cost Center' columns found in IT0027.")
        logger.info(f"[CostCenter] Detected {len(cc_cols)} CC column(s): {cc_cols}")

        result_df = it0027.copy()
        total_matched, total_unmatched = 0, 0

        for cc_col in cc_cols:
            desc_col   = f"{cc_col} Description"
            normalized = normalize_id(result_df[cc_col])
            result_df[desc_col] = normalized.map(cskt_lookup)

            blank     = normalized == ""
            matched   = (~result_df[desc_col].isna()) & (~blank)
            unmatched = result_df[desc_col].isna() & (~blank)
            total_matched   += int(matched.sum())
            total_unmatched += int(unmatched.sum())
            logger.info(
                f"[CostCenter] '{cc_col}': matched={matched.sum():,}, "
                f"unmatched={unmatched.sum():,}, blank_key={blank.sum():,}"
            )

        # Reorder: each CC column immediately followed by its Description
        ordered = []
        for col in it0027.columns:
            ordered.append(col)
            if CC_PATTERN.match(str(col).strip()):
                ordered.append(f"{col} Description")
        result_df = result_df[ordered]

        validate_row_count(input_rows, len(result_df), module, logger)
        export_df(result_df, OUTPUT_FILE, logger)

        result.update({
            "Output Rows": len(result_df), "Matched": total_matched,
            "Unmatched": total_unmatched, "Status": "SUCCESS",
        })
        logger.info("[CostCenter] Completed successfully.")

    except Exception as e:
        logger.error(f"[CostCenter] FAILED: {e}")

    return result
