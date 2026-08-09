"""
Column classifier — detects numerical, categorical, datetime, ID, PII, constant, etc.
"""
import pandas as pd
import numpy as np
from typing import List, Dict
from ..validation.schema import ColumnProfile
from ..utils.constants import ColumnType
from ..utils.helpers import is_potential_id
from ..utils.pii import detect_pii_columns
from ..utils.logger import logger

def try_parse_datetime(series: pd.Series, sample_size: int = 100) -> bool:
    """Heuristic: try converting sample to datetime, if >80% success -> datetime
    Guard: don't treat pure numeric as datetime."""
    # If dtype is numeric, don't treat as datetime unless it looks like timestamp
    if pd.api.types.is_numeric_dtype(series):
        # Only consider datetime if values are large timestamp-like? Skip for MVP
        # For safety, return False for numeric to avoid misclassifying quantity, price etc.
        return False
    # If dtype is bool, not datetime
    if pd.api.types.is_bool_dtype(series):
        return False

    sample = series.dropna().head(sample_size)
    if len(sample) == 0:
        return False
    # If sample is mostly numeric, skip
    try:
        numeric_attempt = pd.to_numeric(sample, errors='coerce')
        if numeric_attempt.notna().sum() / len(sample) > 0.8:
            return False
    except:
        pass

    try:
        # Try with dayfirst=True for DD-MM-YYYY (common in India, Superstore)
        parsed = pd.to_datetime(sample, errors='coerce', dayfirst=True)
        success_ratio = parsed.notna().sum() / len(sample)
        if success_ratio > 0.8:
            return True
        # Fallback without dayfirst
        parsed2 = pd.to_datetime(sample, errors='coerce')
        success_ratio2 = parsed2.notna().sum() / len(sample)
        return success_ratio2 > 0.8
    except:
        return False

def classify_columns(df: pd.DataFrame) -> List[ColumnProfile]:
    profiles = []
    # Pre-detect PII for all cols — pass dtypes to avoid flagging numeric metrics
    sample_dict = {col: df[col].dropna().astype(str).head(20).tolist() for col in df.columns}
    dtype_dict = {col: str(df[col].dtype) for col in df.columns}
    pii_map = detect_pii_columns(list(df.columns), sample_dict, dtype_dict)

    for col in df.columns:
        s = df[col]
        original_dtype = str(s.dtype)
        missing_count = int(s.isna().sum())
        missing_pct = round((missing_count / len(df) * 100) if len(df) > 0 else 0, 2)
        unique_count = int(s.nunique(dropna=True))
        unique_ratio = round(unique_count / len(df) if len(df) > 0 else 0, 4)
        sample_vals = s.dropna().head(5).tolist()

        is_constant = unique_count == 1
        is_high_card = unique_ratio > 0.8 and original_dtype == 'object' and not is_constant

        # ID detection
        is_id = is_potential_id(s) if unique_ratio > 0.9 else False

        # PII
        is_pii = col in pii_map
        pii_types = pii_map.get(col, [])

        # Type inference — Fixed order: datetime before ID to avoid Date being misclassified as ID
        inferred_type = ColumnType.UNKNOWN.value

        # Special handling: Postal code, zip, pin should be categorical not numeric metric
        col_lower = str(col).lower()
        non_metric_hints = ['postal', 'zip', 'pin code', 'pincode']
        is_non_metric = any(hint in col_lower for hint in non_metric_hints)

        if is_constant:
            inferred_type = ColumnType.CONSTANT.value
        elif try_parse_datetime(s):
            inferred_type = ColumnType.DATETIME.value
        elif is_id:
            inferred_type = ColumnType.ID.value
        elif is_pii:
            inferred_type = ColumnType.PII.value
        elif is_non_metric:
            inferred_type = ColumnType.CATEGORICAL.value
        else:
            if pd.api.types.is_bool_dtype(s) or (set(s.dropna().unique()) <= {0,1,True,False} and len(s.dropna().unique()) <=2):
                inferred_type = ColumnType.BOOLEAN.value
            elif pd.api.types.is_numeric_dtype(s):
                # Check if actually categorical numeric (few uniques)
                if unique_count <= 10 and unique_count < len(df)*0.1:
                    # Could be categorical but keep numerical if large range
                    inferred_type = ColumnType.NUMERICAL.value
                else:
                    inferred_type = ColumnType.NUMERICAL.value
            elif pd.api.types.is_datetime64_any_dtype(s):
                inferred_type = ColumnType.DATETIME.value
            else:
                # Object/text
                if unique_count / len(df) > 0.9:
                    # Likely free text or high-cardinality ID-like (e.g., Product with 10 unique out of 10)
                    # For small datasets (<20 rows), treat high-cardinality text as categorical, not ID, if no ID hint
                    # This fixes 10-row sales data where Product was misclassified as ID
                    if unique_count < 20 and not is_id:
                        inferred_type = ColumnType.CATEGORICAL.value
                    else:
                        inferred_type = ColumnType.TEXT.value
                else:
                    inferred_type = ColumnType.CATEGORICAL.value

        # Basic stats for numeric
        mean_val = median_val = min_val = max_val = None
        if inferred_type == ColumnType.NUMERICAL.value:
            try:
                numeric_s = pd.to_numeric(s, errors='coerce')
                mean_val = float(numeric_s.mean()) if numeric_s.notna().any() else None
                median_val = float(numeric_s.median()) if numeric_s.notna().any() else None
                min_val = float(numeric_s.min()) if numeric_s.notna().any() else None
                max_val = float(numeric_s.max()) if numeric_s.notna().any() else None
            except:
                pass

        profile = ColumnProfile(
            name=col,
            inferred_type=inferred_type,
            original_dtype=original_dtype,
            unique_count=unique_count,
            unique_ratio=unique_ratio,
            missing_count=missing_count,
            missing_pct=missing_pct,
            sample_values=sample_vals,
            is_constant=is_constant,
            is_high_cardinality=is_high_card,
            is_id=is_id,
            is_potential_pii=is_pii,
            pii_types=pii_types,
            mean=mean_val,
            median=median_val,
            min_val=min_val,
            max_val=max_val
        )
        profiles.append(profile)

    return profiles
