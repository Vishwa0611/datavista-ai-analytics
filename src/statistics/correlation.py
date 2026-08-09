"""
Correlation analysis — Pearson & Spearman with interpretation.
"""
import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr
from typing import List, Dict, Any
from ..validation.schema import CorrelationResult

def analyze_correlations(df: pd.DataFrame, numeric_cols: List[str]) -> Dict[str, Any]:
    if len(numeric_cols) < 2:
        return {"available": False, "reason": "Need at least 2 numeric columns", "results": []}

    results = []
    # Compute correlation matrix for heatmap
    try:
        numeric_df = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        corr_matrix_pearson = numeric_df.corr(method='pearson')
        corr_matrix_spearman = numeric_df.corr(method='spearman')
    except:
        corr_matrix_pearson = None
        corr_matrix_spearman = None

    # Pairwise
    for i in range(len(numeric_cols)):
        for j in range(i+1, len(numeric_cols)):
            col1 = numeric_cols[i]
            col2 = numeric_cols[j]
            try:
                s1 = pd.to_numeric(df[col1], errors='coerce').dropna()
                s2 = pd.to_numeric(df[col2], errors='coerce').dropna()
                # Align
                combined = pd.DataFrame({col1: s1, col2: s2}).dropna()
                if len(combined) < 5:
                    continue
                # Pearson
                r_pearson, p_pearson = pearsonr(combined[col1], combined[col2])
                r_spearman, p_spearman = spearmanr(combined[col1], combined[col2])

                # Interpretation
                abs_r = abs(r_pearson)
                if abs_r < 0.1:
                    strength = "negligible"
                elif abs_r < 0.3:
                    strength = "weak"
                elif abs_r < 0.5:
                    strength = "moderate"
                elif abs_r < 0.7:
                    strength = "strong"
                else:
                    strength = "very strong"

                direction = "positive" if r_pearson >0 else "negative"

                # Improved interpretation with both p-values and derived var check
                # Check if one column is derived from the other (e.g., Total Sales = Units Sold * Unit Price)
                derived_warning = ""
                col1_lower = col1.lower()
                col2_lower = col2.lower()
                # Heuristic: if one column name contains the other and is a product (Total Sales contains Sales and Price)
                if ('total' in col1_lower or 'total' in col2_lower) and any(x in col1_lower+col2_lower for x in ['price', 'units', 'quantity']):
                    if 'sales' in col1_lower or 'sales' in col2_lower:
                        derived_warning = " Note: One variable appears mathematically derived from the other (e.g., Total Sales = Units × Price), so correlation is expected and not necessarily a discovered business relationship."

                interpretation = f"{strength.capitalize()} {direction} correlation: Pearson r={r_pearson:.2f} ({'p<0.001' if p_pearson<0.001 else f'p={p_pearson:.4f}'}), Spearman ρ={r_spearman:.2f} ({'p<0.001' if p_spearman<0.001 else f'p={p_spearman:.4f}'}). {'Statistically significant at α=0.05' if p_pearson<0.05 else 'Not significant'}. Correlation does NOT imply causation.{derived_warning}"

                is_sig = p_pearson < 0.05

                results.append(CorrelationResult(
                    col1=col1,
                    col2=col2,
                    pearson_r=float(r_pearson),
                    pearson_p=float(p_pearson),
                    spearman_r=float(r_spearman),
                    spearman_p=float(p_spearman),
                    interpretation=interpretation,
                    is_significant=is_sig
                ))
            except Exception as e:
                continue

    # Sort by significant and then by abs r
    results_sorted = sorted(results, key=lambda x: (not x.is_significant, -abs(x.pearson_r)))

    return {
        "available": True,
        "results": results_sorted,
        "pearson_matrix": corr_matrix_pearson,
        "spearman_matrix": corr_matrix_spearman,
        "top_correlations": results_sorted[:5]
    }
