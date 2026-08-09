"""
Page 5 — EDA — Enhanced Attractive
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
from app.ui.layout import apply_custom_css
from app.components.sidebar import render_sidebar
from src.visualization.charts import create_histogram, create_box_plot, create_bar_chart, create_line_chart, create_scatter_plot, create_correlation_heatmap

st.set_page_config(page_title="EDA — DataVista", layout="wide")
apply_custom_css()
render_sidebar(current_page_file="pages/05_EDA.py")

st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <div style="width:40px; height:40px; background:linear-gradient(135deg,#06B6D4,#0891B2); border-radius:12px; display:flex; align-items:center; justify-content:center; color:white; font-size:20px;">📊</div>
    <div>
        <div style="font-size:24px; font-weight:800; letter-spacing:-0.02em;">Exploratory Data Analysis</div>
        <div style="font-size:12px; color:#64748B; font-weight:500;">Step 5/9 • Smart chart selection based on data types, not meaningless charts • Why each chart matters</div>
    </div>
</div>
""", unsafe_allow_html=True)

if 'pipeline_result' not in st.session_state or not st.session_state['pipeline_result']:
    st.warning("No dataset")
    st.switch_page("pages/01_Upload.py")
    st.stop()

result = st.session_state['pipeline_result']
eda = result.get('eda', {})
profile = result['profile']
df = result['df_cleaned']

if not eda:
    st.warning("EDA not available")
    st.stop()

summary = eda.get('summary', {})
c1,c2,c3,c4 = st.columns(4)
with c1:
    st.markdown(f"<div class='premium-card' style='text-align:center;'><div style='font-size:11px; color:#64748B; font-weight:700;'>NUMERIC</div><div style='font-size:24px; font-weight:800;'>{summary.get('numeric_count',0)}</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='premium-card' style='text-align:center;'><div style='font-size:11px; color:#64748B; font-weight:700;'>CATEGORICAL</div><div style='font-size:24px; font-weight:800;'>{summary.get('categorical_count',0)}</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='premium-card' style='text-align:center;'><div style='font-size:11px; color:#64748B; font-weight:700;'>TEMPORAL</div><div style='font-size:14px; font-weight:700; color:{'#10B981' if summary.get('temporal_available') else '#94A3B8'}'>{'✅ Yes' if summary.get('temporal_available') else '❌ No'}</div></div>", unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='premium-card' style='text-align:center;'><div style='font-size:11px; color:#64748B; font-weight:700;'>CHARTS PLANNED</div><div style='font-size:24px; font-weight:800; color:#6366F1;'>{summary.get('total_charts_planned',0)}</div><div style='font-size:10px; color:#64748B;'>Smart selection</div></div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Overview", "🔢 Numerical", "🔤 Categorical", "📅 Temporal", "🔗 Correlation"])

with tab1:
    st.markdown("#### 🧠 Chart Plan — Why Each Chart Matters (Not Chart Spam)")
    for plan in eda.get('chart_plan', [])[:10]:
        st.markdown(f"""
        <div style="background:white; border:1px solid #E2E8F0; border-radius:10px; padding:10px 14px; margin-bottom:6px; display:flex; justify-content:space-between; align-items:center;">
            <div><span style="background:#EEF2FF; color:#4338CA; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:600;">{plan.get('type')}</span> <span style="font-weight:600; font-size:13px; margin-left:8px;">{plan.get('column', plan.get('date_col',''))}</span></div>
            <div style="font-size:11px; color:#64748B;">{plan.get('reason','')}</div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    numerical = eda.get('numerical', {})
    if not numerical:
        st.info("No numerical columns")
    for col, stats in numerical.items():
        with st.container():
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div style="font-weight:800; font-size:16px;">🔢 {col}</div>
                <div><span class="badge badge-indigo">Mean {stats['mean']:.1f} • Median {stats['median']:.1f} • Skew {stats['skew']:.2f}</span></div>
            </div>
            <div style="font-size:12px; color:#475569; background:#F8FAFC; padding:8px 12px; border-radius:8px; margin-bottom:12px;">💡 {stats['skew_interpretation']}</div>
            """, unsafe_allow_html=True)
            c1,c2 = st.columns(2)
            with c1:
                fig = create_histogram(df, col, title=f"Distribution of {col}")
                if fig: st.plotly_chart(fig, use_container_width=True)
            with c2:
                fig = create_box_plot(df, col, title=f"Box Plot — {col} (Outliers)")
                if fig: st.plotly_chart(fig, use_container_width=True)

with tab3:
    categorical = eda.get('categorical', {})
    if not categorical:
        st.info("No categorical columns")
    for col, stats in categorical.items():
        with st.container():
            st.markdown(f"**🔤 {col}** — Unique {stats['unique']}, Top: {stats['most_common']} ({stats['most_common_count']})")
            if stats.get('pareto_insight'):
                st.success(f"📊 {stats['pareto_insight']}")
            fig = create_bar_chart(df, col, title=f"Frequency — {col}")
            if fig: st.plotly_chart(fig, use_container_width=True)

with tab4:
    temporal = eda.get('temporal', {})
    if not temporal.get('available'):
        st.info(f"Temporal unavailable: {temporal.get('reason','Need date + numeric')}")
    else:
        for date_col, data in temporal.get('by_date_col', {}).items():
            if not isinstance(data, dict) or 'monthly' not in data:
                continue
            with st.container():
                st.markdown(f"**📅 {date_col} → {data.get('metric')}** — Trend {data.get('trend')} • MoM {data.get('mom_growth_pct')} • YoY {data.get('yoy_growth_pct')}")
                fig = create_line_chart(data['monthly'], title=f"Monthly {data.get('metric')} trend")
                if fig: st.plotly_chart(fig, use_container_width=True)

with tab5:
    stats_res = result.get('statistics', {})
    corr_data = stats_res.get('correlation', {})
    if not corr_data.get('available'):
        st.info("Correlation needs at least 2 numeric columns")
    else:
        matrix = corr_data.get('pearson_matrix')
        if matrix is not None and not matrix.empty:
            fig = create_correlation_heatmap(matrix)
            if fig: st.plotly_chart(fig, use_container_width=True)

c1,c2 = st.columns(2)
with c1:
    if st.button("🎯 Continue to KPIs →", type="primary", use_container_width=True):
        st.switch_page("pages/06_KPIs.py")
with c2:
    if st.button("← Back to Cleaning", use_container_width=True):
        st.switch_page("pages/04_Cleaning.py")
