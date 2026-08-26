"""
Automation: Education, Institute & Branch of Study
============================================================
Input:  input/Education, Institute, Branch of Study/IKP_IT0022.xlsx
        input/Education, Institute, Branch of Study/Order_IKP_IT0022.xlsx
        input/Education, Institute, Branch of Study/IKP_Branch of Study.xlsx
Output: output/intermediate/IKP_IT0022_HighestOrder_IgnoreTraining_WithBranchText.xlsx

Logic:
  - Exclude training records (Subtype != 10, Order != 11).
  - Map qualification rank from Order_IKP_IT0022.
  - Per employee, sort by Order descending, keep top 1 highest qualification.
  - Lookup Branch of Study Text from IKP_Branch of Study.
  - Export enriched highest education per employee.
"""
import logging
from pathlib import Path
import pandas as pd

from src.common import (normalize_id, load_excel, get_required_column_ci,
                        find_column_ci)
from src.validator import (validate_file_exists, validate_columns,
                            validate_row_count)
from src.excel_export import export_df

INPUT_DIR      = Path("input/Education, Institute, Branch of Study")
IT0022_FILE    = INPUT_DIR / "IKP_IT0022.xlsx"
ORDER_FILE     = INPUT_DIR / "Order_IKP_IT0022.xlsx"
BRANCH_FILE    = INPUT_DIR / "IKP_Branch of Study.xlsx"
OUTPUT_FILE    = Path("output/intermediate/IKP_IT0022_HighestOrder_IgnoreTraining_WithBranchText.xlsx")


def run(logger: logging.Logger) -> dict:
    module = "Education, Institute & Branch of Study"
    result = {
        "Module": module, "Input Rows": 0, "Output Rows": 0,
        "Matched": 0, "Unmatched": 0,
        "Status": "FAILED", "Output File": OUTPUT_FILE.name,
    }

    try:
        validate_file_exists(IT0022_FILE, logger)
        validate_file_exists(ORDER_FILE,  logger)
        validate_file_exists(BRANCH_FILE, logger)

        it0022 = load_excel(IT0022_FILE)
        order  = load_excel(ORDER_FILE)
        branch = load_excel(BRANCH_FILE)
        input_rows = len(it0022)
        result["Input Rows"] = input_rows
        logger.info(f"[Education] IT0022: {input_rows:,} rows | Order: {len(order):,} rows | Branch: {len(branch):,} rows")

        validate_columns(it0022, ["Personnel Number", "Subtype"], "IKP_IT0022.xlsx", logger)
        validate_columns(order,  ["Key", "Order", "Text"],        "Order_IKP_IT0022.xlsx", logger)
        validate_columns(branch, ["Branch of Study", "Branch of Study Text"], "IKP_Branch of Study.xlsx", logger)

        pno_col     = get_required_column_ci(it0022, "Personnel Number")
        subtype_col = get_required_column_ci(it0022, "Subtype")

        ord_key_col  = get_required_column_ci(order, "Key")
        ord_rank_col = get_required_column_ci(order, "Order")
        ord_text_col = get_required_column_ci(order, "Text")

        br_key_col  = get_required_column_ci(branch, "Branch of Study")
        br_text_col = get_required_column_ci(branch, "Branch of Study Text")

        # 1. Filter out training Subtype 10
        df = it0022.copy()
        df["_pno_norm"]     = normalize_id(df[pno_col])
        df["_subtype_norm"] = normalize_id(df[subtype_col])
        df = df[df["_subtype_norm"] != "10"].copy()

        # 2. Join Order ranking
        order["_ord_key_norm"] = normalize_id(order[ord_key_col])
        order["_order_num"]    = pd.to_numeric(order[ord_rank_col], errors="coerce").fillna(0)

        df = df.merge(order[["_ord_key_norm", "_order_num", ord_text_col]],
                      left_on="_subtype_norm", right_on="_ord_key_norm", how="left")

        # Filter out training Order 11
        df = df[df["_order_num"] != 11].copy()

        # 3. Sort by employee and Order descending, keep highest degree
        df = df.sort_values(by=["_pno_norm", "_order_num"], ascending=[True, False])
        highest_edu = df.drop_duplicates(subset=["_pno_norm"], keep="first").copy()

        # 4. Lookup Branch of Study Text
        branch_src_col = find_column_ci(highest_edu, "Branch of Study 1") or find_column_ci(highest_edu, "Branch of Study")
        if branch_src_col:
            branch["_br_key_norm"] = normalize_id(branch[br_key_col]).str.zfill(5)
            br_lookup = branch.drop_duplicates(subset=["_br_key_norm"]).set_index("_br_key_norm")[br_text_col]
            highest_edu["_br_src_norm"] = normalize_id(highest_edu[branch_src_col]).str.zfill(5)
            highest_edu["Branch of Study Text"] = highest_edu["_br_src_norm"].map(br_lookup)
            highest_edu = highest_edu.drop(columns=["_br_src_norm"], errors="ignore")

        # Standardize output column names
        if ord_text_col in highest_edu.columns:
            highest_edu["Education"] = highest_edu[ord_text_col]
        
        inst_col = find_column_ci(highest_edu, "Educational est.") or find_column_ci(highest_edu, "Institute")
        if inst_col:
            highest_edu["Institute"] = highest_edu[inst_col]

        highest_edu = highest_edu.drop(columns=["_pno_norm", "_subtype_norm", "_ord_key_norm", "_order_num"], errors="ignore")

        matched = int(highest_edu["Education"].notna().sum()) if "Education" in highest_edu.columns else len(highest_edu)
        unmatched = len(highest_edu) - matched

        export_df(highest_edu, OUTPUT_FILE, logger)

        result.update({
            "Output Rows": len(highest_edu), "Matched": matched,
            "Unmatched": unmatched, "Status": "SUCCESS",
        })
        logger.info(f"[Education] Completed successfully. Unique employees with highest edu: {len(highest_edu):,}")

    except Exception as e:
        logger.error(f"[Education] FAILED: {e}")

    return result
