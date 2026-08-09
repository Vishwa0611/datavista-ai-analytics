"""
Page 3 — Data Quality — Enhanced Attractive
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px
from app.ui.layout import apply_custom_css
from app.components.sidebar import render_sidebar

st.set_page_config(page_title="Data Quality — DataVista", layout="wide")
apply_custom_css()
render_sidebar(current_page_file="pages/03_Data_Quality.py")

st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <div style="width:40px; height:40px; background:linear-gradient(135deg,#10B981,#059669); border-radius:12px; display:flex; align-items:center; justify-content:center; color:white; font-size:20px;">✅</div>
    <div>
        <div style="font-size:24px; font-weight:800; letter-spacing:-0.02em;">Data Quality Audit</div>
        <div style="font-size:12px; color:#64748B; font-weight:500;">Step 3/9 • Professional audit with 0-100 score, not just missing % • Weighted: Completeness 40%, Uniqueness 20%, Validity 20%, Consistency 20%</div>
    </div>
</div>
""", unsafe_allow_html=True)

if 'pipeline_result' not in st.session_state or not st.session_state['pipeline_result']:
    st.warning("No dataset loaded.")
    if st.button("Go to Upload"):
        st.switch_page("pages/01_Upload.py")
    st.stop()

result = st.session_state['pipeline_result']
quality = result['quality']
profile = result['profile']

# Score hero — attractive
c1,c2 = st.columns([1.2,2])
with c1:
    score = quality.score
    if score >=90:
        color_bg = "#ECFDF5"
        color_border = "#A7F3D0"
        color_text = "#065F46"
        emoji = "🌟"
        label = "Excellent"
    elif score >=70:
        color_bg = "#FFFBEB"
        color_border = "#FDE68A"
        color_text = "#92400E"
        emoji = "👍"
        label = "Good"
    else:
        color_bg = "#FEF2F2"
        color_border = "#FECACA"
        color_text = "#991B1B"
        emoji = "⚠️"
        label = "Needs Attention"

    st.markdown(f"""
    <div style="background:{color_bg}; border:2px solid {color_border}; border-radius:20px; padding:24px; text-align:center;">
        <div style="font-size:12px; font-weight:700; letter-spacing:0.1em; color:{color_text};">QUALITY SCORE</div>
        <div style="font-size:56px; font-weight:900; letter-spacing:-0.04em; color:{color_text}; line-height:1; margin:12px 0;">{score}<span style="font-size:20px; font-weight:600;">/100</span></div>
        <div style="display:inline-block; background:white; border:1px solid {color_border}; padding:4px 12px; border-radius:999px; font-size:12px; font-weight:700; color:{color_text};">{emoji} {label}</div>
        <div style="margin-top:16px; display:grid; grid-template-columns:1fr 1fr; gap:8px; text-align:left;">
            <div style="background:white; border-radius:10px; padding:10px; border:1px solid {color_border};">
                <div style="font-size:10px; color:#64748B; font-weight:600;">COMPLETENESS</div>
                <div style="font-weight:800; font-size:14px; color:#111827;">{quality.score_breakdown.get('completeness',0)}%</div>
                <div style="font-size:10px; color:#94A3B8;">40% weight</div>
            </div>
            <div style="background:white; border-radius:10px; padding:10px; border:1px solid {color_border};">
                <div style="font-size:10px; color:#64748B; font-weight:600;">UNIQUENESS</div>
                <div style="font-weight:800; font-size:14px; color:#111827;">{quality.score_breakdown.get('uniqueness',0)}%</div>
                <div style="font-size:10px; color:#94A3B8;">20% weight</div>
            </div>
            <div style="background:white; border-radius:10px; padding:10px; border:1px solid {color_border};">
                <div style="font-size:10px; color:#64748B; font-weight:600;">VALIDITY</div>
                <div style="font-weight:800; font-size:14px; color:#111827;">{quality.score_breakdown.get('validity',0)}%</div>
                <div style="font-size:10px; color:#94A3B8;">20% weight</div>
            </div>
            <div style="background:white; border-radius:10px; padding:10px; border:1px solid {color_border};">
                <div style="font-size:10px; color:#64748B; font-weight:600;">CONSISTENCY</div>
                <div style="font-weight:800; font-size:14px; color:#111827;">{quality.score_breakdown.get('consistency',0)}%</div>
                <div style="font-size:10px; color:#94A3B8;">20% weight</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("#### 🔍 Issues Feed — Detected / Potential / Requires Review")
    for issue in quality.issues[:12]:
        if issue.severity == 'info':
            bg = "#ECFDF5"; border = "#A7F3D0"; icon = "✅"; color = "#065F46"
        elif issue.severity == 'warning':
            bg = "#FFFBEB"; border = "#FDE68A"; icon = "⚠️"; color = "#92400E"
        else:
            bg = "#FEF2F2"; border = "#FECACA"; icon = "🔴"; color = "#991B1B"
        st.markdown(f"""
        <div style="background:{bg}; border:1px solid {border}; border-radius:12px; padding:12px 16px; margin-bottom:8px; display:flex; gap:10px; align-items:start;">
            <div style="font-size:16px;">{icon}</div>
            <div style="flex:1;">
                <div style="font-weight:600; font-size:13px; color:{color};">{issue.label} {f'• {issue.column}' if issue.column else ''}</div>
                <div style="font-size:12px; color:#475569; margin-top:2px;">{issue.description}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Tabs — enhanced
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Missing", "👯 Duplicates", "📦 Outliers", "🔤 Consistency", "🛡️ Validity"])

with tab1:
    st.markdown("#### Missing Values — Completeness 40% weight")
    c1,c2 = st.columns([1,1.5])
    with c1:
        st.metric("Total Missing Cells", f"{quality.missing.total_missing_cells:,}")
        st.metric("Missing %", f"{quality.missing.missing_pct}%")
        st.metric("Total Cells", f"{quality.missing.total_cells:,}")
    with c2:
        missing_df = pd.DataFrame([
            {"column": col, "missing_pct": info["pct"], "count": info["count"]}
            for col, info in quality.missing.per_column.items() if info["pct"]>0
        ])
        if not missing_df.empty:
            fig = px.bar(missing_df.sort_values("missing_pct", ascending=False), x="column", y="missing_pct", title="Missing % by Column (Top Issues)", color_discrete_sequence=["#F59E0B"])
            fig.update_layout(template="plotly_white", height=320, margin=dict(l=20,r=20,t=40,b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("""
            <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-radius:12px; padding:20px; text-align:center;">
                <div style="font-size:32px;">✨</div>
                <div style="font-weight:700; color:#065F46; margin-top:8px;">No missing values — excellent!</div>
                <div style="font-size:12px; color:#047857; margin-top:4px;">100% complete • 40% weight maxed</div>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    c1,c2 = st.columns(2)
    with c1:
        st.metric("Duplicate Rows", quality.duplicates.duplicate_row_count)
        st.metric("Duplicate %", f"{quality.duplicates.duplicate_pct}%")
    with c2:
        st.markdown("**Duplicate ID Columns:**")
        st.json(quality.duplicates.duplicate_id_cols)
    if quality.duplicates.sample_duplicates is not None and not quality.duplicates.sample_duplicates.empty:
        st.markdown("**Sample Duplicate Rows:**")
        st.dataframe(quality.duplicates.sample_duplicates, use_container_width=True)
    else:
        st.success("✅ No full duplicate rows detected — uniqueness 100%")

with tab3:
    st.markdown("#### Outliers — IQR Method (Q1-1.5IQR, Q3+1.5IQR)")
    st.caption("Potential outliers, not automatically removed — review manually. Shows data quality, not errors necessarily.")
    if quality.outliers.per_column:
        outlier_df = pd.DataFrame([
            {"column": col, "count": info["count"], "pct": info["pct"], "lower": round(info["lower"],2), "upper": round(info["upper"],2)}
            for col, info in quality.outliers.per_column.items()
        ])
        st.dataframe(outlier_df, use_container_width=True)
        st.metric("Total rows affected by outliers", quality.outliers.total_outlier_rows)
        from src.visualization.charts import create_box_plot
        df = result['df_cleaned']
        cols = st.columns(3)
        for idx, col in enumerate(list(quality.outliers.per_column.keys())[:3]):
            with cols[idx]:
                fig = create_box_plot(df, col)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No outliers detected via IQR")

with tab4:
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("**Blank Strings:**")
        st.json(quality.consistency.blank_string_counts)
        st.markdown("**Whitespace Issues:**")
        st.json(quality.consistency.whitespace_counts)
        st.markdown("**Constant Columns:**")
        st.json(quality.consistency.constant_columns)
    with c2:
        st.markdown("**High Cardinality:**")
        st.json(quality.consistency.high_cardinality_columns)
        st.markdown("**Inconsistent Labels (US vs us):**")
        st.json(quality.consistency.inconsistent_labels)

with tab5:
    st.markdown("#### Validity — Suspicious Values")
    validity_issues = [i for i in quality.issues if "negative" in i.description.lower() or "impossible" in i.description.lower()]
    if validity_issues:
        for iss in validity_issues:
            st.warning(f"⚠️ {iss.description}")
    else:
        st.markdown("""
        <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-radius:12px; padding:20px; text-align:center;">
            <div style="font-size:24px;">🛡️</div>
            <div style="font-weight:700; color:#065F46;">No validity issues — no negatives where >=0 expected</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()
c1,c2 = st.columns(2)
with c1:
    if st.button("🧹 Go to Cleaning → Transform with Log", type="primary", use_container_width=True):
        st.switch_page("pages/04_Cleaning.py")
with c2:
    if st.button("← Back to Profiling", use_container_width=True):
        st.switch_page("pages/02_Profiling.py")
