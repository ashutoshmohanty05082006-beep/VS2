import re
from typing import Dict, Tuple, Optional

import numpy as np
import pandas as pd


def preprocess_df(
    df: pd.DataFrame,
    drop_threshold: float = 0.9,
    fill_numeric: str = "median",
    fill_categorical: str = "mode",
    encode_categoricals: bool = True,
    parse_dates: bool = True,
) -> Tuple[pd.DataFrame, Dict]:
    """Basic swiss-army preprocessing for rapid prototyping.

    Steps performed:
    - normalize column names (lowercase, underscores)
    - drop columns with > `drop_threshold` missing fraction
    - parse date-like columns (optional)
    - fill numeric and categorical missing values
    - drop constant columns
    - optionally one-hot encode categoricals

    Returns the processed DataFrame and a small metadata dict.
    """
    df = df.copy()
    metadata: Dict[str, Optional[object]] = {}

    # Standardize column names
    def _clean(col: str) -> str:
        col = col.strip().lower()
        col = re.sub(r"\s+", "_", col)
        col = re.sub(r"[^0-9a-zA-Z_]+", "", col)
        return col

    df.columns = [_clean(c) for c in df.columns.astype(str)]

    # Drop high-missingness columns
    missing_frac = df.isna().mean()
    to_drop = missing_frac[missing_frac > drop_threshold].index.tolist()
    df.drop(columns=to_drop, inplace=True)
    metadata["dropped_high_missing"] = to_drop

    # Parse dates heuristically
    date_cols = []
    if parse_dates:
        for col in df.columns:
            if "date" in col or "time" in col:
                try:
                    parsed = pd.to_datetime(df[col], errors="coerce")
                    non_na = parsed.notna().sum()
                    if non_na >= max(1, int(len(df) * 0.01)):
                        df[col] = parsed
                        date_cols.append(col)
                except Exception:
                    continue
    metadata["parsed_dates"] = date_cols

    # Separate dtypes
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # Fill numeric
    for col in numeric_cols:
        if fill_numeric == "median":
            val = df[col].median()
        else:
            val = df[col].mean()
        df[col] = df[col].fillna(val)

    # Fill categorical
    for col in cat_cols:
        if fill_categorical == "mode":
            if df[col].mode().shape[0] > 0:
                val = df[col].mode().iloc[0]
            else:
                val = "missing"
        else:
            val = "missing"
        df[col] = df[col].fillna(val)

    # Drop constant columns
    const_cols = [c for c in df.columns if df[c].nunique(dropna=False) <= 1]
    df.drop(columns=const_cols, inplace=True)
    metadata["dropped_constant"] = const_cols

    # Optionally encode categoricals
    encoded_cols = []
    if encode_categoricals:
        df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
        encoded_cols = [c for c in df.columns if any(orig in c for orig in cat_cols)]
    metadata["encoded_cols_sample"] = encoded_cols[:20]

    return df, metadata
