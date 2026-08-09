"""
Numerical EDA — descriptive stats.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any

def analyze_numerical(df: pd.DataFrame, numeric_cols: list) -> Dict[str, Dict[str, Any]]:
    results = {}
    for col in numeric_cols:
        if col not in df.columns:
            continue
        try:
            s = pd.to_numeric(df[col], errors='coerce').dropna()
            if len(s) == 0:
                continue
            q1 = s.quantile(0.25)
            q3 = s.quantile(0.75)
            iqr = q3 - q1
            # skewness, kurtosis
            skew = float(s.skew()) if len(s) >2 else 0.0
            kurt = float(s.kurtosis()) if len(s) >3 else 0.0

            # Interpretation of skew
            if abs(skew) < 0.5:
                skew_interp = "Approximately symmetric"
            elif skew > 0.5:
                skew_interp = "Right skewed — few high values pull mean higher than median"
            else:
                skew_interp = "Left skewed — few low values pull mean lower than median"

            results[col] = {
                "count": int(s.count()),
                "mean": float(s.mean()),
                "median": float(s.median()),
                "mode": float(s.mode().iloc[0]) if not s.mode().empty else None,
                "min": float(s.min()),
                "max": float(s.max()),
                "std": float(s.std()),
                "var": float(s.var()),
                "q1": float(q1),
                "q3": float(q3),
                "iqr": float(iqr),
                "skew": skew,
                "kurtosis": kurt,
                "skew_interpretation": skew_interp,
                "cv": float(s.std()/s.mean()) if s.mean()!=0 else None  # coefficient variation
            }
        except Exception as e:
            continue
    return results
