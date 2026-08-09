"""
Cleaning engine — orchestrates transformations and maintains log.
"""
import pandas as pd
from typing import List, Dict, Any, Optional
from ..validation.schema import CleaningResult
from .transformations import (
    remove_duplicates, fill_missing_mean, fill_missing_median, fill_missing_mode,
    drop_column, trim_whitespace, standardize_case, cap_outliers_iqr,
    remove_outliers_iqr, parse_dates
)
from ..utils.constants import CleaningOp
from ..validation.schema import TransformationRecord

def apply_cleaning_operations(
    df: pd.DataFrame,
    operations: List[Dict[str, Any]]
) -> CleaningResult:
    """
    operations: list of dicts like {"op": CleaningOp.REMOVE_DUPLICATES, "column": "age", "case": "lower"}
    Returns CleaningResult with log.
    """
    df_current = df.copy()
    log: List[TransformationRecord] = []
    rows_before = len(df)
    step = 1

    for op_dict in operations:
        op = op_dict.get("op")
        col = op_dict.get("column", "all")
        before_val = None
        after_val = None
        rows_affected = 0
        details = None

        try:
            if op == CleaningOp.REMOVE_DUPLICATES:
                df_current, rows_affected = remove_duplicates(df_current)
                before_val = f"{rows_before} rows"
                after_val = f"{len(df_current)} rows"
                details = "Removed duplicate rows"

            elif op == CleaningOp.FILL_NUM_MEAN:
                if col not in df_current.columns:
                    continue
                before_missing = int(df_current[col].isna().sum())
                df_current, rows_affected = fill_missing_mean(df_current, col)
                before_val = f"{before_missing} missing"
                after_val = f"filled with mean"

            elif op == CleaningOp.FILL_NUM_MEDIAN:
                if col not in df_current.columns:
                    continue
                before_missing = int(df_current[col].isna().sum())
                df_current, rows_affected = fill_missing_median(df_current, col)
                before_val = f"{before_missing} missing"
                after_val = f"filled with median"

            elif op == CleaningOp.FILL_CAT_MODE:
                if col not in df_current.columns:
                    continue
                before_missing = int(df_current[col].isna().sum())
                df_current, rows_affected = fill_missing_mode(df_current, col)
                before_val = f"{before_missing} missing"
                after_val = f"filled with mode"

            elif op == CleaningOp.DROP_COL:
                if col not in df_current.columns:
                    continue
                df_current, rows_affected = drop_column(df_current, col)
                before_val = f"Constant column {col} with 1 unique value"
                after_val = f"Removed — contains only one unique value, adds no analytical value"

            elif op == CleaningOp.TRIM_WHITESPACE:
                if col not in df_current.columns:
                    continue
                df_current, rows_affected = trim_whitespace(df_current, col)
                before_val = "with whitespace"
                after_val = "trimmed"

            elif op == CleaningOp.STANDARDIZE_CASE:
                if col not in df_current.columns:
                    continue
                case = op_dict.get("case", "lower")
                df_current, rows_affected = standardize_case(df_current, col, case)
                before_val = "mixed case"
                after_val = f"standardized to {case}"

            elif op == CleaningOp.CAP_OUTLIERS:
                if col not in df_current.columns:
                    continue
                df_current, rows_affected = cap_outliers_iqr(df_current, col)
                before_val = "with outliers"
                after_val = "capped via IQR"

            elif op == CleaningOp.REMOVE_OUTLIERS:
                if col not in df_current.columns:
                    continue
                df_current, rows_affected = remove_outliers_iqr(df_current, col)
                before_val = f"{rows_before} rows"
                after_val = f"{len(df_current)} rows after outlier removal"

            elif op == CleaningOp.PARSE_DATES:
                if col not in df_current.columns:
                    continue
                df_current, rows_affected = parse_dates(df_current, col)
                before_val = "string dates"
                after_val = "parsed datetime"

            elif op == CleaningOp.DROP_ROWS_MISSING:
                if col == "all":
                    before = len(df_current)
                    df_current = df_current.dropna()
                    rows_affected = before - len(df_current)
                else:
                    if col not in df_current.columns:
                        continue
                    before = len(df_current)
                    df_current = df_current.dropna(subset=[col])
                    rows_affected = before - len(df_current)
                before_val = f"{rows_before} rows"
                after_val = f"{len(df_current)} rows"

            else:
                continue

            # Only log if affected >0
            if rows_affected > 0 or op in [CleaningOp.DROP_COL]:
                record = TransformationRecord(
                    step=step,
                    column=col,
                    action=op,
                    before=before_val,
                    after=after_val,
                    rows_affected=rows_affected,
                    details=details
                )
                log.append(record)
                step += 1

        except Exception as e:
            # Log error but continue
            record = TransformationRecord(
                step=step,
                column=col,
                action=f"{op}_FAILED",
                before=str(e),
                after=None,
                rows_affected=0,
                details=f"Error: {e}"
            )
            log.append(record)
            step += 1
            continue

    return CleaningResult(
        df_cleaned=df_current,
        log=log,
        rows_before=rows_before,
        rows_after=len(df_current)
    )

def suggest_cleaning_operations(df: pd.DataFrame, quality_report) -> List[Dict[str, Any]]:
    """
    Auto-suggest cleaning ops based on quality report.
    Returns list of operation dicts.
    """
    ops = []
    # Duplicates
    if quality_report.duplicates.duplicate_row_count > 0:
        ops.append({"op": CleaningOp.REMOVE_DUPLICATES, "column": "all", "reason": f"{quality_report.duplicates.duplicate_row_count} duplicate rows"})

    # Whitespace
    for col, cnt in quality_report.consistency.whitespace_counts.items():
        ops.append({"op": CleaningOp.TRIM_WHITESPACE, "column": col, "reason": f"{cnt} whitespace issues"})

    # Inconsistent labels -> suggest lower case standardization
    for col in quality_report.consistency.inconsistent_labels.keys():
        ops.append({"op": CleaningOp.STANDARDIZE_CASE, "column": col, "case": "lower", "reason": "Inconsistent casing"})

    # Missing — suggest median for numeric, mode for categorical
    for col, info in quality_report.missing.per_column.items():
        if info["pct"] > 0 and info["pct"] < 30:  # only suggest if <30%
            # Determine if numeric
            try:
                # heuristic: if column can be numeric
                sample = df[col].dropna().head(10)
                is_num = pd.to_numeric(sample, errors='coerce').notna().sum() > 0
                if is_num:
                    ops.append({"op": CleaningOp.FILL_NUM_MEDIAN, "column": col, "reason": f"{info['pct']}% missing"})
                else:
                    ops.append({"op": CleaningOp.FILL_CAT_MODE, "column": col, "reason": f"{info['pct']}% missing"})
            except:
                pass

    # Constant columns -> suggest drop
    for col in quality_report.consistency.constant_columns:
        ops.append({"op": CleaningOp.DROP_COL, "column": col, "reason": "Constant column"})

    return ops
