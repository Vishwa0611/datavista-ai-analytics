"""
Segmentation engine.
"""
import pandas as pd
from typing import List
from ..validation.schema import ModuleResult
from .rfm import find_rfm_columns, calculate_rfm
from .pareto import pareto_analysis

def run_segmentation(
    df: pd.DataFrame,
    numeric_cols: List[str],
    categorical_cols: List[str],
    datetime_cols: List[str]
) -> ModuleResult:
    try:
        results = {}

        # Try RFM
        rfm_col_map = find_rfm_columns(list(df.columns))
        # Need customer, at least date + monetary
        if rfm_col_map["customer"] and datetime_cols and rfm_col_map["monetary"]:
            date_col = datetime_cols[0]
            rfm_res = calculate_rfm(df, rfm_col_map["customer"], date_col, rfm_col_map["monetary"])
            results["rfm"] = rfm_res
        else:
            results["rfm"] = {"available": False, "reason": f"RFM requires customer_id, date, monetary — found {rfm_col_map}. Missing columns."}

        # Pareto — try categorical + numeric combinations
        pareto_results = {}
        for cat_col in categorical_cols[:3]:  # limit
            for num_col in numeric_cols[:2]:
                if cat_col not in df.columns or num_col not in df.columns:
                    continue
                if df[cat_col].nunique() <2 or df[cat_col].nunique()>100:
                    continue
                key = f"{cat_col}_vs_{num_col}"
                pareto_results[key] = pareto_analysis(df, cat_col, num_col)
        results["pareto"] = pareto_results

        # Regional/Product performance ranking — generic
        performance = {}
        for cat_col in categorical_cols[:3]:
            for num_col in numeric_cols[:2]:
                if cat_col not in df.columns or num_col not in df.columns:
                    continue
                try:
                    grouped = df.groupby(cat_col)[num_col].agg(['sum','mean','count']).sort_values('sum', ascending=False).head(10)
                    performance[f"{cat_col}_by_{num_col}"] = grouped
                except:
                    continue
        results["performance_ranking"] = performance

        available = any(v.get("available", False) for v in [results.get("rfm", {})]) or len(performance)>0

        return ModuleResult(available=available, data=results, reason=None if available else "Segmentation requires categorical + numeric columns or customer/date/monetary for RFM")

    except Exception as e:
        return ModuleResult(available=False, reason=f"Segmentation failed: {e}")
