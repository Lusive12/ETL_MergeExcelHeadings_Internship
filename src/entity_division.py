"""
Automation: Entity, Division, Area, Function
============================================================
Input:  input/Entity, Division, Area, Function/ZHR_MAP_ENTITY.xlsx
        input/Entity, Division, Area, Function/ZHR_MASTER_DIVISION.xlsx
        input/Shared/IKP_PQAH.xlsx
Output: output/intermediate/IKP_PQAH_With_Entity_DivisionDesc_Area_Function.xlsx

Logic:
  - Step 1: Join ZHR_MAP_ENTITY with ZHR_MASTER_DIVISION on Division == DivCode -> Div Desc.
  - Step 2: Composite key join onto IKP_PQAH (PArea | Subarea == Personnel area | Personnel subarea).
  - Enriches Entity, Division (Div Desc), Area, Function.
"""
import logging
from pathlib import Path
import pandas as pd

from src.common import (normalize_id, load_excel, get_required_column_ci,
                        find_column_ci)
from src.validator import (validate_file_exists, validate_columns,
                            validate_row_count)
from src.excel_export import export_df

INPUT_DIR    = Path("input/Entity, Division, Area, Function")
MAP_FILE     = INPUT_DIR / "ZHR_MAP_ENTITY.xlsx"
DIV_FILE     = INPUT_DIR / "ZHR_MASTER_DIVISION.xlsx"
PQAH_FILE    = Path("input/Shared/IKP_PQAH.xlsx")
OUTPUT_FILE  = Path("output/intermediate/IKP_PQAH_With_Entity_DivisionDesc_Area_Function.xlsx")


def run(logger: logging.Logger) -> dict:
    module = "Entity, Division, Area, Function"
    result = {
        "Module": module, "Input Rows": 0, "Output Rows": 0,
        "Matched": 0, "Unmatched": 0,
        "Status": "FAILED", "Output File": OUTPUT_FILE.name,
    }

    try:
        validate_file_exists(MAP_FILE,  logger)
        validate_file_exists(DIV_FILE,  logger)
        validate_file_exists(PQAH_FILE, logger)

        map_df  = load_excel(MAP_FILE)
        div_df  = load_excel(DIV_FILE)
        pqah_df = load_excel(PQAH_FILE)
        input_rows = len(pqah_df)
        result["Input Rows"] = input_rows
        logger.info(f"[EntityDivision] Map: {len(map_df):,} rows | Div: {len(div_df):,} rows | PQAH: {input_rows:,} rows")

        validate_columns(map_df,  ["Personnel area", "Personnel subarea", "Entity", "Division", "Area", "Function"], "ZHR_MAP_ENTITY.xlsx", logger)
        validate_columns(div_df,  ["DivCode", "Div Desc"], "ZHR_MASTER_DIVISION.xlsx", logger)
        validate_columns(pqah_df, ["PArea", "Subarea"],    "IKP_PQAH.xlsx", logger)

        div_code_col = get_required_column_ci(div_df, "DivCode")
        div_desc_col = get_required_column_ci(div_df, "Div Desc")
        map_div_col  = get_required_column_ci(map_df, "Division")

        # Step 1: Map Division code to Div Desc
        div_df["_div_norm"] = normalize_id(div_df[div_code_col])
        div_lookup = div_df.drop_duplicates(subset=["_div_norm"]).set_index("_div_norm")[div_desc_col]

        map_df["_map_div_norm"] = normalize_id(map_df[map_div_col])
        map_df["Div Desc"] = map_df["_map_div_norm"].map(div_lookup).fillna(map_df[map_div_col])

        # Step 2: Composite key matching
        map_parea_col    = get_required_column_ci(map_df, "Personnel area")
        map_psubarea_col = get_required_column_ci(map_df, "Personnel subarea")
        pqah_parea_col   = get_required_column_ci(pqah_df, "PArea")
        pqah_subarea_col = get_required_column_ci(pqah_df, "Subarea")

        map_df["_comp_key"] = normalize_id(map_df[map_parea_col]) + "|" + normalize_id(map_df[map_psubarea_col])
        master_map = map_df.drop_duplicates(subset=["_comp_key"]).set_index("_comp_key")

        pqah_df["_comp_key"] = normalize_id(pqah_df[pqah_parea_col]) + "|" + normalize_id(pqah_df[pqah_subarea_col])

        entity_col   = get_required_column_ci(map_df, "Entity")
        area_col     = get_required_column_ci(map_df, "Area")
        func_col     = get_required_column_ci(map_df, "Function")

        pqah_df["Entity"]   = pqah_df["_comp_key"].map(master_map[entity_col])
        pqah_df["Division"] = pqah_df["_comp_key"].map(master_map["Div Desc"])
        pqah_df["Area"]     = pqah_df["_comp_key"].map(master_map[area_col])
        pqah_df["Function"] = pqah_df["_comp_key"].map(master_map[func_col])

        matched = int(pqah_df["Entity"].notna().sum())
        unmatched = int(pqah_df["Entity"].isna().sum())

        pqah_df = pqah_df.drop(columns=["_comp_key"], errors="ignore")

        validate_row_count(input_rows, len(pqah_df), module, logger)
        export_df(pqah_df, OUTPUT_FILE, logger)

        result.update({
            "Output Rows": len(pqah_df), "Matched": matched,
            "Unmatched": unmatched, "Status": "SUCCESS",
        })
        logger.info(f"[EntityDivision] Completed successfully. Matched={matched:,}, Unmatched={unmatched:,}")

    except Exception as e:
        logger.error(f"[EntityDivision] FAILED: {e}")

    return result
