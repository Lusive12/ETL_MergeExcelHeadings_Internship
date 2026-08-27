"""
Final Assembler — Topic Report Builder
============================================================
Reads:
  - input/Shared/IKP_Headings.xlsx (Column layout template)
  - input/Shared/IKP_PQAH.xlsx (Base employee records)
  - input/Shared/IKP_Direct_Spv.xlsx (Supervisor NIK & Name)
  - input/Shared/IKP_PA0105.xlsx (Email)
  - input/Shared/IKP_Job_Layer.xlsx (Job Layer)
  - Enriched intermediate files in output/intermediate/

Produces:
  - output/FINAL_HR_Topic_Report_YYYYMMDD.xlsx
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import pandas as pd

from src.common import (normalize_id, load_excel, get_required_column_ci,
                        find_column_ci)
from src.validator import (validate_file_exists, validate_row_count)
from src.excel_export import export_df

SHARED_DIR       = Path("input/Shared")
HEADINGS_FILE    = SHARED_DIR / "IKP_Headings.xlsx"
PQAH_FILE        = SHARED_DIR / "IKP_PQAH.xlsx"

INTER_DIR        = Path("output/intermediate")
OUT_COST_CENTER  = INTER_DIR / "IT0027_Enriched_CostCenterDesc.xlsx"
OUT_JOIN_DATE    = INTER_DIR / "PQAH_Enriched_JoinDate_YoS.xlsx"
OUT_POS_TENURE   = INTER_DIR / "PQAH_Enriched_PositionTenure.xlsx"
OUT_CONTRACT     = INTER_DIR / "IKP_PA0016_With_ContractType_Description.xlsx"
OUT_EDUCATION    = INTER_DIR / "IKP_IT0022_HighestOrder_IgnoreTraining_WithBranchText.xlsx"
OUT_ENTITY       = INTER_DIR / "IKP_PQAH_With_Entity_DivisionDesc_Area_Function.xlsx"

OUTPUT_FINAL     = Path(f"output/FINAL_HR_Topic_Report_{datetime.now():%Y%m%d}.xlsx")


def _find_shared_file(candidates: List[str]) -> Optional[Path]:
    for name in candidates:
        p = SHARED_DIR / name
        if p.exists():
            return p
    return None


def run(logger: logging.Logger) -> dict:
    module = "Final Topic Report Assembler"
    result = {
        "Module": module, "Input Rows": 0, "Output Rows": 0,
        "Matched": 0, "Unmatched": 0,
        "Status": "FAILED", "Output File": OUTPUT_FINAL.name,
    }

    try:
        validate_file_exists(HEADINGS_FILE, logger)
        validate_file_exists(PQAH_FILE,     logger)

        headings_df = load_excel(HEADINGS_FILE)
        target_columns = list(headings_df.columns)
        logger.info(f"[Assembler] Target output template has {len(target_columns)} columns: {target_columns}")

        pqah = load_excel(PQAH_FILE)
        input_rows = len(pqah)
        result["Input Rows"] = input_rows
        logger.info(f"[Assembler] Base PQAH has {input_rows:,} rows.")

        pno_col = get_required_column_ci(pqah, "Personnel No.")
        pqah["_pno_norm"] = normalize_id(pqah[pno_col])

        # Standard PQAH column mappings
        pqah_standard_maps = {
            "Gender text": "Gender",
            "Date of Birth": "Birth Date",
            "Age of employee": "Age",
            "Religious denomination": "Religion",
            "MarSt": "Marital Status",
            "P. SubArea Text": "P. SubArea Text",
        }
        for src_col, tgt_col in pqah_standard_maps.items():
            actual = find_column_ci(pqah, src_col)
            if actual and tgt_col not in pqah.columns:
                pqah[tgt_col] = pqah[actual]

        # 1. Join Enriched Join Date & YoS
        if OUT_JOIN_DATE.exists():
            jd_df = load_excel(OUT_JOIN_DATE)
            jd_pno = get_required_column_ci(jd_df, "Personnel No.")
            jd_df["_pno_norm"] = normalize_id(jd_df[jd_pno])
            cols_to_add = [c for c in ["Join Date", "Year of Service"] if c in jd_df.columns]
            if cols_to_add:
                pqah = pqah.merge(jd_df[["_pno_norm"] + cols_to_add].drop_duplicates(subset=["_pno_norm"]),
                                  on="_pno_norm", how="left")
                logger.info(f"[Assembler] Merged Join Date / YoS columns: {cols_to_add}")

        # 2. Join Enriched Position Tenure
        if OUT_POS_TENURE.exists():
            pt_df = load_excel(OUT_POS_TENURE)
            pt_pno = get_required_column_ci(pt_df, "Personnel No.")
            pt_df["_pno_norm"] = normalize_id(pt_df[pt_pno])
            cols_map = {}
            if "Position Effective Date" in pt_df.columns:
                cols_map["Position Effective Date"] = "Position Effective Date"
            if "Current Tenure (Years)" in pt_df.columns:
                cols_map["Current Tenure (Years)"] = "Current Tenure"
            elif "Current Tenure" in pt_df.columns:
                cols_map["Current Tenure"] = "Current Tenure"

            if cols_map:
                sub_pt = pt_df[["_pno_norm"] + list(cols_map.keys())].rename(columns=cols_map)
                pqah = pqah.merge(sub_pt.drop_duplicates(subset=["_pno_norm"]), on="_pno_norm", how="left")
                logger.info(f"[Assembler] Merged Position Tenure columns: {list(cols_map.values())}")

        # 3. Join Enriched Entity / Division / Area / Function
        if OUT_ENTITY.exists():
            ent_df = load_excel(OUT_ENTITY)
            ent_pno = get_required_column_ci(ent_df, "Personnel No.")
            ent_df["_pno_norm"] = normalize_id(ent_df[ent_pno])
            cols_to_add = [c for c in ["Entity", "Division", "Area", "Function"] if c in ent_df.columns]
            if cols_to_add:
                pqah = pqah.merge(ent_df[["_pno_norm"] + cols_to_add].drop_duplicates(subset=["_pno_norm"]),
                                  on="_pno_norm", how="left")
                logger.info(f"[Assembler] Merged Entity/Division columns: {cols_to_add}")

        # 4. Join Enriched Contract Type & End Date
        if OUT_CONTRACT.exists():
            ct_df = load_excel(OUT_CONTRACT)
            ct_pno = find_column_ci(ct_df, "Personnel number") or find_column_ci(ct_df, "Personnel No.")
            if ct_pno:
                ct_df["_pno_norm"] = normalize_id(ct_df[ct_pno])
                cols_map = {}
                if "Contract Type Description" in ct_df.columns:
                    cols_map["Contract Type Description"] = "Contract Type"
                elif "Contract Type" in ct_df.columns:
                    cols_map["Contract Type"] = "Contract Type"
                if "Contract End Date" in ct_df.columns:
                    cols_map["Contract End Date"] = "Contract End Date"

                sub_ct = ct_df[["_pno_norm"] + list(cols_map.keys())].rename(columns=cols_map)
                pqah = pqah.merge(sub_ct.drop_duplicates(subset=["_pno_norm"]), on="_pno_norm", how="left")
                logger.info(f"[Assembler] Merged Contract columns: {list(cols_map.values())}")

        # 5. Join Enriched Highest Education
        if OUT_EDUCATION.exists():
            edu_df = load_excel(OUT_EDUCATION)
            edu_pno = find_column_ci(edu_df, "Personnel Number") or find_column_ci(edu_df, "Personnel No.")
            if edu_pno:
                edu_df["_pno_norm"] = normalize_id(edu_df[edu_pno])
                cols_map = {}
                if "Education" in edu_df.columns:
                    cols_map["Education"] = "Education"
                if "Institute" in edu_df.columns:
                    cols_map["Institute/location"] = "Institute"
                if "Branch of Study Text" in edu_df.columns:
                    cols_map["Branch of Study Text"] = "Branch Study"
                elif "Branch Study" in edu_df.columns:
                    cols_map["Branch Study"] = "Branch Study"

                sub_edu = edu_df[["_pno_norm"] + list(cols_map.keys())].rename(columns=cols_map)
                pqah = pqah.merge(sub_edu.drop_duplicates(subset=["_pno_norm"]), on="_pno_norm", how="left")
                logger.info(f"[Assembler] Merged Education columns: {list(cols_map.values())}")

        # 6. Join General Expense Cost Center & Desc
        if OUT_COST_CENTER.exists():
            cc_df = load_excel(OUT_COST_CENTER)
            cc_pno = find_column_ci(cc_df, "Personnel Number") or find_column_ci(cc_df, "Personnel No.")
            if cc_pno:
                cc_df["_pno_norm"] = normalize_id(cc_df[cc_pno])
                cc_col = find_column_ci(cc_df, "Cost Center")
                cc_desc_col = find_column_ci(cc_df, "Cost Center Description")
                cols_map = {}
                if cc_col:
                    cols_map[cc_col] = "General Expense Cost Center"
                if cc_desc_col:
                    cols_map[cc_desc_col] = "General Expense Cost Center Desc"

                sub_cc = cc_df[["_pno_norm"] + list(cols_map.keys())].rename(columns=cols_map)
                pqah = pqah.merge(sub_cc.drop_duplicates(subset=["_pno_norm"]), on="_pno_norm", how="left")
                logger.info(f"[Assembler] Merged Cost Center columns: {list(cols_map.values())}")

        # 7. Join Direct Supervisor (NIK & Name)
        spv_path = _find_shared_file(["IKP_Direct_Spv.xlsx", "IKP_Direct Spv.xlsx"])
        if spv_path:
            spv_df = load_excel(spv_path)
            spv_pno = spv_df.columns[0]
            spv_df["_pno_norm"] = normalize_id(spv_df[spv_pno])
            spv_name_col = find_column_ci(spv_df, "Direct Sup") or find_column_ci(spv_df, "Superior Name") or (spv_df.columns[3] if len(spv_df.columns) > 3 else None)
            spv_nik_col  = find_column_ci(spv_df, "D.Superior") or find_column_ci(spv_df, "Superior NIK")  or (spv_df.columns[2] if len(spv_df.columns) > 2 else None)

            sub_spv = pd.DataFrame({"_pno_norm": spv_df["_pno_norm"]})
            if spv_name_col:
                sub_spv["Superior Name"] = spv_df[spv_name_col]
            if spv_nik_col:
                sub_spv["Superior NIK"] = spv_df[spv_nik_col]

            pqah = pqah.merge(sub_spv.drop_duplicates(subset=["_pno_norm"]), on="_pno_norm", how="left")
            logger.info("[Assembler] Merged Supervisor NIK and Name.")

        # 8. Join Email (PA0105)
        email_path = _find_shared_file(["IKP_PA0105.xlsx"])
        if email_path:
            email_df = load_excel(email_path)
            email_pno = get_required_column_ci(email_df, "Personnel number")
            email_df["_pno_norm"] = normalize_id(email_df[email_pno])
            email_val_col = find_column_ci(email_df, "Long ID/Number") or find_column_ci(email_df, "Email") or (email_df.columns[-1] if len(email_df.columns) > 1 else None)
            if email_val_col:
                sub_email = pd.DataFrame({
                    "_pno_norm": email_df["_pno_norm"],
                    "Email": email_df[email_val_col]
                })
                pqah = pqah.merge(sub_email.drop_duplicates(subset=["_pno_norm"]), on="_pno_norm", how="left")
                logger.info("[Assembler] Merged Email address.")

        # 9. Join Job Layer
        layer_path = _find_shared_file(["IKP_Job_Layer.xlsx", "IKP_Job Layer.xlsx"])
        if layer_path:
            layer_df = load_excel(layer_path)
            layer_key = find_column_ci(layer_df, "Job") or layer_df.columns[0]
            layer_val = find_column_ci(layer_df, "Layer") or (layer_df.columns[1] if len(layer_df.columns) > 1 else layer_df.columns[0])
            layer_df["_layer_key_norm"] = normalize_id(layer_df[layer_key])
            layer_lookup = layer_df.drop_duplicates(subset=["_layer_key_norm"]).set_index("_layer_key_norm")[layer_val]

            job_col = find_column_ci(pqah, "Job") or find_column_ci(pqah, "Position")
            if job_col:
                pqah["_job_norm"] = normalize_id(pqah[job_col])
                pqah["Layer"] = pqah["_job_norm"].map(layer_lookup)
                pqah = pqah.drop(columns=["_job_norm"], errors="ignore")
                logger.info("[Assembler] Merged Job Layer.")

        # 10. Construct Final DataFrame mapped to IKP_Headings.xlsx exactly
        final_df = pd.DataFrame(index=range(len(pqah)))

        for col in target_columns:
            matched_col = find_column_ci(pqah, col)
            if matched_col:
                final_df[col] = pqah[matched_col].values
            else:
                # Blank column (e.g. Salary Cost Center S4, or unrun modules)
                final_df[col] = ""

        validate_row_count(input_rows, len(final_df), module, logger)
        export_df(final_df, OUTPUT_FINAL, logger)

        result.update({
            "Output Rows": len(final_df),
            "Matched": len(final_df),
            "Unmatched": 0,
            "Status": "SUCCESS",
        })
        logger.info(f"[Assembler] Final Topic Report successfully generated: {OUTPUT_FINAL.name} ({len(final_df):,} rows)")

    except Exception as e:
        logger.error(f"[Assembler] FAILED: {e}")

    return result