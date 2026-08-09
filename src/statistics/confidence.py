"""
Confidence intervals and effect size.
"""
import pandas as pd
import numpy as np
from scipy import stats
from typing import List, Dict, Any

def calculate_confidence_intervals(df: pd.DataFrame, numeric_cols: List[str], confidence: float = 0.95) -> Dict[str, Any]:
    results = {}
    for col in numeric_cols[:5]:
        try:
            s = pd.to_numeric(df[col], errors='coerce').dropna()
            if len(s) < 10:
                continue
            mean = s.mean()
            sem = stats.sem(s)  # standard error mean
            # t critical value
            ci = stats.t.interval(confidence, len(s)-1, loc=mean, scale=sem)
            margin = ci[1] - mean
            results[col] = {
                "mean": float(mean),
                "ci_lower": float(ci[0]),
                "ci_upper": float(ci[1]),
                "margin": float(margin),
                "confidence": confidence,
                "interpretation": f"95% CI [{ci[0]:.2f}, {ci[1]:.2f}] — if we repeated sampling, 95% of intervals would contain true mean. Margin ±{margin:.2f}."
            }
        except:
            continue
    return {"available": len(results)>0, "intervals": results}
