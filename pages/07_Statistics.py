"""
Page 7 — Statistics — Enhanced Attractive — Fixed p-value bug
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from app.ui.layout import apply_custom_css
from app.components.sidebar import render_sidebar

st.set_page_config(page_title="Statistics — DataVista", layout="wide")
apply_custom_css()
render_sidebar(current_page_file="pages/07_Statistics.py")

def format_pvalue(p):
    if p is None:
        return "p = N/A"
    if p < 0.001:
        return "p < 0.001"
    else:
        return f"p = {p:.4f}"

st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <div style="width:40px; height:40px; background:linear-gradient(135deg,#EC4899,#8B5CF6); border-radius:12px; display:flex; align-items:center; justify-content:center; color:white; font-size:20px;">📈</div>
    <div>
        <div style="font-size:24px; font-weight:800; letter-spacing:-0.02em;">Statistical Analysis — Major Differentiator</div>
        <div style="font-size:12px; color:#64748B; font-weight:500;">Step 7/9 • Descriptive, correlation, hypothesis testing with H0/H1, p-value, effect size, plain English • Correlation ≠ causation</div>
    </div>
</div>
""", unsafe_allow_html=True)

if 'pipeline_result' not in st.session_state or not st.session_state['pipeline_result']:
    st.warning("No dataset")
    st.switch_page("pages/01_Upload.py")
    st.stop()

result = st.session_state['pipeline_result']
stats_data = result.get('statistics', {})

if not stats_data:
    st.warning("No statistical results — need numeric/categorical columns")
    st.stop()

summary = stats_data.get('summary', {})
c1,c2,c3,c4 = st.columns(4)
with c1: st.metric("CORRELATIONS", summary.get('correlations_found',0))
with c2: st.metric("TESTS RUN", summary.get('tests_run',0))
with c3: st.metric("SIGNIFICANT", summary.get('significant_tests',0))
with c4: st.metric("CI CALC", summary.get('ci_calculated',0))

tab1, tab2, tab3 = st.tabs(["🔗 Correlations", "🧪 Hypothesis Tests", "📏 Confidence Intervals"])

with tab1:
    st.markdown("""
    <div style="background:#F0F9FF; border:1px solid #BAE6FD; border-radius:12px; padding:12px 16px; margin-bottom:12px;">
        <div style="font-weight:700; font-size:13px; color:#0C4A6E;">📚 Pearson vs Spearman</div>
        <div style="font-size:12px; color:#075985; margin-top:4px;"><b>Pearson:</b> linear, sensitive to outliers • <b>Spearman:</b> rank, robust, monotonic • <b style="background:#FEF2F2; padding:2px 6px; border-radius:4px;">Correlation does NOT imply causation</b></div>
    </div>
    """, unsafe_allow_html=True)
    corr = stats_data.get('correlation', {})
    results = corr.get('results', [])
    if not results:
        st.info("No correlations")
    for res in results[:6]:
        with st.container():
            badge = "🟢 Significant" if res.is_significant else "⚪ Not significant"
            st.markdown(f"**🔗 {res.col1} vs {res.col2}** — {badge} • r={res.pearson_r:.3f} ({format_pvalue(res.pearson_p)})")
            c1,c2 = st.columns(2)
            with c1: st.metric("Pearson r", f"{res.pearson_r:.3f}", format_pvalue(res.pearson_p))
            with c2: st.metric("Spearman r", f"{res.spearman_r:.3f}", format_pvalue(res.spearman_p))
            st.caption(f"💡 {res.interpretation}")

with tab2:
    tests = stats_data.get('hypothesis_tests', [])
    if not tests:
        st.info("No hypothesis tests auto-suggested — need categorical + numeric (e.g., profit by region)")
    for test in tests:
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <div style="font-weight:800; font-size:14px;">🧪 {test.test_name}</div>
                <span class="badge {'badge-green' if test.p_value<0.05 else 'badge-gray'}">{test.decision} • {format_pvalue(test.p_value)}</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**H0:** {test.null_hypothesis}")
            st.markdown(f"**H1:** {test.alt_hypothesis}")
            c1,c2,c3 = st.columns(3)
            with c1: st.metric("Test Statistic", f"{test.test_statistic:.3f}")
            with c2: st.metric("p-value", format_pvalue(test.p_value))
            with c3: st.metric("α", "0.05")
            st.info(f"💡 **Interpretation:** {test.interpretation}")
            if test.effect_size is not None:
                st.markdown(f"**Effect Size (Cohen's d):** {test.effect_size:.3f} — {test.effect_interpretation} • Effect size matters beyond p-value")

with tab3:
    ci_data = stats_data.get('confidence_intervals', {})
    intervals = ci_data.get('intervals', {})
    if not intervals:
        st.info("Need numeric columns >=10 rows for CI")
    for col, data in intervals.items():
        with st.container(border=True):
            st.markdown(f"**📏 {col} — 95% CI**")
            c1,c2,c3 = st.columns(3)
            with c1: st.metric("Mean", f"{data['mean']:.2f}")
            with c2: st.metric("CI Lower", f"{data['ci_lower']:.2f}")
            with c3: st.metric("CI Upper", f"{data['ci_upper']:.2f}")
            st.caption(f"💡 {data['interpretation']}")

st.divider()
c1,c2 = st.columns(2)
with c1:
    if st.button("🧩 Continue to Segmentation →", type="primary", use_container_width=True):
        st.switch_page("pages/08_Segmentation.py")
with c2:
    if st.button("← Back to KPIs", use_container_width=True):
        st.switch_page("pages/06_KPIs.py")
