"""
KPI calculator — safe calculations with fuzzy column matching.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from ..utils.helpers import fuzzy_column_match
from ..validation.schema import KPIResult

def calculate_kpi(
    df: pd.DataFrame,
    kpi_config: Dict[str, Any]
) -> KPIResult:
    """
    kpi_config: {"name": ..., "aliases": [[...], [...]], "formula": ..., "unit": ...}
    aliases is list of groups: each group is list of possible column names for one required field.
    For single-column KPIs, aliases = [["revenue","sales"]]
    For two-column KPIs, aliases = [["revenue"], ["order_id"]]
    """
    name = kpi_config["name"]
    aliases = kpi_config["aliases"]
    formula_str = kpi_config.get("formula", "")
    unit = kpi_config.get("unit", "")

    columns = list(df.columns)
    match = fuzzy_column_match(aliases, columns)

    if not match:
        return KPIResult(
            name=name,
            formula=formula_str,
            value=None,
            unit=unit,
            interpretation=f"Unavailable — requires {aliases}",
            evidence_columns=[],
            calculation_details=f"No matching columns for {aliases}",
            available=False,
            reason_if_unavailable=f"Required columns not found: {aliases}"
        )

    # Map matched columns
    matched_cols = [match[i] for i in sorted(match.keys())]
    evidence = matched_cols

    try:
        value = None
        calc_details = ""
        # Single col KPIs
        if len(matched_cols) == 1:
            col = matched_cols[0]
            s = pd.to_numeric(df[col], errors='coerce') if df[col].dtype == 'object' else df[col]
            s = s.dropna()
            if name.lower() == "total revenue" or "revenue" in name.lower() or "spend" in name.lower() or "mrr" in name.lower() or "total spend" in name.lower():
                value = float(s.sum())
                calc_details = f"SUM({col}) over {len(s)} rows"
            elif "average" in name.lower() or "aov" in name.lower() or name == "Average Order Value" or "salary" in name.lower() or "tenure" in name.lower():
                value = float(s.mean())
                calc_details = f"AVG({col})"
            elif "total orders" in name.lower() or "total customers" in name.lower() or "orders" in name.lower():
                # Count distinct if ID, else count
                value = int(df[col].nunique())
                calc_details = f"COUNT_DISTINCT({col})"
            elif "discount" in name.lower():
                raw_avg = float(s.mean())
                # If discount stored as 0-1, convert to % for display but keep raw for calc
                value = raw_avg * 100 if raw_avg < 1 else raw_avg
                calc_details = f"AVG({col})={raw_avg:.4f} ({value:.1f}%)"
            else:
                value = float(s.sum())
                calc_details = f"SUM({col})"

        elif len(matched_cols) == 2:
            col1, col2 = matched_cols[0], matched_cols[1]
            # Examples: AOV = revenue / orders, CTR = clicks/impressions, ROAS = revenue/spend, Conversion = conversions/clicks, CPA = spend/conversions, Profit Margin = profit/revenue
            s1 = pd.to_numeric(df[col1], errors='coerce').dropna() if df[col1].dtype == 'object' else df[col1].dropna()
            # For second col, need logic for distinct counts for orders
            if name == "Average Order Value":
                total_rev = float(pd.to_numeric(df[col1], errors='coerce').sum())
                total_orders = int(df[col2].nunique())
                value = total_rev / total_orders if total_orders !=0 else 0
                calc_details = f"SUM({col1})={total_rev:.2f} / COUNT_DISTINCT({col2})={total_orders}"
            elif name == "Profit Margin":
                profit_sum = float(pd.to_numeric(df[col1], errors='coerce').sum())
                rev_sum = float(pd.to_numeric(df[col2], errors='coerce').sum())
                value = (profit_sum / rev_sum *100) if rev_sum !=0 else 0
                calc_details = f"SUM({col1})={profit_sum:.2f} / SUM({col2})={rev_sum:.2f} *100"
            elif name in ["CTR", "Conversion Rate"]:
                clicks = float(pd.to_numeric(df[col1], errors='coerce').sum())
                impr = float(pd.to_numeric(df[col2], errors='coerce').sum())
                value = (clicks / impr *100) if impr !=0 else 0
                calc_details = f"SUM({col1})={clicks:.0f} / SUM({col2})={impr:.0f} *100"
            elif name == "ROAS":
                rev = float(pd.to_numeric(df[col1], errors='coerce').sum())
                spend = float(pd.to_numeric(df[col2], errors='coerce').sum())
                value = rev / spend if spend !=0 else 0
                calc_details = f"SUM({col1}) / SUM({col2}) = {rev:.2f}/{spend:.2f}"
            elif name == "CPA":
                spend = float(pd.to_numeric(df[col1], errors='coerce').sum())
                conv = float(pd.to_numeric(df[col2], errors='coerce').sum())
                value = spend / conv if conv !=0 else 0
                calc_details = f"SUM({col1}) / SUM({col2})"
            elif "goals per 90" in name.lower():
                goals = float(pd.to_numeric(df[col1], errors='coerce').sum())
                mins = float(pd.to_numeric(df[col2], errors='coerce').sum())
                value = (goals / mins * 90) if mins !=0 else 0
                calc_details = f"SUM({col1})={goals:.0f} / SUM({col2})={mins:.0f} *90 = {value:.3f}"
            else:
                # Generic ratio
                sum1 = float(pd.to_numeric(df[col1], errors='coerce').sum())
                sum2 = float(pd.to_numeric(df[col2], errors='coerce').sum())
                value = sum1 / sum2 if sum2 !=0 else 0
                calc_details = f"SUM({col1}) / SUM({col2})"

        else:
            value = None
            calc_details = "Unsupported KPI arity"

        # Special handling for Churn Rate when no churn column but status column exists
        if not value and "churn" in name.lower():
            # Try to find status column with churned values
            for col in df.columns:
                if 'status' in col.lower() or 'attrition' in col.lower():
                    try:
                        series = df[col].astype(str).str.lower()
                        churned_count = series.str.contains('churn').sum()
                        total = len(series)
                        if churned_count > 0:
                            value = churned_count / total * 100 if total > 0 else 0
                            calc_details = f"COUNT(status contains 'churn')={churned_count} / COUNT(*)={total} *100 = {value:.1f}%"
                            evidence = [col]
                            # Update name to be more accurate
                            name = "Churn Rate (from status)"
                            break
                    except:
                        continue

        # Interpretation
        interpretation = generate_interpretation(name, value, unit)

        return KPIResult(
            name=name,
            formula=formula_str,
            value=value,
            unit=unit,
            interpretation=interpretation,
            evidence_columns=evidence,
            calculation_details=calc_details,
            available=True
        )

    except Exception as e:
        return KPIResult(
            name=name,
            formula=formula_str,
            value=None,
            unit=unit,
            interpretation=f"Calculation failed: {e}",
            evidence_columns=evidence,
            calculation_details=str(e),
            available=False,
            reason_if_unavailable=str(e)
        )

def generate_interpretation(name: str, value: Any, unit: str) -> str:
    if value is None:
        return "Not calculated"
    if unit == "currency":
        return f"Total is {value:,.2f} — baseline for financial tracking. Compare MoM/YoY for growth."
    if unit == "percent":
        # Handle discount which is stored as 0-1 but should be shown as %
        display_value = value * 100 if value < 1 and "discount" in name.lower() else value
        if "discount" in name.lower():
            if display_value < 5:
                return f"Avg discount {display_value:.1f}% — low discounting, good margin protection."
            elif display_value < 20:
                return f"Avg discount {display_value:.1f}% — moderate, check impact on profit."
            else:
                return f"Avg discount {display_value:.1f}% — high discounting, may hurt margin, review pricing."
        if "margin" in name.lower():
            if display_value < 10:
                return f"Margin {display_value:.1f}% is low — generates revenue but retains little profit. Investigate costs, discounting, product mix."
            elif display_value < 25:
                return f"Margin {display_value:.1f}% is moderate — room for optimization via pricing or cost control."
            else:
                return f"Margin {display_value:.1f}% is healthy — strong cost control."
        if "ctr" in name.lower():
            return f"CTR {display_value:.2f}% measures ad relevance. Industry avg 2-3% — {'above' if display_value>2 else 'below'} average."
        if "conversion" in name.lower():
            return f"Conversion {display_value:.2f}% — percentage converting to desired action. Track by channel."
        if "attrition" in name.lower() or "churn" in name.lower():
            if display_value > 20:
                return f"Churn {display_value:.1f}% is high — retention risk, investigate drivers."
            else:
                return f"Churn {display_value:.1f}% — monitor trend, segment by tenure/department."
        return f"Rate is {display_value:.2f}% — compare across segments and time."
    if unit == "ratio":
        return f"Ratio {value:.2f} — >1 means revenue exceeds spend, <1 means loss. Higher is better for ROAS."
    if unit == "count":
        return f"Count {int(value)} — base for segmentation and growth analysis."
    if unit == "years":
        return f"Average {value:.1f} years — indicates experience/retention level."
    # Default
    if isinstance(value, (int,float)):
        return f"Value {value:.2f} — compare across categories and time to find drivers."
    return f"Value {value}"
