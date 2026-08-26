"""
validator.py — 5-Level Validation Layer

Level 1  Mandatory columns     -> raise ValueError  (stop module)
Level 2  File existence        -> raise FileNotFoundError (stop module)
Level 3  Lookup match report   -> log WARNING (continue)
Level 4  Row count integrity   -> raise ValueError  (stop module)
Level 5  Date validity         -> log WARNING (continue)
"""
import logging
from pathlib import Path
from typing import List
import pandas as pd
from src.common import find_column_ci


def validate_file_exists(path: Path, logger: logging.Logger) -> None:
    """Level 2: Raise FileNotFoundError if the input file is missing."""
    if not path.exists():
        msg = f"[Validator] Missing required file: {path}"
        logger.error(msg)
        raise FileNotFoundError(msg)
    logger.info(f"[Validator] File found: {path.name}")


def validate_columns(
    df: pd.DataFrame,
    required: List[str],
    source_name: str,
    logger: logging.Logger
) -> None:
    """
    Level 1: Case-insensitive column validation without aliases.
    Raises ValueError listing missing columns.
    """
    missing = []
    for req in required:
        found = find_column_ci(df, req)
        if not found:
            missing.append(req)

    if missing:
        msg = f"[Validator] {source_name} is missing required columns (case-insensitive): {missing}"
        logger.error(msg)
        raise ValueError(msg)
    logger.info(f"[Validator] {source_name}: all required columns present.")


def validate_row_count(
    before: int, after: int,
    module: str, logger: logging.Logger
) -> None:
    """Level 4: Raise ValueError if any rows were lost during processing."""
    if before != after:
        msg = (
            f"[Validator] [{module}] Row count mismatch! "
            f"Input={before}, Output={after}. Rows were lost."
        )
        logger.error(msg)
        raise ValueError(msg)
    logger.info(f"[Validator] [{module}] Row count OK: {after} rows preserved.")


def validate_dates(
    series: pd.Series, col_name: str,
    logger: logging.Logger
) -> None:
    """Level 5: Log a warning for invalid or blank dates."""
    invalid = series.isna()
    count   = int(invalid.sum())
    if count > 0:
        logger.warning(
            f"[Validator] '{col_name}': {count} invalid/blank date(s) detected. "
            f"Affected rows will have blank values in output."
        )
