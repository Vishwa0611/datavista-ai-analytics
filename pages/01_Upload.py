"""
Page 1 — Upload — Enhanced Attractive
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import io
from app.ui.layout import apply_custom_css
from app.components.sidebar import render_sidebar
from src.ingestion.loader import read_file
from src.ingestion.sample_loader import get_sample_list, get_sample_path
from src.orchestrator.pipeline import run_full_pipeline

st.set_page_config(page_title="Upload — DataVista", layout="wide")
apply_custom_css()
render_sidebar(current_page_file="pages/01_Upload.py")

# Header with stepper
st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <div style="width:40px; height:40px; background:linear-gradient(135deg,#111827,#6366F1); border-radius:12px; display:flex; align-items:center; justify-content:center; color:white; font-size:20px;">📤</div>
    <div>
        <div style="font-size:24px; font-weight:800; letter-spacing:-0.02em;">Upload Dataset</div>
        <div style="font-size:12px; color:#64748B; font-weight:500;">Step 1/9 • Your data stays in memory • PII detection active • No external upload unless you enable AI</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Demo section — attractive cards
st.markdown("""
<div style="background:linear-gradient(135deg,#FFFFFF 0%,#F8FAFC 100%); border:1px solid #E2E8F0; border-radius:16px; padding:20px; margin:16px 0;">
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
        <span style="background:#111827; color:white; font-size:11px; font-weight:700; padding:3px 10px; border-radius:999px; letter-spacing:0.05em;">RECOMMENDED</span>
        <span style="font-weight:700; font-size:16px;">Try Demo Dataset — No Upload Needed</span>
        <span style="font-size:12px; color:#64748B;">• 5 seconds • Perfect for recruiter review</span>
    </div>
</div>
""", unsafe_allow_html=True)

samples = get_sample_list()
cols = st.columns(3)
icons = ["🛒", "📣", "💳"]
colors = ["#EEF2FF", "#ECFDF5", "#F5F3FF"]
for idx, sample in enumerate(samples):
    with cols[idx]:
        st.markdown(f"""
        <div class="demo-card" style="border-top:3px solid #6366F1;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div style="width:48px; height:48px; background:{colors[idx]}; border-radius:14px; display:flex; align-items:center; justify-content:center; font-size:24px;">{icons[idx]}</div>
                <span class="badge badge-indigo">{sample['domain']}</span>
            </div>
            <div style="font-weight:800; font-size:15px; letter-spacing:-0.01em; margin-bottom:6px;">{sample['title']}</div>
            <div style="font-size:12px; color:#475569; line-height:1.5; height:44px; margin-bottom:12px;">{sample['description']}</div>
            <div style="display:flex; gap:6px; flex-wrap:wrap; margin-bottom:16px;">
                <span class="badge badge-gray">📊 {sample['rows']} rows</span>
                <span class="badge badge-gray">🎯 {sample['domain']}</span>
                <span class="badge badge-green">✓ messy demo</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Load {sample['id']} →", key=f"demo_up_{sample['id']}", type="primary" if idx==0 else "secondary", use_container_width=True):
            path = get_sample_path(sample['id'])
            with open(path, 'rb') as f:
                file_bytes = f.read()
            st.session_state['uploaded_file_bytes'] = file_bytes
            st.session_state['uploaded_file_name'] = f"{sample['id']}.csv"
            result = read_file(file_bytes, f"{sample['id']}.csv")
            st.session_state['ingestion_result'] = result
            with st.spinner("⚙️ Running full pipeline: profiling → quality → EDA → KPIs → stats → insights..."):
                pipeline_result = run_full_pipeline(result.df, result.metadata, app_version="0.1.0")
                st.session_state['pipeline_result'] = pipeline_result
            st.success(f"✅ Loaded {sample['id']}: {result.metadata['rows']} rows — redirecting to profiling...")
            st.switch_page("pages/02_Profiling.py")

st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

# Upload area — enhanced
st.markdown("""
<div style="background:white; border:1px solid #E2E8F0; border-radius:16px; padding:20px; margin-bottom:16px;">
    <div style="font-weight:700; font-size:15px; margin-bottom:4px;">📁 Upload Your Own Dataset</div>
    <div style="font-size:12px; color:#64748B;">CSV, XLSX, XLS, JSON, Parquet • Up to 200MB • Encoding auto-detected (utf-8 → latin1 fallback) • Secure validation</div>
</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader("Drag and drop your dataset here", type=['csv','xlsx','xls','json','parquet'], label_visibility="collapsed")

if uploaded:
    file_bytes = uploaded.read()
    st.session_state['uploaded_file_bytes'] = file_bytes
    st.session_state['uploaded_file_name'] = uploaded.name

if 'uploaded_file_bytes' in st.session_state and st.session_state['uploaded_file_bytes']:
    file_bytes = st.session_state['uploaded_file_bytes']
    file_name = st.session_state['uploaded_file_name']

    if file_name.lower().endswith(('.xlsx','.xls')):
        import pandas as pd
        try:
            xls = pd.ExcelFile(io.BytesIO(file_bytes))
            sheet = st.selectbox("📑 Select Excel Sheet", xls.sheet_names, key="sheet_selector")
            st.session_state['selected_sheet'] = sheet
        except Exception as e:
            st.error(f"Could not read Excel sheets: {e}")

    try:
        sheet_name = st.session_state.get('selected_sheet')
        result = read_file(file_bytes, file_name, sheet_name=sheet_name)
        st.session_state['ingestion_result'] = result

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#ECFDF5 0%,#F0FDF4 100%); border:1px solid #A7F3D0; border-radius:12px; padding:14px 18px; margin:16px 0; display:flex; align-items:center; gap:12px;">
            <div style="width:36px; height:36px; background:#10B981; border-radius:10px; display:flex; align-items:center; justify-content:center; color:white; font-size:18px;">✓</div>
            <div>
                <div style="font-weight:700; color:#065F46;">Loaded {file_name}</div>
                <div style="font-size:12px; color:#047857;">{result.metadata['rows']} rows • {result.metadata['columns']} cols • {result.metadata['memory_usage_human']} • {result.metadata['file_type']} • Encoding {result.metadata['encoding']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        m = result.metadata
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: st.metric("📄 File", m['file_name'][:18])
        with c2: st.metric("📊 Rows", f"{m['rows']:,}")
        with c3: st.metric("📋 Columns", m['columns'])
        with c4: st.metric("💾 Memory", m['memory_usage_human'])
        with c5: st.metric("🏷️ Type", m['file_type'])

        with st.expander("👀 Preview first 100 rows", expanded=True):
            st.dataframe(result.preview, use_container_width=True)

        with st.expander("🔍 Column Detection Preview"):
            st.write(f"**Excel sheets:** {m.get('excel_sheets', [])}")
            st.write(f"**Encoding detected:** {m.get('encoding')}")
            st.write(f"**File hash (reproducibility):** {m.get('file_hash')}")
            st.json({k: v for k,v in m.items() if k not in ['excel_sheets']})

        if st.button("⚙️ Run Full Profiling & Analysis →", type="primary", use_container_width=True):
            with st.spinner("🔬 Profiling columns → Quality audit 0-100 → EDA → KPIs → Stats → Insights... This may take 10-30 sec"):
                pipeline_result = run_full_pipeline(result.df, result.metadata, app_version="0.1.0")
                st.session_state['pipeline_result'] = pipeline_result
                st.session_state['current_step'] = 2
                st.switch_page("pages/02_Profiling.py")

    except Exception as e:
        st.error(f"❌ Failed to load file: {e}")

else:
    st.markdown("""
    <div style="background:#F8FAFC; border:1px dashed #CBD5E1; border-radius:16px; padding:24px; text-align:center; margin-top:16px;">
        <div style="font-size:32px; margin-bottom:12px;">📂</div>
        <div style="font-weight:700; font-size:14px; color:#334155; margin-bottom:8px;">No dataset yet — upload or try demo above</div>
        <div style="font-size:12px; color:#64748B; line-height:1.6; max-width:500px; margin:0 auto;">
            <b>Supported:</b> CSV, XLSX, XLS, JSON, Parquet<br>
            <b>Max size:</b> 200MB MVP — sampling for larger files in production would use Polars + chunking<br>
            <b>Security:</b> File validated for extension, size, magic bytes. No arbitrary code exec. PII detection active (only object columns, conservative). Data stays in memory.
        </div>
    </div>
    """, unsafe_allow_html=True)
