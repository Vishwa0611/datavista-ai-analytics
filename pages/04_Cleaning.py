"""
Page 4 — Cleaning — Enhanced
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
from app.ui.layout import apply_custom_css
from app.components.sidebar import render_sidebar
from src.cleaning.engine import apply_cleaning_operations, suggest_cleaning_operations
from src.utils.constants import CleaningOp
from src.orchestrator.pipeline import run_full_pipeline
from src.quality.auditor import audit_dataset

st.set_page_config(page_title="Cleaning — DataVista", layout="wide")
apply_custom_css()
render_sidebar(current_page_file="pages/04_Cleaning.py")

st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <div style="width:40px; height:40px; background:linear-gradient(135deg,#F59E0B,#D97706); border-radius:12px; display:flex; align-items:center; justify-content:center; color:white; font-size:20px;">🧹</div>
    <div>
        <div style="font-size:24px; font-weight:800; letter-spacing:-0.02em;">Data Cleaning — Original → Cleaned</div>
        <div style="font-size:12px; color:#64748B; font-weight:500;">Step 4/9 • Never silently modify original • Transformation log for reproducibility • Original immutable</div>
    </div>
</div>
""", unsafe_allow_html=True)

if 'pipeline_result' not in st.session_state or not st.session_state['pipeline_result']:
    st.warning("No dataset loaded.")
    st.switch_page("pages/01_Upload.py")
    st.stop()

result = st.session_state['pipeline_result']
quality = result['quality']
profile = result['profile']
df_original = result['df_original']

suggested = suggest_cleaning_operations(df_original, quality)

st.markdown("""
<div style="background:white; border:1px solid #E2E8F0; border-radius:16px; padding:20px; margin:16px 0;">
    <div style="font-weight:700; font-size:14px; margin-bottom:8px;">💡 Suggested Operations (Based on Quality Audit)</div>
</div>
""", unsafe_allow_html=True)

if suggested:
    for op in suggested:
        st.markdown(f"""
        <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:10px; padding:10px 14px; margin-bottom:6px; display:flex; justify-content:space-between; align-items:center;">
            <div><span style="font-weight:600; font-size:12px;">{op['op']}</span> <span style="color:#92400E; font-size:12px;">on `{op['column']}`</span></div>
            <div style="font-size:11px; color:#B45309;">{op.get('reason','')}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.success("✨ No cleaning suggested — high quality!")

st.divider()
st.markdown("#### 🛠️ Build Cleaning Pipeline")

with st.form("cleaning_form"):
    st.write("**Select operations to apply:**")
    selected_ops = []
    for idx, op_dict in enumerate(suggested):
        checked = st.checkbox(f"{op_dict['op']} | Column: {op_dict['column']} | Reason: {op_dict.get('reason','')}", key=f"op_{idx}", value=True if op_dict['op']!=CleaningOp.DROP_COL else False)
        if checked:
            selected_ops.append(op_dict)

    st.markdown("**Add Custom Operation**")
    c1,c2,c3 = st.columns(3)
    with c1:
        custom_op = st.selectbox("Operation", [e.value for e in CleaningOp], key="custom_op")
    with c2:
        custom_col = st.selectbox("Column (or all)", ["all"] + list(df_original.columns), key="custom_col")
    with c3:
        custom_case = st.selectbox("Case", ["lower","upper","title"], key="custom_case")

    add_custom = st.checkbox("Add custom operation above", key="add_custom")
    submitted = st.form_submit_button("🧹 Apply Cleaning", type="primary")

if submitted:
    ops_to_apply = selected_ops.copy()
    if add_custom:
        op_entry = {"op": custom_op, "column": custom_col}
        if custom_op == CleaningOp.STANDARDIZE_CASE.value:
            op_entry["case"] = custom_case
        ops_to_apply.append(op_entry)

    if not ops_to_apply:
        st.warning("No operations selected")
    else:
        with st.spinner(f"🧹 Applying {len(ops_to_apply)} operations..."):
            cleaning_result = apply_cleaning_operations(df_original, ops_to_apply)
            new_quality = audit_dataset(cleaning_result.df_cleaned, profile.numeric_cols, profile.categorical_cols)
            cleaning_result.score_before = quality.score
            cleaning_result.score_after = new_quality.score
            st.session_state['cleaning_result'] = cleaning_result
            metadata = result['metadata']
            new_pipeline = run_full_pipeline(df_original, metadata, app_version="0.1.0", cleaning_result=cleaning_result)
            new_pipeline['quality'] = new_quality
            st.session_state['pipeline_result'] = new_pipeline
            st.success(f"✅ Cleaning applied: {len(cleaning_result.log)} steps, rows {cleaning_result.rows_before} → {cleaning_result.rows_after}, quality {cleaning_result.score_before} → {cleaning_result.score_after}")

if 'cleaning_result' in st.session_state and st.session_state['cleaning_result']:
    cr = st.session_state['cleaning_result']
    st.divider()
    st.markdown("#### 📜 Transformation Log — Reproducibility")
    log_df = pd.DataFrame([rec.__dict__ if hasattr(rec, '__dict__') else rec.to_dict() for rec in cr.log])
    if not log_df.empty:
        st.dataframe(log_df, use_container_width=True)
    else:
        st.info("No transformations logged")

    c1,c2,c3 = st.columns(3)
    with c1: st.metric("Rows Before", cr.rows_before)
    with c2: st.metric("Rows After", cr.rows_after)
    with c3: st.metric("Quality After", cr.score_after if cr.score_after else "N/A")

    st.markdown("#### 👀 Preview Cleaned Data (100 rows)")
    st.dataframe(cr.df_cleaned.head(100), use_container_width=True)

    from src.reporting.exporter import export_cleaned_csv
    csv_bytes = export_cleaned_csv(cr.df_cleaned)
    st.download_button("📥 Download Cleaned CSV", data=csv_bytes, file_name="cleaned_data.csv", mime="text/csv", use_container_width=True)

else:
    st.info("No cleaning applied yet — showing original data")
    st.dataframe(df_original.head(100), use_container_width=True)

st.divider()
c1,c2 = st.columns(2)
with c1:
    if st.button("📊 Continue to EDA →", type="primary", use_container_width=True):
        st.switch_page("pages/05_EDA.py")
with c2:
    if st.button("← Back to Quality", use_container_width=True):
        st.switch_page("pages/03_Data_Quality.py")
