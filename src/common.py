"""
common.py — Shared utilities for all HR automation modules.

Implements the 5 Common Business Rules from the specification:
  Rule 1  Normalize numeric IDs  (2102.0 -> "2102")
  Rule 2  Trim spaces            ("  NIK  " -> "NIK")
  Rule 3  Key lookup as string   (all merge keys cast to str)
  Rule 4  Row preservation       (all merges must be LEFT JOIN)
  Rule 5  Auditability           (matched / unmatched / blank counts)
"""
from pathlib import Path
from typing import List, Optional
import pandas as pd


def normalize_id(series: pd.Series) -> pd.Series:
    """
    Rule 1 + 2: Convert to string, strip whitespace, remove trailing .0
    """
    return (
        series.fillna("")
              .astype(str)
              .str.strip()
              .str.replace(r"\.0$", "", regex=True)
    )


def normalize_date_type(series: pd.Series) -> pd.Series:
    """
    Normalize SAP date type codes to zero-padded 2-character strings.
    """
    s = series.fillna("").astype(str).str.strip()
    s = s.str.replace(r"\.0$", "", regex=True)
    return s.apply(lambda x: x.zfill(2) if x != "" else "")


def strip_leading_zeros(series: pd.Series) -> pd.Series:
    """
    Strip leading zeros from string series, keeping at least one character.
    """
    return series.apply(lambda x: x.lstrip("0") or "0" if isinstance(x, str) else x)


def load_excel(path: Path) -> pd.DataFrame:
    """
    Load an Excel file, reading all columns as strings.
    Strips whitespace from all column names.
    """
    df = pd.read_excel(path, dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def find_column_ci(df: pd.DataFrame, target_name: str, aliases: Optional[List[str]] = None) -> Optional[str]:
    """
    Find exact column name in DataFrame using case-insensitive and trimmed comparison.
    Supports list of alternative alias names.
    """
    candidates = [target_name] + (aliases if aliases else [])
    cand_norm = [c.strip().lower() for c in candidates]
    
    col_map = {str(c).strip().lower(): c for c in df.columns}
    for cand in cand_norm:
        if cand in col_map:
            return col_map[cand]
    return None


def get_required_column_ci(df: pd.DataFrame, target_name: str, aliases: Optional[List[str]] = None) -> str:
    """
    Get required column name in DataFrame case-insensitively, or raise ValueError.
    """
    col = find_column_ci(df, target_name, aliases)
    if col is None:
        opts = [target_name] + (aliases if aliases else [])
        raise ValueError(f"Missing required column (case-insensitive): any of {opts}")
    return col


def audit_counts(df: pd.DataFrame, lookup_col: str) -> dict:
    """
    Rule 5: Return matched / unmatched / blank counts for a lookup result column.
    """
    total     = len(df)
    blank     = df[lookup_col].isna() | (df[lookup_col].astype(str).str.strip() == "")
    matched   = int((~blank).sum())
    unmatched = int(blank.sum())
    return {"total": total, "matched": matched, "unmatched": unmatched}
