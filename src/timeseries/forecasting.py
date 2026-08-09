"""
Simple forecasting — moving average and linear trend, clearly labelled as estimate.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any

def simple_forecast(monthly_series: pd.Series, periods: int = 3) -> Dict[str, Any]:
    """
    Forecast next N periods using:
    - Moving average (3-month)
    - Linear trend extrapolation
    Returns both with disclaimer.
    """
    try:
        if len(monthly_series) <6:
            return {"available": False, "reason": "Need at least 6 months for forecast"}

        # Moving avg forecast: last 3 months avg
        last_3_avg = monthly_series.tail(3).mean()
        ma_forecast = [float(last_3_avg)] * periods

        # Linear trend
        x = np.arange(len(monthly_series))
        y = monthly_series.values
        slope, intercept = np.polyfit(x, y, 1)
        future_x = np.arange(len(monthly_series), len(monthly_series)+periods)
        linear_forecast = [float(slope*xi + intercept) for xi in future_x]

        # Create future dates
        last_date = monthly_series.index[-1]
        future_dates = pd.date_range(start=last_date, periods=periods+1, freq='ME')[1:]

        return {
            "available": True,
            "method_ma": "3-month moving average — simple, assumes recent average continues",
            "method_linear": "Linear trend extrapolation — assumes existing trend continues",
            "forecast_ma": pd.Series(ma_forecast, index=future_dates),
            "forecast_linear": pd.Series(linear_forecast, index=future_dates),
            "disclaimer": "Forecast is an estimate based on historical pattern, not guaranteed. Use for planning, not commitment.",
            "last_3_avg": float(last_3_avg),
            "slope": float(slope)
        }
    except Exception as e:
        return {"available": False, "reason": f"Forecast failed: {e}"}
