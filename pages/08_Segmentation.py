"""
Page 8 — Segmentation
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from app.ui.layout import apply_custom_css
from app.components.sidebar import render_sidebar
from src.visualization.charts import create_pareto_chart, create_bar_chart
import pandas as pd

st.set_page_config(page_title="Segmentation — DataVista", layout="wide")
apply_custom_css()
render_sidebar(current_page_file="pages/08_Segmentation.py")

st.title("🧩 Segmentation Analysis")
st.caption("Step 8/9 — RFM, Pareto, Performance Ranking — only activates when data supports it")

if 'pipeline_result' not in st.session_state or not st.session_state['pipeline_result']:
    st.warning("No dataset")
    st.switch_page("pages/01_Upload.py")
    st.stop()

result = st.session_state['pipeline_result']
seg = result.get('segmentation', {})
seg_raw = result.get('segmentation_raw')

if not seg:
    st.info("Segmentation data not available")
    st.stop()

# RFM
st.markdown("### RFM — Recency, Frequency, Monetary (Customer Segmentation)")
rfm = seg.get('rfm', {})
if not rfm.get('available'):
    st.info(f"RFM unavailable — {rfm.get('reason','Need customer_id + date + monetary')}")
    st.caption("For RFM, dataset needs: customer_id column, date column (e.g., order_date), monetary column (e.g., revenue). E-commerce demo supports RFM.")
else:
    c1,c2 = st.columns([1,2])
    with c1:
        st.write("**Segment Counts:**")
        st.json(rfm.get('segment_counts', {}))
        st.caption("Champions: recent, frequent, high spend\nLoyal: consistent\nAt Risk: valuable but inactive\nLost: low recency & frequency")
    with c2:
        rfm_table = rfm.get('rfm_table')
        if rfm_table is not None and not rfm_table.empty:
            st.dataframe(rfm_table.head(100), use_container_width=True)
            # Bar chart segment counts
            seg_counts = rfm.get('segment_counts', {})
            if seg_counts:
                df_seg = pd.DataFrame(list(seg_counts.items()), columns=['Segment','Count'])
                fig = create_bar_chart(df_seg, 'Segment', 'Count', title="Customers by RFM Segment")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

# Pareto
st.divider()
st.markdown("### Pareto Analysis — 80/20 Rule")
pareto_dict = seg.get('pareto', {})
if not pareto_dict:
    st.info("Pareto needs categorical + numeric columns")
else:
    available_pareto = {k:v for k,v in pareto_dict.items() if v.get('available')}
    if not available_pareto:
        st.info("No Pareto analysis available — insufficient data")
    for key, pareto_res in list(available_pareto.items())[:3]:
        with st.container():
            st.markdown(f"**{key}**")
            st.success(pareto_res.get('insight'))
            fig = create_pareto_chart(pareto_res.get('grouped'), title=f"Pareto — {key}")
            if fig:
                st.plotly_chart(fig, use_container_width=True)

# Performance ranking
st.divider()
st.markdown("### Performance Ranking — Top Categories/Products/Regions")
perf = seg.get('performance_ranking', {})
if not perf:
    st.info("No performance ranking — need categorical + numeric")
else:
    for key, grouped in list(perf.items())[:4]:
        with st.container():
            st.markdown(f"**{key}** — Top 10 by sum")
            st.dataframe(grouped, use_container_width=True)
            # Try bar chart
            try:
                df_plot = grouped.reset_index()
                # first column is category, second is sum
                cat_col = df_plot.columns[0]
                val_col = 'sum'
                fig = create_bar_chart(df_plot, cat_col, val_col, title=f"{val_col} by {cat_col}")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            except:
                pass

c1,c2 = st.columns(2)
with c1:
    if st.button("Continue to Time Series →", type="primary"):
        st.switch_page("pages/09_TimeSeries.py")
with c2:
    if st.button("← Back to Statistics"):
        st.switch_page("pages/07_Statistics.py")
