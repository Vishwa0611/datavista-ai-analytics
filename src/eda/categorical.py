"""
Categorical EDA.
"""
import pandas as pd
from typing import Dict, Any, List

def analyze_categorical(df: pd.DataFrame, categorical_cols: List[str], top_n: int = 10) -> Dict[str, Dict[str, Any]]:
    results = {}
    for col in categorical_cols:
        if col not in df.columns:
            continue
        try:
            s = df[col].dropna().astype(str)
            if len(s) == 0:
                continue
            freq = s.value_counts()
            freq_pct = s.value_counts(normalize=True) * 100
            unique = int(s.nunique())
            top = freq.head(top_n)

            # Pareto check: does top 20% categories contribute 80% rows?
            cumulative_pct = freq_pct.cumsum()
            pareto_80 = (cumulative_pct <= 80).sum()
            pareto_insight = None
            if len(freq) >0:
                top_pareto_pct = (pareto_80 / len(freq) *100) if len(freq)>0 else 0
                if top_pareto_pct <= 30:
                    pareto_insight = f"Approximately {top_pareto_pct:.0f}% of {col} values ({pareto_80} categories) account for 80% of records, indicating a concentrated distribution"

            results[col] = {
                "unique": unique,
                "top_n": top.to_dict(),
                "top_n_pct": {k: round(float(freq_pct[k]),2) for k in top.index},
                "freq_table": freq.to_dict(),
                "pareto_insight": pareto_insight,
                "most_common": freq.index[0] if len(freq)>0 else None,
                "most_common_count": int(freq.iloc[0]) if len(freq)>0 else 0
            }
        except Exception as e:
            continue
    return results
