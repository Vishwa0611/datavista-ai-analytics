"""
File uploader component with demo mode.
"""
import streamlit as st
import io
from ...src.ingestion.loader import read_file
from ...src.ingestion.sample_loader import get_sample_list
from ...src.ingestion.sample_loader import get_sample_path

def render_uploader():
    st.markdown("### Upload Dataset")
    st.caption("CSV, XLSX, XLS, JSON, Parquet • Up to 200MB • Encoding auto-detected • Your data stays in memory")

    # Demo selector
    st.markdown("#### Try Demo Dataset — No Upload Needed")
    samples = get_sample_list()
    cols = st.columns(len(samples))
    for idx, sample in enumerate(samples):
        with cols[idx]:
            with st.container():
                st.markdown(f"**{sample['title']}**")
                st.caption(sample['description'])
                st.caption(f"Rows: {sample['rows']} | Domain: {sample['domain']}")
                if st.button(f"Load {sample['id']}", key=f"demo_{sample['id']}", use_container_width=True):
                    st.session_state['demo_dataset'] = sample['id']
                    st.rerun()

    st.divider()
    uploaded = st.file_uploader("Drag and drop or browse", type=['csv','xlsx','xls','json','parquet'], accept_multiple_files=False)

    # Check for demo
    if 'demo_dataset' in st.session_state and st.session_state['demo_dataset']:
        demo_id = st.session_state['demo_dataset']
        path = get_sample_path(demo_id)
        with open(path, 'rb') as f:
            file_bytes = f.read()
        st.session_state['uploaded_file_bytes'] = file_bytes
        st.session_state['uploaded_file_name'] = f"{demo_id}.csv"
        st.session_state['demo_dataset'] = None  # clear after load
        st.success(f"Loaded demo dataset: {demo_id}")
        st.rerun()

    if uploaded:
        file_bytes = uploaded.read()
        st.session_state['uploaded_file_bytes'] = file_bytes
        st.session_state['uploaded_file_name'] = uploaded.name

    # If file exists in session
    if 'uploaded_file_bytes' in st.session_state and st.session_state['uploaded_file_bytes']:
        file_bytes = st.session_state['uploaded_file_bytes']
        file_name = st.session_state['uploaded_file_name']

        # Handle Excel sheet selection
        if file_name.lower().endswith(('.xlsx', '.xls')):
            import pandas as pd
            try:
                xls = pd.ExcelFile(io.BytesIO(file_bytes))
                sheet = st.selectbox("Select Excel Sheet", xls.sheet_names)
                st.session_state['selected_sheet'] = sheet
            except Exception as e:
                st.error(f"Could not read Excel sheets: {e}")
                return None

        # Try to load
        try:
            sheet_name = st.session_state.get('selected_sheet')
            result = read_file(file_bytes, file_name, sheet_name=sheet_name)
            st.session_state['ingestion_result'] = result
            st.success(f"Loaded {file_name}: {result.metadata['rows']} rows, {result.metadata['columns']} cols, {result.metadata['memory_usage_human']}")

            # Show preview
            with st.expander("Preview first 100 rows", expanded=True):
                st.dataframe(result.preview, use_container_width=True)

            # File metadata cards
            m = result.metadata
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.metric("File", m['file_name'][:20])
            with c2: st.metric("Rows", m['rows'])
            with c3: st.metric("Columns", m['columns'])
            with c4: st.metric("Memory", m['memory_usage_human'])

            if st.button("Continue to Profiling →", type="primary"):
                st.session_state['current_step'] = 2
                st.switch_page("pages/02_Profiling.py")

            return result

        except Exception as e:
            st.error(f"Failed to load file: {e}")
            return None

    return None
