"""
Temporal EDA — trends, MoM, YoY, rolling.
"""
import pandas as pd

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


from typing import Dict, Any, Optional, List

def analyze_temporal(df: pd.DataFrame, datetime_cols: List[str], numeric_cols: List[str]) -> Dict[str, Any]:
    """
    For each datetime col + each numeric metric, produce time series aggregations.
    """
    if not datetime_cols or not numeric_cols:
        return {"available": False, "reason": "Need both datetime and numeric columns"}

    results = {}
    for date_col in datetime_cols:
        if date_col not in df.columns:
            continue
        try:
            # Ensure datetime
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce', dayfirst=True)
            df_copy = df_copy.dropna(subset=[date_col])
            if len(df_copy) == 0:
                continue

            df_copy = df_copy.sort_values(date_col)

            # Determine range
            min_date = df_copy[date_col].min()
            max_date = df_copy[date_col].max()

            # For best meaningful metric
            metric_col = get_best_metric(numeric_cols) or numeric_cols[0]
            # Resample
            df_copy.set_index(date_col, inplace=True)

            # Try daily, weekly, monthly, yearly
            resampled = {}
            try:
                # Monthly trend
                monthly = df_copy[metric_col].resample('ME').sum()
                resampled['monthly'] = monthly
                # Weekly
                weekly = df_copy[metric_col].resample('W').sum()
                resampled['weekly'] = weekly
                # Yearly
                yearly = df_copy[metric_col].resample('YE').sum()
                resampled['yearly'] = yearly

                # Growth calculations
                if len(monthly) >=2:
                    mom = monthly.pct_change().iloc[-1] *100
                    yoy = None
                    if len(monthly) >=13:
                        yoy = (monthly.iloc[-1] - monthly.iloc[-13]) / monthly.iloc[-13] *100 if monthly.iloc[-13]!=0 else None
                else:
                    mom = None
                    yoy = None

                # Peak/low
                peak_month = monthly.idxmax() if len(monthly)>0 else None
                low_month = monthly.idxmin() if len(monthly)>0 else None

                # Trend: simple linear regression slope sign
                trend = "stable"
                if len(monthly) >=3:
                    x = range(len(monthly))
                    y = monthly.values
                    # simple slope via correlation
                    import numpy as np
                    slope = np.polyfit(x, y, 1)[0] if len(x)>1 else 0
                    if slope > 0:
                        trend = "increasing"
                    elif slope <0:
                        trend = "decreasing"

                results[date_col] = {
                    "metric": metric_col,
                    "min_date": min_date,
                    "max_date": max_date,
                    "monthly": monthly,
                    "weekly": weekly,
                    "yearly": yearly,
                    "mom_growth_pct": float(mom) if mom is not None and pd.notna(mom) else None,
                    "yoy_growth_pct": float(yoy) if yoy is not None and pd.notna(yoy) else None,
                    "peak_month": peak_month,
                    "low_month": low_month,
                    "trend": trend,
                    "total_points": len(df_copy)
                }

            except Exception as e:
                results[date_col] = {"error": str(e), "available": False}

        except Exception as e:
            continue

    return {"available": True, "by_date_col": results}
