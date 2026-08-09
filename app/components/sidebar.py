"""
Reusable sidebar — easy navigation + back button + light theme
"""
import streamlit as st
from pathlib import Path

WORKFLOW_PAGES = [
    ("🏠 Home", "streamlit_app.py"),
    ("📤 Upload", "pages/01_Upload.py"),
    ("🔍 Profiling", "pages/02_Profiling.py"),
    ("✅ Quality", "pages/03_Data_Quality.py"),
    ("🧹 Cleaning", "pages/04_Cleaning.py"),
    ("📊 EDA", "pages/05_EDA.py"),
    ("🎯 KPIs", "pages/06_KPIs.py"),
    ("📈 Statistics", "pages/07_Statistics.py"),
    ("🧩 Segmentation", "pages/08_Segmentation.py"),
    ("⏱️ Time Series", "pages/09_TimeSeries.py"),
    ("🤖 AI Insights", "pages/10_AI_Insights.py"),
    ("💬 Ask Data", "pages/11_Ask_Data.py"),
    ("🗄️ SQL Lab", "pages/12_SQL_Lab.py"),
    ("📄 Report", "pages/13_Report.py"),
    ("🔄 Comparison", "pages/14_Comparison.py"),
]

def render_sidebar(current_page_file: str = None):
    with st.sidebar:
        # Logo — light premium, correct palette
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; padding:4px 0 14px 0; border-bottom:1px solid #F3F4F6; margin-bottom:14px;">
            <div style="width:34px; height:34px; background:linear-gradient(135deg,#6366F1 0%,#06B6D4 100%); border-radius:10px; display:flex; align-items:center; justify-content:center; color:white; font-weight:800; font-size:15px; font-family:Space Grotesk; box-shadow:0 2px 8px rgba(99,102,241,0.2);">DV</div>
            <div>
                <div style="font-weight:700; font-size:15px; letter-spacing:-0.02em; color:#111827;">DataVista</div>
                <div style="font-size:11px; color:#6B7280; font-weight:500;">AI Analytics</div>
            </div>
            <div style="margin-left:auto;">
                <div style="width:8px; height:8px; background:#10B981; border-radius:50%; box-shadow:0 0 0 3px #ECFDF5;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Dataset info
        if 'pipeline_result' in st.session_state and st.session_state['pipeline_result']:
            result = st.session_state['pipeline_result']
            profile = result.get('profile')
            quality = result.get('quality')
            metadata = result.get('metadata', {})
            st.markdown("**📦 Dataset**")
            with st.container():
                st.markdown(f"**{metadata.get('file_name','dataset')[:22]}**")
                if profile:
                    c1,c2 = st.columns(2)
                    with c1: st.metric("Rows", f"{profile.row_count:,}")
                    with c2: st.metric("Cols", profile.column_count)
                if quality:
                    dot_color = "#10B981" if quality.score>=90 else "#F59E0B" if quality.score>=70 else "#EF4444"
                    st.markdown(f"<div style='display:flex; align-items:center; gap:6px; font-size:12px;'><div style='width:8px; height:8px; background:{dot_color}; border-radius:50%;'></div>Quality {quality.score}/100 • {profile.detected_domain}</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown("**🧭 Navigation**")
        
        current_idx = 0
        if current_page_file:
            for idx, (label, path) in enumerate(WORKFLOW_PAGES):
                if path == current_page_file or path in current_page_file or current_page_file in path:
                    current_idx = idx
                    break
                if Path(path).name == Path(current_page_file).name:
                    current_idx = idx
                    break

        for idx, (label, path) in enumerate(WORKFLOW_PAGES):
            try:
                is_current = (idx == current_idx)
                if is_current:
                    st.markdown(f"""
                    <div style='background:#F3F4F6; border:1px solid #E5E7EB; border-radius:8px; padding:8px 10px; margin-bottom:4px; display:flex; align-items:center; gap:8px;'>
                        <div style='font-size:13px; font-weight:600; color:#111827;'>● {label}</div>
                        <div style='margin-left:auto; width:6px; height:6px; background:#6366F1; border-radius:50%;'></div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.page_link(path, label=label)
            except Exception:
                st.caption(f"{label}")

        st.divider()

        if current_idx > 0:
            prev_label, prev_path = WORKFLOW_PAGES[current_idx - 1]
            if st.button(f"← Back to {prev_label}", use_container_width=True):
                st.switch_page(prev_path)

        if current_idx < len(WORKFLOW_PAGES) - 1:
            next_label, next_path = WORKFLOW_PAGES[current_idx + 1]
            if 'pipeline_result' in st.session_state or current_idx < 2:
                if st.button(f"Next: {next_label} →", type="primary", use_container_width=True):
                    st.switch_page(next_path)

        st.divider()

        if st.button("🔄 Reset Dataset", use_container_width=True):
            for key in ['uploaded_file_bytes', 'uploaded_file_name', 'ingestion_result', 'pipeline_result', 'cleaning_result', 'selected_sheet', 'demo_dataset', 'current_step', 'duckdb_engine', 'ask_query', 'ask_history']:
                if key in st.session_state:
                    del st.session_state[key]
            st.switch_page("streamlit_app.py")

        st.markdown(f"""
        <div style="margin-top:16px; padding:12px; background:#F9FAFB; border:1px solid #F3F4F6; border-radius:10px;">
            <div style="font-size:11px; font-weight:600; color:#111827;">DataVista v0.2</div>
            <div style="font-size:11px; color:#6B7280; margin-top:4px;">Upload any CSV → get analysis<br>Built for analyst roles</div>
        </div>
        """, unsafe_allow_html=True)
