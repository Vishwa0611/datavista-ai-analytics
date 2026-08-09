"""
Page 9 — Time Series
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from app.ui.layout import apply_custom_css
from app.components.sidebar import render_sidebar
from src.visualization.charts import create_line_chart, create_metric_trend_with_rolling
import pandas as pd

st.set_page_config(page_title="Time Series — DataVista", layout="wide")
apply_custom_css()
render_sidebar(current_page_file="pages/09_TimeSeries.py")

st.title("⏱️ Time Series Analysis")
st.caption("Step 9/9 — Trend, Seasonality, MoM/YoY, Peak/Low, Forecasting (estimates)")

if 'pipeline_result' not in st.session_state or not st.session_state['pipeline_result']:
    st.warning("No dataset")
    st.switch_page("pages/01_Upload.py")
    st.stop()

result = st.session_state['pipeline_result']
ts = result.get('timeseries', {})
trends_wrapper = ts.get('trends', {})
trends = trends_wrapper.get('trends', {}) if isinstance(trends_wrapper, dict) else {}
forecasts = ts.get('forecasts', {})

if not trends_wrapper.get('available'):
    st.info(f"Time series unavailable: {trends_wrapper.get('reason','Need datetime + numeric')}")
    st.caption("If your dataset has order_date and revenue, this page will show monthly trend, growth, seasonality, peak periods.")
    st.stop()

for key, data in trends.items():
    with st.container():
        st.markdown(f"### {data.get('date_col')} → {data.get('metric')}")
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: st.metric("Trend", data.get('trend','unknown'))
        with c2: st.metric("MoM Growth", f"{data.get('mom_growth'):.1f}%" if data.get('mom_growth') else "N/A")
        with c3: st.metric("YoY Growth", f"{data.get('yoy_growth'):.1f}%" if data.get('yoy_growth') else "N/A")
        with c4: st.metric("Peak Month", str(data.get('peak'))[:10] if data.get('peak') else "N/A")
        with c5: st.metric("Low Month", str(data.get('low'))[:10] if data.get('low') else "N/A")

        # Charts
        monthly = data.get('monthly')
        if monthly is not None:
            fig = create_line_chart(monthly, title=f"Monthly {data.get('metric')} Trend")
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            # Rolling
            rolling_3 = data.get('rolling_3')
            if rolling_3 is not None:
                fig2 = create_metric_trend_with_rolling(monthly, rolling_3, title="Trend with 3M Rolling Avg")
                if fig2:
                    st.plotly_chart(fig2, use_container_width=True)

        # Seasonal
        seasonal = data.get('seasonal_avg')
        if seasonal is not None and not seasonal.empty:
            st.markdown("**Seasonality — Avg by Month (across years)**")
            df_seas = seasonal.reset_index()
            df_seas.columns = ['Month','Avg']
            st.bar_chart(df_seas.set_index('Month'))

        # Forecast
        fc = forecasts.get(key)
        if fc and fc.get('available'):
            st.divider()
            st.markdown("#### Forecast — Next 3 Periods (Estimates, Not Guaranteed)")
            st.caption(fc.get('disclaimer'))
            c1,c2 = st.columns(2)
            with c1:
                st.write("**Moving Average (3M) Forecast**")
                st.write(fc.get('forecast_ma'))
                st.caption(fc.get('method_ma'))
            with c2:
                st.write("**Linear Trend Forecast**")
                st.write(fc.get('forecast_linear'))
                st.caption(fc.get('method_linear'))

            # Combined chart
            try:
                import plotly.graph_objects as go
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=monthly.index, y=monthly.values, name='Historical', mode='lines+markers'))
                fig.add_trace(go.Scatter(x=fc['forecast_ma'].index, y=fc['forecast_ma'].values, name='MA Forecast', mode='lines+markers', line=dict(dash='dash')))
                fig.add_trace(go.Scatter(x=fc['forecast_linear'].index, y=fc['forecast_linear'].values, name='Linear Forecast', mode='lines+markers', line=dict(dash='dot')))
                fig.update_layout(title="Historical + Forecast", template="plotly_white", height=400)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.caption(f"Forecast chart error: {e}")

st.divider()
c1,c2 = st.columns(2)
with c1:
    if st.button("Continue to AI Insights →", type="primary"):
        st.switch_page("pages/10_AI_Insights.py")
with c2:
    if st.button("← Back to Segmentation"):
        st.switch_page("pages/08_Segmentation.py")
