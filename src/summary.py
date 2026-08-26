"""
summary.py â€” Generates the 00_processing_summary.xlsx report.

Collects one result dict per module and writes a consolidated
audit table showing matched/unmatched counts and status per module.
"""
import logging
import pandas as pd
from pathlib import Path

from src.excel_export import export_df

OUTPUT_PATH = Path("output/00_processing_summary.xlsx")

COLUMNS = [
    "Module", "Input Rows", "Output Rows",
    "Matched", "Unmatched", "Status", "Output File"
]


def write_summary(results: list, logger: logging.Logger) -> None:
    """Write all module results to the processing summary Excel file."""
    if not results:
        logger.warning("[Summary] No module results to summarize.")
        return

    df = pd.DataFrame(results, columns=COLUMNS)
    export_df(df, OUTPUT_PATH, logger)
    logger.info(f"[Summary] Summary written: {OUTPUT_PATH}")
