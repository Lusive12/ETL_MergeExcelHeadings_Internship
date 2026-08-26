"""
excel_export.py â€” Shared Excel writer with safe overwrite.

Handles the common PermissionError that occurs when Excel has the
output file open. Gives the user a clear actionable error message.
"""
import logging
import pandas as pd
from pathlib import Path


def export_df(
    df: pd.DataFrame,
    path: Path,
    logger: logging.Logger = None
) -> None:
    """
    Write DataFrame to Excel.
    - Auto-creates parent directories.
    - Deletes any existing file before writing to avoid lock errors.
    """
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        try:
            output_path.unlink()
        except PermissionError:
            msg = (
                f"Cannot overwrite '{output_path.name}' â€” "
                f"the file is open in Excel. Close it and run again."
            )
            if logger:
                logger.error(f"[Export] {msg}")
            raise PermissionError(msg)

    df.to_excel(output_path, index=False)

    if logger:
        logger.info(f"[Export] Saved: {output_path.name} ({len(df):,} rows)")
