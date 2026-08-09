"""
Statistics engine — orchestrates correlation, hypothesis tests, CI.
"""
from typing import List
import pandas as pd
from ..validation.schema import ModuleResult
from .correlation import analyze_correlations
from .hypothesis import auto_suggest_and_run_tests
from .confidence import calculate_confidence_intervals

def run_statistical_analysis(
    df: pd.DataFrame,
    numeric_cols: List[str],
    categorical_cols: List[str]
) -> ModuleResult:
    try:
        corr_result = analyze_correlations(df, numeric_cols)
        hypo_results = auto_suggest_and_run_tests(df, numeric_cols, categorical_cols)
        ci_results = calculate_confidence_intervals(df, numeric_cols)

        data = {
            "correlation": corr_result,
            "hypothesis_tests": hypo_results,
            "confidence_intervals": ci_results,
            "summary": {
                "correlations_found": len(corr_result.get("results", [])),
                "tests_run": len(hypo_results),
                "significant_tests": sum(1 for t in hypo_results if t.p_value <0.05),
                "ci_calculated": len(ci_results.get("intervals", {}))
            }
        }

        return ModuleResult(available=True, data=data)

    except Exception as e:
        return ModuleResult(available=False, reason=f"Statistical analysis failed: {e}")
