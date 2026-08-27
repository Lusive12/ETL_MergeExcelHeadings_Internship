"""
Automation: Education, Institute & Branch of Study
============================================================
Input:  input/Education, Institute, Branch of Study/IKP_IT0022.xlsx
        input/Education, Institute, Branch of Study/Order_IKP_IT0022.xlsx
        input/Education, Institute, Branch of Study/IKP_Branch of Study.xlsx
Output: output/intermediate/IKP_IT0022_HighestOrder_IgnoreTraining_WithBranchText.xlsx

Logic:
  Step 1: Join Order table onto IT0022.
          "Educational est." in IT0022 == "Key" in Order_IKP_IT0022.xlsx
          Educational est. values: "2", "3" etc. -> zero-pad to "02", "03" to match Key.
          This brings in: Key, Order, Text

  Step 2: Exclude training records:
          - Key == "10" (Training key)
          - Order == 11 (Training order as int)

  Step 3: Per employee (Personnel number), sort by Order DESCENDING (numeric),
          keep first row = highest qualification.

  Step 4: BranchCodeNorm = Branch of Study 1 zero-padded to 5 digits
          e.g. "40" -> "00040"

  Step 5: Lookup Branch of Study Text from IKP_Branch of Study.xlsx:
          BranchCodeNorm == Branch of Study column in lookup -> pull Branch of Study Text

Output columns (in order):
  All original IT0022 columns + Key + Text + Order + BranchCodeNorm + Branch of Study Text
  (No synthetic "Education" or "Institute" columns added)

Assembler reads:
  "Text"             -> Education level (e.g. University/S1)
  "Institute/location" -> Institute name
  "Branch of Study Text" -> Branch of study
"""
import logging
from pathlib import Path
import pandas as pd

from src.common import (normalize_id, load_excel, get_required_column_ci,
                        find_column_ci)
from src.validator import (validate_file_exists, validate_columns)
from src.excel_export import export_df

INPUT_DIR   = Path("input/Education, Institute, Branch of Study")
IT0022_FILE = INPUT_DIR / "IKP_IT0022.xlsx"
ORDER_FILE  = INPUT_DIR / "Order_IKP_IT0022.xlsx"
BRANCH_FILE = INPUT_DIR / "IKP_Branch of Study.xlsx"
OUTPUT_FILE = Path("output/intermediate/IKP_IT0022_HighestOrder_IgnoreTraining_WithBranchText.xlsx")

TRAINING_KEY   = "10"   # Key value that means Training
TRAINING_ORDER = 11     # Order value that means Training


def _zfill2(s: str) -> str:
    """Zero-pad a numeric string to 2 digits. '2' -> '02', '10' -> '10'."""
    s = s.strip()
    if s.isdigit():
        return s.zfill(2)
    return s


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

        # ── Validate required columns ─────────────────────────────────────────
        validate_columns(it0022, ["Personnel number", "Educational est.", "Branch of Study 1"],
                         "IKP_IT0022.xlsx", logger)
        validate_columns(order,  ["Key", "Order", "Text"],
                         "Order_IKP_IT0022.xlsx", logger)
        validate_columns(branch, ["Branch of Study", "Branch of Study Text"],
                         "IKP_Branch of Study.xlsx", logger)

        pno_col     = get_required_column_ci(it0022, "Personnel number")
        edu_est_col = get_required_column_ci(it0022, "Educational est.")
        branch1_col = get_required_column_ci(it0022, "Branch of Study 1")

        ord_key_col  = get_required_column_ci(order, "Key")
        ord_ord_col  = get_required_column_ci(order, "Order")
        ord_text_col = get_required_column_ci(order, "Text")

        br_key_col  = get_required_column_ci(branch, "Branch of Study")
        br_text_col = get_required_column_ci(branch, "Branch of Study Text")

        # ── Step 1: Normalize keys then join ──────────────────────────────────
        # Educational est. values: "2", "3" -> zero-pad to "02", "03" to match Order Keys
        it0022["_edu_zfill"] = (
            normalize_id(it0022[edu_est_col])
            .apply(_zfill2)
        )

        # Normalize Order keys (already "01", "02" format, but normalize anyway)
        order["_ord_key_norm"] = normalize_id(order[ord_key_col]).apply(_zfill2)

        # Convert Order column to numeric for comparison and sorting
        order["_order_num"] = pd.to_numeric(
            normalize_id(order[ord_ord_col]), errors="coerce"
        ).fillna(0).astype(int)

        logger.info(f"[Education] Order keys: {sorted(order['_ord_key_norm'].tolist())}")
        logger.info(f"[Education] Sample IT0022 edu keys (after zfill): {sorted(it0022['_edu_zfill'].dropna().unique().tolist())}")

        # Build lookup dicts: Key -> Order (numeric), Key -> Text
        order_dedup    = order.drop_duplicates(subset=["_ord_key_norm"]).set_index("_ord_key_norm")
        order_num_map  = order_dedup["_order_num"]
        order_text_map = order_dedup[ord_text_col]

        # Key = the zero-padded edu code itself (only when it exists in Order table)
        it0022["Key"]   = it0022["_edu_zfill"].where(it0022["_edu_zfill"].isin(order_dedup.index))
        it0022["Order"] = it0022["_edu_zfill"].map(order_num_map)    # 2, 7 etc. (int)
        it0022["Text"]  = it0022["_edu_zfill"].map(order_text_map)   # "University/S1" etc.

        # Log how many rows got a match
        matched_order = int(it0022["Key"].notna().sum())
        logger.info(f"[Education] Order join: {matched_order:,}/{input_rows:,} rows matched")
        if matched_order < input_rows:
            unmatched_keys = it0022[it0022["Key"].isna()]["_edu_zfill"].unique().tolist()
            logger.warning(f"[Education] Unmatched edu keys: {unmatched_keys}")

        # ── Step 2: Exclude training records ──────────────────────────────────
        before_filter = len(it0022)
        mask_training = (
            (it0022["Key"] == TRAINING_KEY) |
            (it0022["Order"] == TRAINING_ORDER)
        )
        excluded = int(mask_training.sum())
        it0022_filtered = it0022[~mask_training].copy()
        logger.info(
            f"[Education] Excluded {excluded:,} training records "
            f"(Key={TRAINING_KEY!r} or Order={TRAINING_ORDER}). "
            f"Remaining: {len(it0022_filtered):,}"
        )

        # ── Step 3: Keep highest Order per employee ───────────────────────────
        it0022_filtered["_pno_norm"] = normalize_id(it0022_filtered[pno_col])
        it0022_filtered = it0022_filtered.sort_values(
            by=["_pno_norm", "Order"], ascending=[True, False]
        )
        highest_edu = it0022_filtered.drop_duplicates(
            subset=["_pno_norm"], keep="first"
        ).copy()
        logger.info(f"[Education] Unique employees with highest education: {len(highest_edu):,}")

        # ── Step 4: BranchCodeNorm = zero-pad Branch of Study 1 to 5 digits ──
        highest_edu["_br1_norm"] = normalize_id(highest_edu[branch1_col])
        highest_edu["BranchCodeNorm"] = highest_edu["_br1_norm"].apply(
            lambda x: x.zfill(5) if x.isdigit() else ""
        )

        # ── Step 5: Lookup Branch of Study Text ───────────────────────────────
        branch["_br_key_norm"] = normalize_id(branch[br_key_col])
        br_lookup = (
            branch.drop_duplicates(subset=["_br_key_norm"])
                  .set_index("_br_key_norm")[br_text_col]
        )
        highest_edu["Branch of Study Text"] = highest_edu["BranchCodeNorm"].map(br_lookup)

        matched_branch   = int(highest_edu["Branch of Study Text"].notna().sum())
        unmatched_branch = int(highest_edu["Branch of Study Text"].isna().sum())
        logger.info(
            f"[Education] Branch lookup: matched={matched_branch:,}, "
            f"unmatched={unmatched_branch:,}"
        )

        # ── Drop internal helper columns ───────────────────────────────────────
        highest_edu = highest_edu.drop(
            columns=["_edu_zfill", "_pno_norm", "_br1_norm"], errors="ignore"
        )

        logger.info(f"[Education] Output columns ({len(highest_edu.columns)}): {list(highest_edu.columns)}")
        # logger.info(
        #     f"[Education] Sample Key/Order/Text:\n"
        #     + highest_edu[["Key", "Order", "Text"]].head(5).to_string(index=False)
        # )

        export_df(highest_edu, OUTPUT_FILE, logger)

        result.update({
            "Output Rows":  len(highest_edu),
            "Matched":      matched_branch,
            "Unmatched":    unmatched_branch,
            "Status":       "SUCCESS",
        })
        logger.info("[Education] Completed successfully.")

    except Exception as e:
        logger.error(f"[Education] FAILED: {e}")

    return result
