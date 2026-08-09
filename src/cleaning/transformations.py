"""
Pure transformation functions — each returns new DF and affected count.
No side effects, testable.
"""
import pandas as pd
import numpy as np
from typing import Tuple

def remove_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    before = len(df)
    df_clean = df.drop_duplicates()
    affected = before - len(df_clean)
    return df_clean, affected

def fill_missing_mean(df: pd.DataFrame, column: str) -> Tuple[pd.DataFrame, int]:
    s = df[column]
    missing = s.isna().sum()
    if missing == 0:
        return df, 0
    mean_val = pd.to_numeric(s, errors='coerce').mean()
    df_new = df.copy()
    df_new[column] = df_new[column].fillna(mean_val)
    return df_new, int(missing)

def fill_missing_median(df: pd.DataFrame, column: str) -> Tuple[pd.DataFrame, int]:
    s = df[column]
    missing = s.isna().sum()
    if missing == 0:
        return df, 0
    median_val = pd.to_numeric(s, errors='coerce').median()
    df_new = df.copy()
    df_new[column] = df_new[column].fillna(median_val)
    return df_new, int(missing)

def fill_missing_mode(df: pd.DataFrame, column: str) -> Tuple[pd.DataFrame, int]:
    s = df[column]
    missing = s.isna().sum()
    if missing == 0:
        return df, 0
    mode_val = s.mode().iloc[0] if not s.mode().empty else None
    if mode_val is None:
        return df, 0
    df_new = df.copy()
    df_new[column] = df_new[column].fillna(mode_val)
    return df_new, int(missing)

def drop_column(df: pd.DataFrame, column: str) -> Tuple[pd.DataFrame, int]:
    if column not in df.columns:
        return df, 0
    df_new = df.drop(columns=[column])
    return df_new, 1

def trim_whitespace(df: pd.DataFrame, column: str) -> Tuple[pd.DataFrame, int]:
    if column not in df.columns:
        return df, 0
    s = df[column]
    if s.dtype != 'object':
        return df, 0
    # Count affected
    affected = s.astype(str).apply(lambda x: x != x.strip() if isinstance(x, str) else False).sum()
    df_new = df.copy()
    df_new[column] = df_new[column].astype(str).apply(lambda x: x.strip() if isinstance(x, str) else x)
    # Revert 'nan' strings back to NaN if original was NaN? Keep simple
    df_new[column] = df_new[column].replace('nan', np.nan)
    return df_new, int(affected)

def standardize_case(df: pd.DataFrame, column: str, case: str = "lower") -> Tuple[pd.DataFrame, int]:
    if column not in df.columns:
        return df, 0
    df_new = df.copy()
    # Count distinct before/after
    before_unique = df_new[column].nunique()
    if case == "lower":
        df_new[column] = df_new[column].astype(str).str.lower()
    elif case == "upper":
        df_new[column] = df_new[column].astype(str).str.upper()
    elif case == "title":
        df_new[column] = df_new[column].astype(str).str.title()
    after_unique = df_new[column].nunique()
    affected = max(0, before_unique - after_unique)  # reduction indicates standardization
    # If no reduction, count as affected if any value changed case
    if affected == 0:
        # crude
        affected = (df[column].astype(str) != df_new[column].astype(str)).sum()
    return df_new, int(affected)

def cap_outliers_iqr(df: pd.DataFrame, column: str) -> Tuple[pd.DataFrame, int]:
    if column not in df.columns:
        return df, 0
    try:
        s = pd.to_numeric(df[column], errors='coerce')
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5*iqr
        upper = q3 + 1.5*iqr
        df_new = df.copy()
        # Cap
        df_new[column] = np.where(s < lower, lower, np.where(s > upper, upper, s))
        affected = ((s < lower) | (s > upper)).sum()
        return df_new, int(affected)
    except:
        return df, 0

def remove_outliers_iqr(df: pd.DataFrame, column: str) -> Tuple[pd.DataFrame, int]:
    if column not in df.columns:
        return df, 0
    try:
        s = pd.to_numeric(df[column], errors='coerce')
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5*iqr
        upper = q3 + 1.5*iqr
        mask = (s >= lower) & (s <= upper) | s.isna()  # keep NaNs
        df_new = df[mask].copy()
        affected = len(df) - len(df_new)
        return df_new, int(affected)
    except:
        return df, 0

def parse_dates(df: pd.DataFrame, column: str) -> Tuple[pd.DataFrame, int]:
    if column not in df.columns:
        return df, 0
    try:
        s = df[column]
        parsed = pd.to_datetime(s, errors='coerce', dayfirst=True)
        success = parsed.notna().sum()
        if success == 0:
            return df, 0
        df_new = df.copy()
        df_new[column] = parsed
        affected = int(success)
        return df_new, affected
    except:
        return df, 0
