"""
Pareto analysis — 80/20.
"""
import pandas as pd
from typing import Dict, Any, List

def pareto_analysis(df: pd.DataFrame, category_col: str, value_col: str, top_pct: float = 0.2) -> Dict[str, Any]:
    """
    Analyze if top X% of category contribute 80% of value.
    """
    try:
        df_copy = df.copy()
        df_copy[value_col] = pd.to_numeric(df_copy[value_col], errors='coerce')
        df_copy = df_copy.dropna(subset=[category_col, value_col])
        if len(df_copy)==0:
            return {"available": False, "reason": "No valid rows"}

        grouped = df_copy.groupby(category_col)[value_col].sum().sort_values(ascending=False)
        total = grouped.sum()
        cumulative = grouped.cumsum()
        cumulative_pct = cumulative / total *100

        # Find how many categories contribute 80%
        count_80 = (cumulative_pct <= 80).sum() + 1
        pct_categories_80 = count_80 / len(grouped) *100

        top_categories = grouped.head(max(1, int(len(grouped)*top_pct)))

        top_contrib_pct = top_categories.sum() / total *100 if total!=0 else 0

        insight = f"Top {count_80} categories ({pct_categories_80:.1f}%) contribute 80% of {value_col}. Top {top_pct*100:.0f}% categories contribute {top_contrib_pct:.1f}% of {value_col}."

        return {
            "available": True,
            "grouped": grouped,
            "cumulative_pct": cumulative_pct,
            "count_80": int(count_80),
            "pct_categories_80": float(pct_categories_80),
            "top_contrib_pct": float(top_contrib_pct),
            "insight": insight
        }
    except Exception as e:
        return {"available": False, "reason": f"Pareto failed: {e}"}
