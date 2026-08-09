"""
Individual quality checks — each returns partial report.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from collections import Counter
import re

def check_missing(df: pd.DataFrame):
    total_cells = df.size
    total_missing = int(df.isna().sum().sum())
    missing_pct = round((total_missing / total_cells * 100) if total_cells >0 else 0, 2)
    per_col = {}
    worst = []
    for col in df.columns:
        cnt = int(df[col].isna().sum())
        pct = round((cnt / len(df) * 100) if len(df)>0 else 0, 2)
        per_col[col] = {"count": cnt, "pct": pct}
        if pct > 0:
            worst.append((col, pct))
    worst_sorted = [col for col,_ in sorted(worst, key=lambda x: x[1], reverse=True)[:5]]
    return total_missing, total_cells, missing_pct, per_col, worst_sorted

def check_duplicates(df: pd.DataFrame):
    dupe_rows = int(df.duplicated().sum())
    dupe_pct = round(dupe_rows / len(df) * 100 if len(df)>0 else 0, 2)
    # ID cols duplicate check
    dupe_id_cols = {}
    for col in df.columns:
        if df[col].nunique() < len(df):
            # Check if column looks like ID but has dupes
            if 'id' in col.lower() or 'key' in col.lower():
                dupes = len(df) - df[col].nunique()
                if dupes > 0:
                    dupe_id_cols[col] = dupes
    sample_dupes = None
    if dupe_rows >0:
        try:
            sample_dupes = df[df.duplicated(keep=False)].head(10)
        except:
            sample_dupes = None
    return dupe_rows, dupe_pct, dupe_id_cols, sample_dupes

def check_outliers(df: pd.DataFrame, numeric_cols: List[str], method: str = "IQR"):
    """
    IQR and Z-score based.
    Returns per column outlier info.
    """
    per_col = {}
    total_outlier_rows = set()
    for col in numeric_cols:
        try:
            s = pd.to_numeric(df[col], errors='coerce').dropna()
            if len(s) < 10:
                continue
            if method == "IQR":
                q1 = s.quantile(0.25)
                q3 = s.quantile(0.75)
                iqr = q3 - q1
                lower = q1 - 1.5*iqr
                upper = q3 + 1.5*iqr
                outliers = s[(s < lower) | (s > upper)]
            else: # Z-score
                mean = s.mean()
                std = s.std()
                if std == 0:
                    continue
                z = (s - mean)/std
                outliers = s[z.abs() > 3]
                lower = mean - 3*std
                upper = mean + 3*std

            count = len(outliers)
            if count >0:
                pct = round(count / len(df) * 100, 2)
                per_col[col] = {"count": count, "pct": pct, "lower": float(lower), "upper": float(upper), "method": method}
                # track rows
                outlier_idx = outliers.index
                total_outlier_rows.update(outlier_idx.tolist())
        except Exception as e:
            continue
    return per_col, len(total_outlier_rows)

def check_consistency(df: pd.DataFrame, categorical_cols: List[str]):
    blank_counts = {}
    whitespace_counts = {}
    inconsistent_examples = {}
    constant_cols = []
    high_card_cols = []

    for col in df.columns:
        try:
            s = df[col]
            # Constant
            if s.nunique(dropna=True) == 1:
                constant_cols.append(col)
            # High cardinality for categorical
            if col in categorical_cols:
                uniq_ratio = s.nunique()/len(df) if len(df)>0 else 0
                if uniq_ratio > 0.8:
                    high_card_cols.append(col)

            # For object cols, check blank strings and whitespace
            if s.dtype == 'object':
                # Blank strings
                blank = s.astype(str).str.strip().eq('').sum() if len(s)>0 else 0
                # But exclude NaN already counted
                # Count where original is empty string
                blank_exact = (s == '').sum() if s.dtype == 'object' else 0
                if blank_exact >0:
                    blank_counts[col] = int(blank_exact)

                # Whitespace leading/trailing
                has_ws = s.astype(str).apply(lambda x: x != x.strip() if isinstance(x, str) else False).sum()
                if has_ws >0:
                    whitespace_counts[col] = int(has_ws)

                # Inconsistent casing e.g., US vs us vs Usa
                if col in categorical_cols or col in df.select_dtypes(include='object').columns:
                    # Get value counts, look for case-insensitive duplicates
                    vals = s.dropna().astype(str).unique()
                    lower_map = {}
                    for v in vals:
                        low = v.lower().strip()
                        lower_map.setdefault(low, []).append(v)
                    inconsist = {low: variants for low, variants in lower_map.items() if len(variants) >1}
                    if inconsist:
                        inconsistent_examples[col] = {"examples": list(inconsist.items())[:3], "total_groups": len(inconsist)}
        except:
            continue

    return blank_counts, whitespace_counts, inconsistent_examples, constant_cols, high_card_cols

def check_validity(df: pd.DataFrame, numeric_cols: List[str]):
    """
    Check for suspicious negatives, impossible values.
    """
    issues = []
    for col in numeric_cols:
        try:
            s = pd.to_numeric(df[col], errors='coerce')
            # Negative where name suggests shouldn't be negative
            hints_non_negative = ['age', 'price', 'revenue', 'quantity', 'count', 'salary', 'tenure', 'click', 'impression', 'spend']
            col_lower = col.lower()
            if any(h in col_lower for h in hints_non_negative):
                neg_count = (s < 0).sum()
                if neg_count >0:
                    issues.append((col, f"{neg_count} negative values in {col} (expected >=0)", int(neg_count)))
            # Age impossible
            if 'age' in col_lower:
                impossible = ((s <0) | (s>120)).sum()
                if impossible >0:
                    issues.append((col, f"{impossible} impossible age values (<0 or >120)", int(impossible)))
            # Percentage >100
            if any(k in col_lower for k in ['pct', 'percent', 'ctr', 'rate', 'margin']):
                # Allow >100 sometimes but flag
                high = (s >100).sum() if 'margin' not in col_lower else (s>1000).sum()  # margin could be <100 but high values flag
                if high>0 and 'margin' not in col_lower:
                    # Only flag if column seems like 0-100
                    if s.max() <=100 or s.min()>=0:
                        pass  # normal
        except:
            continue
    return issues
