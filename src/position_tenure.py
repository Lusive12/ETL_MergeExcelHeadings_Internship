"""
Automation 3: Position Effective Date & Current Tenure
============================================================
Input:  input/Shared/IKP_PQAH.xlsx
        input/Position Effective Date & Current Tenure/IKP_HRP1001.xlsx
Output: output/intermediate/PQAH_Enriched_PositionTenure.xlsx

Logic:
  - Build composite key: normalize(Personnel No.) + "|" + normalize(Position)
    Exact case-insensitive match on "Personnel No." and "Position".
  - In HRP1001: strip leading zeros from "ID of related object"
  - Match "Start Date" and "Object ID"
  - Select MIN(Start Date) per composite key
  - LEFT JOIN onto PQAH
  - Current Tenure (Years) = (today - Earliest Start Date).days / 365.25, round 2dp
"""
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime

from src.common import (normalize_id, strip_leading_zeros, load_excel,
                        get_required_column_ci)
from src.validator import (validate_file_exists, validate_columns,
                            validate_row_count, validate_dates)
from src.excel_export import export_df

SHARED_DIR   = Path("input/Shared")
PQAH_FILE    = SHARED_DIR / "IKP_PQAH.xlsx"
HRP1001_FILE = Path("input/Position Effective Date & Current Tenure/IKP_HRP1001.xlsx")
OUTPUT_FILE  = Path("output/intermediate/PQAH_Enriched_PositionTenure.xlsx")

PQAH_REQUIRED    = ["Personnel No.", "Position"]
HRP1001_REQUIRED = ["Object ID", "ID of related object", "Start Date"]


def run(logger: logging.Logger) -> dict:
    module = "Position Effective Date & Current Tenure"
    result = {
        "Module": module, "Input Rows": 0, "Output Rows": 0,
        "Matched": 0, "Unmatched": 0,
        "Status": "FAILED", "Output File": OUTPUT_FILE.name,
    }

    try:
        validate_file_exists(PQAH_FILE,    logger)
        validate_file_exists(HRP1001_FILE, logger)

        pqah = load_excel(PQAH_FILE)
        hrp  = load_excel(HRP1001_FILE)
        input_rows = len(pqah)
        result["Input Rows"] = input_rows
        logger.info(f"[PosTenure] PQAH: {input_rows:,} rows | HRP1001: {len(hrp):,} rows")

        validate_columns(pqah, PQAH_REQUIRED,    "IKP_PQAH.xlsx",    logger)
        validate_columns(hrp,  HRP1001_REQUIRED, "IKP_HRP1001.xlsx", logger)

        pqah_pno_col = get_required_column_ci(pqah, "Personnel No.")
        pqah_pos_col = get_required_column_ci(pqah, "Position")

        hrp_obj_col = get_required_column_ci(hrp, "Object ID")
        hrp_id_col  = get_required_column_ci(hrp, "ID of related object")
        hrp_dt_col  = get_required_column_ci(hrp, "Start Date")

        # Composite key for PQAH strictly using "Personnel No." and "Position"
        pqah["_key"] = (
            normalize_id(pqah[pqah_pno_col]) + "|" +
            normalize_id(pqah[pqah_pos_col])
        )

        # Composite key for HRP1001 (strip leading zeros from "ID of")
        hrp["_id_norm"] = strip_leading_zeros(normalize_id(hrp[hrp_id_col]))
        hrp["_key"]     = hrp["_id_norm"] + "|" + normalize_id(hrp[hrp_obj_col])

        # MIN Start Date per composite key
        hrp["_dt_parsed"] = pd.to_datetime(hrp[hrp_dt_col], errors="coerce")
        validate_dates(hrp["_dt_parsed"], f"{hrp_dt_col} (HRP1001)", logger)

        min_dates = (
            hrp.groupby("_key")["_dt_parsed"].min().reset_index()
        )
        min_dates.columns = ["_key", "Position Effective Date"]
        logger.info(f"[PosTenure] Unique composite keys in HRP1001: {len(min_dates):,}")

        merged = pqah.merge(min_dates, on="_key", how="left")

        today = pd.Timestamp(datetime.today().date())
        merged["Current Tenure (Years)"] = (
            (today - merged["Position Effective Date"]).dt.days / 365.25
        ).round(2)

        matched   = int(merged["Position Effective Date"].notna().sum())
        unmatched = int(merged["Position Effective Date"].isna().sum())
        logger.info(f"[PosTenure] Matched={matched:,}, Unmatched={unmatched:,}")

        merged = merged.drop(columns=["_key", "_id_norm"], errors="ignore")

        validate_row_count(input_rows, len(merged), module, logger)
        export_df(merged, OUTPUT_FILE, logger)

        result.update({
            "Output Rows": len(merged), "Matched": matched,
            "Unmatched": unmatched, "Status": "SUCCESS",
        })
        logger.info("[PosTenure] Completed successfully.")

    except Exception as e:
        logger.error(f"[PosTenure] FAILED: {e}")

    return result
