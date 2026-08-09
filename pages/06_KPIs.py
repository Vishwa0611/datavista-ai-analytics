"""
Page 6 — KPIs — Enhanced Attractive
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from app.ui.layout import apply_custom_css
from app.components.sidebar import render_sidebar

st.set_page_config(page_title="KPIs — DataVista", layout="wide")
apply_custom_css()
render_sidebar(current_page_file="pages/06_KPIs.py")

st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <div style="width:40px; height:40px; background:linear-gradient(135deg,#8B5CF6,#6366F1); border-radius:12px; display:flex; align-items:center; justify-content:center; color:white; font-size:20px;">🎯</div>
    <div>
        <div style="font-size:24px; font-weight:800; letter-spacing:-0.02em;">Business KPI Analysis</div>
        <div style="font-size:12px; color:#64748B; font-weight:500;">Step 6/9 • Domain-aware • Formula explained • Interpretation in business language • Only if columns exist</div>
    </div>
</div>
""", unsafe_allow_html=True)

if 'pipeline_result' not in st.session_state or not st.session_state['pipeline_result']:
    st.warning("No dataset")
    st.switch_page("pages/01_Upload.py")
    st.stop()

result = st.session_state['pipeline_result']
kpi_data = result.get('kpi', {})
profile = result['profile']

if not kpi_data:
    st.warning("KPI data not available")
    st.stop()

st.markdown(f"""
<div style="background:linear-gradient(135deg,#F5F3FF 0%,#EEF2FF 100%); border:1px solid #C7D2FE; border-radius:16px; padding:16px 20px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;">
    <div>
        <div style="font-size:11px; font-weight:700; letter-spacing:0.08em; color:#4338CA;">DETECTED DOMAIN</div>
        <div style="font-size:18px; font-weight:800; margin-top:4px;">{kpi_data.get('detected_domain').upper()} <span style="font-size:12px; color:#6366F1; font-weight:600;">• {kpi_data.get('summary')}</span></div>
    </div>
    <div style="background:white; padding:8px 14px; border-radius:999px; border:1px solid #C7D2FE; font-size:12px; font-weight:700; color:#4338CA;">{kpi_data.get('available_count')}/{kpi_data.get('total_count')} KPIs</div>
</div>
""", unsafe_allow_html=True)

kpis = kpi_data.get('kpis', [])
available_kpis = [k for k in kpis if k.available]
unavailable = [k for k in kpis if not k.available]

cols = st.columns(2)
for idx, kpi in enumerate(available_kpis):
    with cols[idx % 2]:
        # Color by unit
        icon = "💰" if kpi.unit=="currency" else "📈" if kpi.unit=="percent" else "🔢" if kpi.unit=="count" else "📊"
        bg = "#ECFDF5" if kpi.unit=="currency" else "#FFFBEB" if kpi.unit=="percent" else "#F5F3FF"
        st.markdown(f"""
        <div class="premium-card">
            <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:12px;">
                <div style="display:flex; gap:10px; align-items:center;">
                    <div style="width:40px; height:40px; background:{bg}; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:20px;">{icon}</div>
                    <div>
                        <div style="font-weight:800; font-size:14px; letter-spacing:-0.01em;">{kpi.name}</div>
                        <div style="font-size:11px; color:#64748B; font-family:JetBrains Mono;">{kpi.formula}</div>
                    </div>
                </div>
                <span class="badge badge-indigo">{kpi.unit}</span>
            </div>
            <div style="background:#F8FAFC; border-radius:12px; padding:14px; margin-bottom:12px; text-align:center;">
                <div style="font-size:11px; color:#64748B; font-weight:600; letter-spacing:0.05em;">VALUE</div>
                <div style="font-size:28px; font-weight:900; letter-spacing:-0.03em; color:#111827; margin-top:4px;">{f"{kpi.value:,.2f}" if isinstance(kpi.value,float) else kpi.value}{'%' if kpi.unit=='percent' else ''}</div>
            </div>
            <div style="font-size:11px; color:#94A3B8; font-weight:600; margin-bottom:4px;">CALCULATION</div>
            <div style="font-size:12px; color:#475569; background:#F8FAFC; padding:8px 10px; border-radius:8px; font-family:JetBrains Mono; margin-bottom:10px;">{kpi.calculation_details}</div>
            <div style="font-size:11px; color:#94A3B8; font-weight:600; margin-bottom:4px;">EVIDENCE</div>
            <div style="margin-bottom:10px;">{''.join([f"<span class='badge badge-gray' style='margin:2px;'>{col}</span>" for col in kpi.evidence_columns])}</div>
            <div style="background:#EEF2FF; border:1px solid #C7D2FE; border-radius:10px; padding:10px 12px;">
                <div style="font-size:11px; font-weight:700; color:#4338CA; margin-bottom:4px;">💡 INTERPRETATION</div>
                <div style="font-size:12px; color:#3730A3; line-height:1.5;">{kpi.interpretation}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

if unavailable:
    with st.expander(f"⚠️ {len(unavailable)} KPIs unavailable — missing columns"):
        for kpi in unavailable:
            st.caption(f"**{kpi.name}** — {kpi.reason_if_unavailable}")

import pandas as pd
rows = []
for kpi in kpis:
    rows.append({"KPI": kpi.name, "Formula": kpi.formula, "Value": kpi.value if kpi.available else "N/A", "Unit": kpi.unit, "Available": "✅" if kpi.available else "❌", "Interpretation": kpi.interpretation[:80]})
df_kpi = pd.DataFrame(rows)
st.markdown("#### 📋 KPI Summary Table")
st.dataframe(df_kpi, use_container_width=True)

c1,c2 = st.columns(2)
with c1:
    if st.button("📈 Continue to Statistics →", type="primary", use_container_width=True):
        st.switch_page("pages/07_Statistics.py")
with c2:
    if st.button("← Back to EDA", use_container_width=True):
        st.switch_page("pages/05_EDA.py")
