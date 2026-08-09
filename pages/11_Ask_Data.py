"""
Page 11 — Ask Your Data — Enhanced Attractive
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from app.ui.layout import apply_custom_css
from app.components.sidebar import render_sidebar
from src.ai.nl_to_sql import nl_to_sql_pipeline
from src.sql.engine import get_engine
from src.sql.executor import safe_execute
import pandas as pd

st.set_page_config(page_title="Ask Data — DataVista", layout="wide")
apply_custom_css()
render_sidebar(current_page_file="pages/11_Ask_Data.py")

st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <div style="width:40px; height:40px; background:linear-gradient(135deg,#10B981,#06B6D4); border-radius:12px; display:flex; align-items:center; justify-content:center; color:white; font-size:20px;">💬</div>
    <div>
        <div style="font-size:24px; font-weight:800; letter-spacing:-0.02em;">Ask Your Data — Natural Language to SQL</div>
        <div style="font-size:12px; color:#64748B; font-weight:500;">Type a question, get SQL + table + chart — safe, no arbitrary code execution, whitelist columns</div>
    </div>
</div>
""", unsafe_allow_html=True)

if 'pipeline_result' not in st.session_state or not st.session_state['pipeline_result']:
    st.warning("No dataset")
    st.switch_page("pages/01_Upload.py")
    st.stop()

result = st.session_state['pipeline_result']
df = result['df_cleaned']
profile = result['profile']

if 'duckdb_engine' not in st.session_state:
    engine = get_engine()
    engine.register_table("raw_data", result['df_original'])
    engine.register_table("cleaned_data", df)
    st.session_state['duckdb_engine'] = engine
else:
    engine = st.session_state['duckdb_engine']

with st.expander("📋 Available Columns — use these in questions", expanded=False):
    st.markdown(f"""
    <div style="display:flex; gap:8px; flex-wrap:wrap;">
        <div><b>🔢 Numeric:</b> {', '.join([f'<span class="badge badge-indigo">{c}</span>' for c in profile.numeric_cols])}</div>
    </div>
    <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;">
        <div><b>🔤 Categorical:</b> {', '.join([f'<span class="badge badge-green">{c}</span>' for c in profile.categorical_cols])}</div>
    </div>
    <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;">
        <div><b>📅 Date:</b> {', '.join([f'<span class="badge badge-amber">{c}</span>' for c in profile.datetime_cols])}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("#### 💡 Try these example questions:")
examples = ["Show monthly revenue", "Top 10 products by profit", "Compare regions by revenue", "Average order value by category", "Show revenue growth", "Count orders by payment method"]
cols = st.columns(3)
for idx, ex in enumerate(examples):
    with cols[idx % 3]:
        if st.button(f"💬 {ex}", key=f"ex_{idx}", use_container_width=True):
            st.session_state['ask_query'] = ex

query = st.text_input("💬 Ask your data:", value=st.session_state.get('ask_query',''), placeholder="e.g., Show monthly revenue, Top 10 customers by revenue")

if query:
    nl_result = nl_to_sql_pipeline(query, list(df.columns), table_name="cleaned_data", date_columns=profile.datetime_cols)

    if not nl_result['success']:
        st.markdown(f"""
        <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:12px; padding:16px;">
            <div style="font-weight:700; color:#991B1B;">⚠️ Could not understand query</div>
            <div style="font-size:12px; color:#B91C1C; margin-top:4px;">{nl_result['explanation']}</div>
            <div style="font-size:11px; color:#991B1B; margin-top:8px; font-family:JetBrains Mono;">Intent: {nl_result['intent']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-radius:12px; padding:12px 16px; margin:12px 0;">
            <div style="font-weight:700; color:#065F46; font-size:13px;">✅ Intent detected: {nl_result['explanation']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.code(nl_result['sql'], language="sql")

        exec_result = safe_execute(engine, nl_result['sql'], limit=5000)
        if not exec_result['success']:
            st.error(f"❌ Query execution failed: {exec_result['error']}")
        else:
            result_df = exec_result['df']
            st.markdown(f"""
            <div class="premium-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-weight:700;">📊 Results: {len(result_df)} rows</div>
                    <span class="badge badge-green">Safe execution • Limit 5000</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(result_df, use_container_width=True)

            try:
                if len(result_df.columns) >=2:
                    x_col = result_df.columns[0]
                    y_col = result_df.columns[1]
                    if 'month' in x_col.lower() or 'date' in x_col.lower() or 'period' in x_col.lower():
                        st.line_chart(result_df.set_index(x_col)[y_col])
                    else:
                        st.bar_chart(result_df.set_index(x_col)[y_col])
            except Exception as e:
                st.caption(f"Chart auto-generation skipped: {e}")

if 'ask_history' not in st.session_state:
    st.session_state['ask_history'] = []

if query and nl_result.get('success'):
    if query not in [h['query'] for h in st.session_state['ask_history']]:
        st.session_state['ask_history'].append({"query": query, "sql": nl_result['sql']})

with st.sidebar:
    st.markdown("**🕘 Query History**")
    for h in st.session_state['ask_history'][-8:]:
        st.caption(f"Q: {h['query']}")
        st.code(h['sql'], language="sql")

c1,c2 = st.columns(2)
with c1:
    if st.button("🗄️ Go to SQL Lab →", type="primary", use_container_width=True):
        st.switch_page("pages/12_SQL_Lab.py")
with c2:
    if st.button("← Back to AI Insights", use_container_width=True):
        st.switch_page("pages/10_AI_Insights.py")
