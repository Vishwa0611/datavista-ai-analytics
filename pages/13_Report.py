"""
Page 13 — Report — Enhanced Attractive
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import json
from datetime import datetime
from app.ui.layout import apply_custom_css
from app.components.sidebar import render_sidebar
from src.reporting.generator import generate_html_report
from src.reporting.exporter import export_cleaned_csv, export_cleaned_excel, export_kpi_excel

st.set_page_config(page_title="Report — DataVista", layout="wide")
apply_custom_css()
render_sidebar(current_page_file="pages/13_Report.py")

st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <div style="width:40px; height:40px; background:linear-gradient(135deg,#6366F1,#8B5CF6); border-radius:12px; display:flex; align-items:center; justify-content:center; color:white; font-size:20px;">📄</div>
    <div>
        <div style="font-size:24px; font-weight:800; letter-spacing:-0.02em;">Automated Analytics Report</div>
        <div style="font-size:12px; color:#64748B; font-weight:500;">Executive summary, methodology, limitations, reproducibility — board-ready • 12 sections</div>
    </div>
</div>
""", unsafe_allow_html=True)

if 'pipeline_result' not in st.session_state or not st.session_state['pipeline_result']:
    st.warning("No dataset")
    st.switch_page("pages/01_Upload.py")
    st.stop()

result = st.session_state['pipeline_result']
html_report = generate_html_report(result)

# Preview
st.markdown("#### 📄 Report Preview — Executive Ready")
st.markdown("""
<div style="background:#F8FAFC; border:1px dashed #CBD5E1; border-radius:12px; padding:12px; margin-bottom:12px; display:flex; gap:8px; align-items:center;">
    <span style="font-size:16px;">💡</span>
    <span style="font-size:12px; color:#475569;">This is a live HTML preview — download below for sharing with management. Includes methodology, limitations, reproducibility manifest.</span>
</div>
""", unsafe_allow_html=True)
st.components.v1.html(html_report, height=700, scrolling=True)

st.divider()
st.markdown("#### 📥 Export Options — Download All")

c1,c2,c3,c4 = st.columns(4)
with c1:
    st.download_button("📄 Download HTML Report", data=html_report.encode('utf-8'), file_name=f"datavista_report_{datetime.now().strftime('%Y%m%d')}.html", mime="text/html", type="primary", use_container_width=True)
with c2:
    df_cleaned = result['df_cleaned']
    csv_bytes = export_cleaned_csv(df_cleaned)
    st.download_button("📊 Download Cleaned CSV", data=csv_bytes, file_name="cleaned_data.csv", mime="text/csv", use_container_width=True)
with c3:
    kpi_data = result.get('kpi', {})
    kpis = kpi_data.get('kpis', []) if kpi_data else []
    if kpis:
        kpi_bytes = export_kpi_excel(kpis)
        st.download_button("📈 Download KPIs Excel", data=kpi_bytes, file_name="kpis.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
with c4:
    manifest = {
        "app_version": result.get('app_version'),
        "timestamp": datetime.now().isoformat(),
        "file_metadata": result.get('metadata'),
        "quality_score": result.get('quality').score if result.get('quality') else None,
        "cleaning_log": [rec.__dict__ for rec in result.get('cleaning').log] if result.get('cleaning') else [],
        "domain": result.get('profile').detected_domain if result.get('profile') else None,
        "kpi_count": len(kpis) if kpis else 0,
        "insights_count": len(result.get('insights', []))
    }
    st.download_button("🔍 Download Reproducibility JSON", data=json.dumps(manifest, indent=2, default=str).encode('utf-8'), file_name="reproducibility_manifest.json", mime="application/json", use_container_width=True)

with st.expander("📚 Methodology — How results were computed", expanded=False):
    st.markdown("""
    <div style="background:white; border:1px solid #E2E8F0; border-radius:12px; padding:16px; font-size:12px; line-height:1.6; color:#475569;">
    <b>Tools:</b> Python pandas, DuckDB, SciPy, Plotly<br>
    <b>Profiling:</b> Column type inference via dtype + unique ratio + regex PII + datetime parsing >80%<br>
    <b>Quality Scoring:</b> Weighted 0-100: Completeness 40%, Uniqueness 20%, Validity 20%, Consistency 20%<br>
    <b>Outliers:</b> IQR method (Q1-1.5IQR, Q3+1.5IQR)<br>
    <b>Correlation:</b> Pearson linear + Spearman rank, p-value via scipy<br>
    <b>Tests:</b> Welch's t-test, ANOVA, Chi-square, α=0.05<br>
    <b>CI:</b> t.interval mean ± t*SEM, 95%<br>
    <b>Effect Size:</b> Cohen's d<br>
    <b>KPIs:</b> Domain-aware fuzzy matching, formula + interpretation<br>
    <b>AI Insights:</b> Deterministic rule engine Finding→Evidence→Meaning→Action, no invented numbers
    </div>
    """, unsafe_allow_html=True)

with st.expander("⚠️ Limitations — Honest", expanded=False):
    st.markdown("""
    - Analysis based on provided dataset only — no external validation
    - Domain detection heuristic — verify KPIs match business definitions
    - Missing data handling may bias if not random
    - Correlation does not imply causation — explicitly stated
    - Forecasts estimates, not guaranteed
    - Segmentation requires sufficient columns — shows unavailable reason
    - Max file 200MB MVP — for 10M rows need chunking, Polars, BigQuery
    """)

c1,c2 = st.columns(2)
with c1:
    if st.button("← Back to SQL Lab", use_container_width=True):
        st.switch_page("pages/12_SQL_Lab.py")
with c2:
    if st.button("🔄 Go to Comparison →", use_container_width=True):
        st.switch_page("pages/14_Comparison.py")
