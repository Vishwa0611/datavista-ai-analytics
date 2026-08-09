"""
Page 2 — Profiling — Enhanced Attractive
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
from app.ui.layout import apply_custom_css
from app.components.sidebar import render_sidebar

st.set_page_config(page_title="Profiling — DataVista", layout="wide")
apply_custom_css()
render_sidebar(current_page_file="pages/02_Profiling.py")

st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <div style="width:40px; height:40px; background:linear-gradient(135deg,#6366F1,#8B5CF6); border-radius:12px; display:flex; align-items:center; justify-content:center; color:white; font-size:20px;">🔍</div>
    <div>
        <div style="font-size:24px; font-weight:800; letter-spacing:-0.02em;">Dataset Profiling</div>
        <div style="font-size:12px; color:#64748B; font-weight:500;">Step 2/9 • Understanding your data before analysis • Domain detection adapts KPIs</div>
    </div>
</div>
""", unsafe_allow_html=True)

if 'pipeline_result' not in st.session_state or not st.session_state['pipeline_result']:
    st.warning("No dataset loaded. Go to Upload page.")
    if st.button("Go to Upload"):
        st.switch_page("pages/01_Upload.py")
    st.stop()

result = st.session_state['pipeline_result']
profile = result['profile']
metadata = result['metadata']

# Top metrics — attractive cards
c1,c2,c3,c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="premium-card" style="text-align:center;">
        <div style="font-size:11px; font-weight:700; color:#64748B; letter-spacing:0.08em;">ROWS</div>
        <div style="font-size:28px; font-weight:800; margin:6px 0; letter-spacing:-0.02em;">{profile.row_count:,}</div>
        <div style="font-size:11px; color:#6366F1; font-weight:600;">100% profiled</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="premium-card" style="text-align:center;">
        <div style="font-size:11px; font-weight:700; color:#64748B; letter-spacing:0.08em;">COLUMNS</div>
        <div style="font-size:28px; font-weight:800; margin:6px 0; letter-spacing:-0.02em;">{profile.column_count}</div>
        <div style="font-size:11px; color:#10B981; font-weight:600;">{len(profile.numeric_cols)} num • {len(profile.categorical_cols)} cat</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="premium-card" style="text-align:center;">
        <div style="font-size:11px; font-weight:700; color:#64748B; letter-spacing:0.08em;">MEMORY</div>
        <div style="font-size:28px; font-weight:800; margin:6px 0; letter-spacing:-0.02em;">{profile.memory_usage_mb}</div>
        <div style="font-size:11px; color:#64748B; font-weight:600;">MB • {metadata.get('encoding','utf-8')}</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    score = result['quality'].score
    color = "#10B981" if score>=90 else "#F59E0B" if score>=70 else "#EF4444"
    st.markdown(f"""
    <div class="premium-card" style="text-align:center; border-color:{color};">
        <div style="font-size:11px; font-weight:700; color:#64748B; letter-spacing:0.08em;">QUALITY SCORE</div>
        <div style="font-size:28px; font-weight:800; margin:6px 0; letter-spacing:-0.02em; color:{color};">{score}<span style="font-size:14px;">/100</span></div>
        <div style="font-size:11px; color:{color}; font-weight:600;">Next step →</div>
    </div>
    """, unsafe_allow_html=True)

# Domain detection — premium
st.markdown(f"""
<div style="background:linear-gradient(135deg,#EEF2FF 0%,#F5F3FF 100%); border:1px solid #C7D2FE; border-radius:16px; padding:20px; margin:16px 0;">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
        <div>
            <div style="font-size:11px; font-weight:700; letter-spacing:0.08em; color:#4338CA; margin-bottom:6px;">🎯 DOMAIN DETECTION • ADAPTS KPIs</div>
            <div style="font-size:20px; font-weight:800; letter-spacing:-0.02em; color:#111827;">Detected: <span style="background:#111827; color:white; padding:2px 10px; border-radius:999px; font-size:14px;">{profile.detected_domain.upper()}</span> <span style="font-size:12px; color:#6366F1; font-weight:600;">{profile.domain_confidence*100:.0f}% confidence</span></div>
            <div style="font-size:12px; color:#475569; margin-top:8px;">Matched: {profile.domain_keywords_matched} • Why it matters: E-com → AOV/Margin/Pareto • Marketing → CTR/ROAS/CPA • HR → Attrition/Tenure • SaaS → Churn/MRR</div>
        </div>
        <div style="background:white; border-radius:12px; padding:12px 16px; border:1px solid #C7D2FE; text-align:center;">
            <div style="font-size:24px;">{'🛒' if profile.detected_domain=='ecommerce' else '📣' if profile.detected_domain=='marketing' else '💳' if profile.detected_domain=='saas' else '👥' if profile.detected_domain=='hr' else '📊'}</div>
            <div style="font-size:11px; font-weight:700; color:#4338CA; margin-top:4px;">{profile.detected_domain}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Column classification — attractive metrics
st.markdown("#### 📊 Column Classification")
col1,col2,col3,col4,col5 = st.columns(5)
with col1:
    st.markdown(f"""
    <div class="premium-card" style="text-align:center; padding:16px;">
        <div style="width:36px; height:36px; background:#EEF2FF; border-radius:10px; display:flex; align-items:center; justify-content:center; margin:0 auto 8px; font-size:18px;">🔢</div>
        <div style="font-size:20px; font-weight:800;">{len(profile.numeric_cols)}</div>
        <div style="font-size:11px; color:#64748B; font-weight:600;">NUMERICAL</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="premium-card" style="text-align:center; padding:16px;">
        <div style="width:36px; height:36px; background:#ECFDF5; border-radius:10px; display:flex; align-items:center; justify-content:center; margin:0 auto 8px; font-size:18px;">🔤</div>
        <div style="font-size:20px; font-weight:800;">{len(profile.categorical_cols)}</div>
        <div style="font-size:11px; color:#64748B; font-weight:600;">CATEGORICAL</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="premium-card" style="text-align:center; padding:16px;">
        <div style="width:36px; height:36px; background:#FFFBEB; border-radius:10px; display:flex; align-items:center; justify-content:center; margin:0 auto 8px; font-size:18px;">📅</div>
        <div style="font-size:20px; font-weight:800;">{len(profile.datetime_cols)}</div>
        <div style="font-size:11px; color:#64748B; font-weight:600;">DATETIME</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="premium-card" style="text-align:center; padding:16px;">
        <div style="width:36px; height:36px; background:#F5F3FF; border-radius:10px; display:flex; align-items:center; justify-content:center; margin:0 auto 8px; font-size:18px;">🆔</div>
        <div style="font-size:20px; font-weight:800;">{len(profile.id_cols)}</div>
        <div style="font-size:11px; color:#64748B; font-weight:600;">ID COLUMNS</div>
    </div>
    """, unsafe_allow_html=True)
with col5:
    st.markdown(f"""
    <div class="premium-card" style="text-align:center; padding:16px; border-color:{'#FECACA' if profile.pii_cols else '#E2E8F0'};">
        <div style="width:36px; height:36px; background:{'#FEF2F2' if profile.pii_cols else '#F8FAFC'}; border-radius:10px; display:flex; align-items:center; justify-content:center; margin:0 auto 8px; font-size:18px;">🛡️</div>
        <div style="font-size:20px; font-weight:800;">{len(profile.pii_cols)}</div>
        <div style="font-size:11px; color:#64748B; font-weight:600;">PII</div>
    </div>
    """, unsafe_allow_html=True)

if profile.pii_cols:
    st.warning(f"🛡️ Potential PII detected in: {', '.join(profile.pii_cols)} — not sent to external AI without consent. Review handling.")

# Detailed table — enhanced
st.markdown("#### 📋 Column Details")
rows = []
for col in profile.columns:
    type_emoji = {"numerical":"🔢", "categorical":"🔤", "datetime":"📅", "id":"🆔", "pii":"🛡️", "constant":"📌", "boolean":"☑️"}.get(col.inferred_type, "📄")
    rows.append({
        "Column": f"{type_emoji} {col.name}",
        "Type": col.inferred_type,
        "Unique": col.unique_count,
        "Unique %": f"{col.unique_ratio*100:.1f}%",
        "Missing %": f"{col.missing_pct}%",
        "Sample": ", ".join(map(str, col.sample_values[:2]))
    })
df_display = pd.DataFrame(rows)
st.dataframe(df_display, use_container_width=True, height=380)

# Expanders with icons
with st.expander("🔢 Numerical Columns — histograms, box plots, correlation"):
    st.write(profile.numeric_cols)
    if profile.numeric_cols:
        st.markdown(f"<span class='badge badge-indigo'>{len(profile.numeric_cols)} columns → will show distribution + outliers</span>", unsafe_allow_html=True)

with st.expander("🔤 Categorical — bar charts, Pareto, segmentation"):
    st.write(profile.categorical_cols)

with st.expander("📅 Date — trend, MoM/YoY, rolling"):
    st.write(profile.datetime_cols)

with st.expander("🆔 ID — treated as ID, not for bar charts"):
    st.write(profile.id_cols)

c1,c2 = st.columns(2)
with c1:
    if st.button("✅ Continue to Data Quality →", type="primary", use_container_width=True):
        st.switch_page("pages/03_Data_Quality.py")
with c2:
    if st.button("← Back to Upload", use_container_width=True):
        st.switch_page("pages/01_Upload.py")
