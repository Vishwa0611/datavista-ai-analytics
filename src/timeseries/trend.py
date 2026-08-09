"""
Time series trend analysis.
"""
import pandas as pd
import numpy as np

def get_best_metric(numeric_cols):
    """Prefer meaningful business metrics over postal codes"""
    if not numeric_cols:
        return None
    # Preferred keywords in order
    preferred = ['sales', 'revenue', 'profit', 'quantity', 'amount', 'price', 'discount', 'mrr', 'gmv']
    # Avoid these
    avoid = ['postal', 'zip', 'pin', 'code', 'id', 'latitude', 'longitude']
    
    # Score each col
    scored = []
    for col in numeric_cols:
        col_low = col.lower()
        # Skip avoid list
        if any(a in col_low for a in avoid):
            continue
        score = 0
        for i, pref in enumerate(preferred):
            if pref in col_low:
                score = 100 - i*10  # higher score for earlier preferred
                break
        scored.append((score, col))
    
    if scored:
        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
    
    # Fallback: first col that is not in avoid list
    for col in numeric_cols:
        if not any(a in col.lower() for a in avoid):
            return col
    
    # Last resort: first col
    return numeric_cols[0] if numeric_cols else None


from typing import List, Dict, Any

def analyze_trends(df: pd.DataFrame, datetime_cols: List[str], numeric_cols: List[str]) -> Dict[str, Any]:
    if not datetime_cols or not numeric_cols:
        return {"available": False, "reason": "Need datetime + numeric columns"}

    results = {}
    for date_col in datetime_cols[:2]:
        # Use best meaningful metric instead of first 2 numeric
        best_metric = get_best_metric(numeric_cols)
        metrics_to_use = [best_metric] if best_metric else numeric_cols[:2]
        for metric in metrics_to_use:
            try:
                df_copy = df.copy()
                df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce', dayfirst=True)
                df_copy[metric] = pd.to_numeric(df_copy[metric], errors='coerce')
                df_copy = df_copy.dropna(subset=[date_col, metric]).sort_values(date_col)
                if len(df_copy) < 10:
                    continue

                # Monthly resample for trend
                df_copy.set_index(date_col, inplace=True)
                monthly = df_copy[metric].resample('ME').sum()

                # MoM and YoY
                mom = monthly.pct_change().iloc[-1] *100 if len(monthly)>=2 else None
                yoy = None
                if len(monthly)>=13:
                    yoy = (monthly.iloc[-1] - monthly.iloc[-13]) / monthly.iloc[-13] *100 if monthly.iloc[-13]!=0 else None

                # Rolling avg
                rolling_3 = monthly.rolling(3).mean()
                rolling_6 = monthly.rolling(6).mean()

                # Peak/low
                peak = monthly.idxmax()
                low = monthly.idxmin()

                # Trend via polyfit
                x = np.arange(len(monthly))
                y = monthly.values
                slope = np.polyfit(x, y, 1)[0] if len(x)>1 else 0
                if slope >0.01 * monthly.mean():
                    trend = "increasing"
                elif slope < -0.01*monthly.mean():
                    trend = "decreasing"
                else:
                    trend = "stable"

                # Seasonality — monthly avg across years if >1 year data
                seasonal = None
                if len(monthly) >=12:
                    # Group by month
                    df_month = pd.DataFrame({"value": monthly, "month": monthly.index.month})
                    seasonal = df_month.groupby("month")["value"].mean()

                results[f"{date_col}_{metric}"] = {
                    "date_col": date_col,
                    "metric": metric,
                    "monthly": monthly,
                    "mom_growth": float(mom) if mom is not None and pd.notna(mom) else None,
                    "yoy_growth": float(yoy) if yoy is not None and pd.notna(yoy) else None,
                    "rolling_3": rolling_3,
                    "rolling_6": rolling_6,
                    "peak": peak,
                    "low": low,
                    "trend": trend,
                    "slope": float(slope),
                    "seasonal_avg": seasonal
                }

            except Exception as e:
                continue

    available = len(results) >0
    return {"available": available, "trends": results, "reason": None if available else "No sufficient time series data"}
