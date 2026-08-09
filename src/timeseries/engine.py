"""
Time series engine orchestrator.
"""
from typing import List
from ..validation.schema import ModuleResult
from .trend import analyze_trends
from .forecasting import simple_forecast

def run_timeseries_analysis(df, datetime_cols: List[str], numeric_cols: List[str]) -> ModuleResult:
    try:
        trend_result = analyze_trends(df, datetime_cols, numeric_cols)

        # Add forecast for first trend if available
        forecasts = {}
        if trend_result.get("available"):
            for key, data in trend_result.get("trends", {}).items():
                monthly = data.get("monthly")
                if monthly is not None:
                    forecasts[key] = simple_forecast(monthly)

        data = {
            "trends": trend_result,
            "forecasts": forecasts
        }

        available = trend_result.get("available", False)

        return ModuleResult(available=available, data=data, reason=trend_result.get("reason") if not available else None)

    except Exception as e:
        return ModuleResult(available=False, reason=f"Time series analysis failed: {e}")
