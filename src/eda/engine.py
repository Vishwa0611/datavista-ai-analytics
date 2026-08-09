"""
EDA orchestrator — combines numerical, categorical, temporal.
"""
import pandas as pd
from typing import Dict, Any, List
from .numerical import analyze_numerical
from .categorical import analyze_categorical
from .temporal import analyze_temporal
from ..validation.schema import ModuleResult

def run_eda(
    df: pd.DataFrame,
    numeric_cols: List[str],
    categorical_cols: List[str],
    datetime_cols: List[str]
) -> ModuleResult:
    try:
        numerical = analyze_numerical(df, numeric_cols)
        categorical = analyze_categorical(df, categorical_cols)
        temporal = analyze_temporal(df, datetime_cols, numeric_cols)

        # Decide which charts to generate (smart selection)
        chart_plan = []
        # Numerical -> histogram + box if < 10 numeric cols
        for col in numeric_cols[:10]:  # limit
            chart_plan.append({"type": "histogram", "column": col, "reason": "Distribution shape"})
            chart_plan.append({"type": "box", "column": col, "reason": "Outlier detection"})

        # Categorical -> bar, limit to 10
        for col in categorical_cols[:10]:
            # Skip high cardinality already
            if df[col].nunique() < 50:
                chart_plan.append({"type": "bar", "column": col, "reason": "Frequency distribution"})

        # Temporal -> line
        for col in datetime_cols[:2]:
            if numeric_cols:
                chart_plan.append({"type": "line", "column": date_col, "metric": numeric_cols[0], "reason": "Trend over time"} for date_col in [col])

        # Correlation heatmap if >1 numeric
        if len(numeric_cols) > 1:
            chart_plan.append({"type": "heatmap", "columns": numeric_cols, "reason": "Correlation matrix"})

        # Actually chart_plan for temporal fix
        chart_plan_cleaned = []
        for item in chart_plan:
            if isinstance(item, dict):
                chart_plan_cleaned.append(item)
            else:
                # generator case fix
                for sub in item:
                    chart_plan_cleaned.append(sub)

        # Temporal charts
        for date_col in datetime_cols[:2]:
            if numeric_cols:
                chart_plan_cleaned.append({"type": "line", "date_col": date_col, "metric": numeric_cols[0], "reason": "Monthly trend"})

        data = {
            "numerical": numerical,
            "categorical": categorical,
            "temporal": temporal,
            "chart_plan": chart_plan_cleaned,
            "summary": {
                "numeric_count": len(numerical),
                "categorical_count": len(categorical),
                "temporal_available": temporal.get("available", False),
                "total_charts_planned": len(chart_plan_cleaned)
            }
        }

        return ModuleResult(available=True, reason=None, data=data)

    except Exception as e:
        return ModuleResult(available=False, reason=f"EDA failed: {e}", data=None)
