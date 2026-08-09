"""
Page 14 — Comparison Mode
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
from app.ui.layout import apply_custom_css
from app.components.sidebar import render_sidebar
from src.ingestion.loader import read_file
from src.profiling.profiler import profile_dataset
from src.quality.auditor import audit_dataset

st.set_page_config(page_title="Comparison — DataVista", layout="wide")
apply_custom_css()
render_sidebar(current_page_file="pages/14_Comparison.py")

st.title("🔄 Dataset Comparison Mode")
st.caption("Compare Schema, Row Counts, Missing, Distributions, KPIs — Before vs After, 2025 vs 2026, Region A vs B")

if 'pipeline_result' not in st.session_state or not st.session_state['pipeline_result']:
    st.warning("Load a dataset first in Upload page — this will be Dataset A")
    st.switch_page("pages/01_Upload.py")
    st.stop()

result_a = st.session_state['pipeline_result']
df_a = result_a['df_cleaned']
profile_a = result_a['profile']
quality_a = result_a['quality']

st.markdown("#### Dataset A — Currently Loaded")
st.write(f"File: {result_a['metadata'].get('file_name')} | Rows: {profile_a.row_count} | Cols: {profile_a.column_count} | Quality: {quality_a.score}")

st.divider()
st.markdown("#### Upload Dataset B for Comparison")

uploaded_b = st.file_uploader("Upload second dataset", type=['csv','xlsx','xls','json','parquet'], key="compare_b")

if uploaded_b:
    file_bytes = uploaded_b.read()
    try:
        res_b = read_file(file_bytes, uploaded_b.name)
        st.session_state['comparison_b'] = res_b
        st.success(f"Loaded Dataset B: {res_b.metadata['rows']} rows, {res_b.metadata['columns']} cols")
    except Exception as e:
        st.error(f"Failed: {e}")

if 'comparison_b' in st.session_state and st.session_state['comparison_b']:
    res_b = st.session_state['comparison_b']
    df_b = res_b.df
    profile_b = profile_dataset(df_b, res_b.metadata['file_name'])
    quality_b = audit_dataset(df_b, profile_b.numeric_cols, profile_b.categorical_cols)

    st.divider()
    st.markdown("### Comparison Results")

    # Schema diff
    st.markdown("#### Schema Comparison")
    cols_a = set(df_a.columns)
    cols_b = set(df_b.columns)
    only_a = cols_a - cols_b
    only_b = cols_b - cols_a
    common = cols_a & cols_b

    c1,c2,c3 = st.columns(3)
    with c1: st.metric("Columns in A only", len(only_a))
    with c2: st.metric("Columns in B only", len(only_b))
    with c3: st.metric("Common Columns", len(common))

    if only_a:
        st.warning(f"Columns only in A: {only_a}")
    if only_b:
        st.warning(f"Columns only in B: {only_b}")

    # Row counts
    st.markdown("#### Data Volume Comparison")
    c1,c2 = st.columns(2)
    with c1: st.metric("Dataset A Rows", profile_a.row_count)
    with c2: st.metric("Dataset B Rows", profile_b.row_count, delta=profile_b.row_count - profile_a.row_count)

    # Missing comparison
    st.markdown("#### Missing Values Comparison")
    missing_a = quality_a.missing.per_column
    missing_b = quality_b.missing.per_column
    compare_missing = []
    for col in common:
        pct_a = missing_a.get(col, {}).get('pct',0) if col in missing_a else 0
        pct_b = missing_b.get(col, {}).get('pct',0) if col in missing_b else 0
        if pct_a != pct_b:
            compare_missing.append({"column": col, "missing_A_%": pct_a, "missing_B_%": pct_b, "delta": pct_b-pct_a})
    if compare_missing:
        df_missing_cmp = pd.DataFrame(compare_missing).sort_values("delta", ascending=False)
        st.dataframe(df_missing_cmp, use_container_width=True)
        # Alert example
        for row in compare_missing:
            if row['delta'] > 5:
                st.error(f"⚠ Missing in {row['column']} increased from {row['missing_A_%']}% to {row['missing_B_%']}% — data quality regression")
    else:
        st.success("Missing percentages similar across datasets")

    # Numeric distribution comparison for common numeric cols
    st.markdown("#### Numeric Distribution Comparison (Common Columns)")
    common_numeric = [c for c in profile_a.numeric_cols if c in profile_b.numeric_cols]
    for col in common_numeric[:3]:
        try:
            mean_a = pd.to_numeric(df_a[col], errors='coerce').mean()
            mean_b = pd.to_numeric(df_b[col], errors='coerce').mean()
            st.write(f"**{col}** — Mean A: {mean_a:.2f}, Mean B: {mean_b:.2f}, Delta: {mean_b-mean_a:.2f} ({(mean_b-mean_a)/mean_a*100 if mean_a!=0 else 0:.1f}%)")
        except:
            continue

    # Quality score comparison
    st.markdown("#### Quality Score Comparison")
    c1,c2 = st.columns(2)
    with c1: st.metric("Quality A", quality_a.score)
    with c2: st.metric("Quality B", quality_b.score, delta=quality_b.score - quality_a.score)

else:
    st.info("Upload Dataset B to see comparison — useful for Before vs After, 2025 vs 2026, Region A vs B, Campaign A vs B")

c1,c2 = st.columns(2)
with c1:
    if st.button("← Back to Report"):
        st.switch_page("pages/13_Report.py")
with c2:
    if st.button("Back to Home"):
        st.switch_page("streamlit_app.py")
