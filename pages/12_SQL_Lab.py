"""
Page 12 — SQL Lab — Enhanced Attractive
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from app.ui.layout import apply_custom_css
from app.components.sidebar import render_sidebar
from src.sql.engine import get_engine
from src.sql.query_generator import generate_showcase_queries
from src.sql.executor import safe_execute

st.set_page_config(page_title="SQL Lab — DataVista", layout="wide")
apply_custom_css()
render_sidebar(current_page_file="pages/12_SQL_Lab.py")

st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <div style="width:40px; height:40px; background:linear-gradient(135deg,#111827,#374151); border-radius:12px; display:flex; align-items:center; justify-content:center; color:white; font-size:20px;">🗄️</div>
    <div>
        <div style="font-size:24px; font-weight:800; letter-spacing:-0.02em;">SQL Lab — Demonstrate SQL Skills</div>
        <div style="font-size:12px; color:#64748B; font-weight:500;">CTEs, Window Functions RANK/LAG, GROUP BY, HAVING, CASE WHEN, DATE_TRUNC — interview-ready • 60% JDs require SQL</div>
    </div>
</div>
""", unsafe_allow_html=True)

if 'pipeline_result' not in st.session_state or not st.session_state['pipeline_result']:
    st.warning("No dataset")
    st.switch_page("pages/01_Upload.py")
    st.stop()

result = st.session_state['pipeline_result']
profile = result['profile']
df = result['df_cleaned']

if 'duckdb_engine' not in st.session_state:
    engine = get_engine()
    engine.register_table("raw_data", result['df_original'])
    engine.register_table("cleaned_data", df)
    st.session_state['duckdb_engine'] = engine
else:
    engine = st.session_state['duckdb_engine']

queries = generate_showcase_queries(df, table_name="cleaned_data", numeric_cols=profile.numeric_cols, categorical_cols=profile.categorical_cols, date_cols=profile.datetime_cols)

st.markdown(f"""
<div style="background:white; border:1px solid #E2E8F0; border-radius:14px; padding:16px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;">
    <div><b>📚 Showcase Queries</b> — {len(queries)} examples covering required SQL skills • Copy for interview</div>
    <span class="badge badge-black">SQL 60% JDs</span>
</div>
""", unsafe_allow_html=True)

categories = list(set([q['category'] for q in queries]))
selected_cat = st.multiselect("Filter by category", categories, default=categories)

for q in queries:
    if q['category'] not in selected_cat:
        continue
    with st.container():
        c1,c2 = st.columns([3,1])
        with c1:
            st.markdown(f"""
            <div style="display:flex; gap:8px; align-items:center; margin-bottom:8px;">
                <span class="badge badge-indigo">{q['category']}</span>
                <span style="font-weight:700; font-size:14px;">{q['title']}</span>
            </div>
            <div style="font-size:12px; color:#475569; margin-bottom:8px;">{q['description']}</div>
            """, unsafe_allow_html=True)
            st.code(q['sql'], language="sql")
        with c2:
            if st.button(f"▶️ Run", key=f"run_{q['title']}", use_container_width=True):
                exec_res = engine.execute(q['sql'])
                if exec_res['success']:
                    st.dataframe(exec_res['df'], use_container_width=True)
                    st.success(f"{exec_res['df'].shape[0]} rows")
                else:
                    st.error(exec_res['error'])

st.divider()
st.markdown("#### ✏️ Custom SQL — Only SELECT allowed, safe execution")
st.caption("Whitelist: raw_data, cleaned_data • Blocked: DROP, DELETE, INSERT, UPDATE, ALTER • Limit 5000 rows")

custom_sql = st.text_area("Write your SQL (SELECT only):", height=140, placeholder="SELECT category, SUM(revenue) as total FROM cleaned_data GROUP BY category ORDER BY total DESC LIMIT 10;")

if st.button("▶️ Execute Custom SQL", type="primary", use_container_width=True):
    if custom_sql.strip():
        res = safe_execute(engine, custom_sql)
        if res['success']:
            st.success(f"✅ Returned {res['df'].shape[0]} rows")
            st.dataframe(res['df'], use_container_width=True)
        else:
            st.error(f"❌ Error: {res['error']}")
    else:
        st.warning("Enter SQL first")

with st.expander("🔍 View Table Schema"):
    for tbl in ["raw_data","cleaned_data"]:
        st.markdown(f"**📋 {tbl}**")
        schema = engine.get_schema(tbl)
        if schema is not None:
            st.dataframe(schema, use_container_width=True)

c1,c2 = st.columns(2)
with c1:
    if st.button("📄 Continue to Report →", type="primary", use_container_width=True):
        st.switch_page("pages/13_Report.py")
with c2:
    if st.button("← Back to Ask Data", use_container_width=True):
        st.switch_page("pages/11_Ask_Data.py")
