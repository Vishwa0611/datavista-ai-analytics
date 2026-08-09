"""
Page 10 — AI Insights — Enhanced Attractive
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from app.ui.layout import apply_custom_css
from app.components.sidebar import render_sidebar
from src.ai.llm_wrapper import build_metrics_context, call_llm_if_configured

st.set_page_config(page_title="AI Insights — DataVista", layout="wide")
apply_custom_css()
render_sidebar(current_page_file="pages/10_AI_Insights.py")

st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <div style="width:40px; height:40px; background:linear-gradient(135deg,#8B5CF6,#EC4899); border-radius:12px; display:flex; align-items:center; justify-content:center; color:white; font-size:20px;">🤖</div>
    <div>
        <div style="font-size:24px; font-weight:800; letter-spacing:-0.02em;">AI-Assisted Insights — Traceable, Not Hallucinated</div>
        <div style="font-size:12px; color:#64748B; font-weight:500;">Findings backed by calculated metrics • Every insight shows evidence • Finding → Evidence → Meaning → Action</div>
    </div>
</div>
<div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:12px; padding:12px 16px; margin:12px 0; display:flex; gap:10px; align-items:center;">
    <div style="font-size:20px;">⚠️</div>
    <div style="font-size:12px; color:#92400E;"><b>AI-generated interpretation — verify against underlying analysis.</b> Numbers from calculated metrics only, never invented. Traceable to KPI/stats.</div>
</div>
""", unsafe_allow_html=True)

if 'pipeline_result' not in st.session_state or not st.session_state['pipeline_result']:
    st.warning("No dataset")
    st.switch_page("pages/01_Upload.py")
    st.stop()

result = st.session_state['pipeline_result']
insights = result.get('insights', [])

severity_filter = st.multiselect("Filter by severity", ["critical","warning","info"], default=["critical","warning","info"])

filtered = [ins for ins in insights if ins.severity in severity_filter]

if not filtered:
    st.info("No insights matching filter")
else:
    st.markdown(f"#### 💡 Top Findings — {len(filtered)} insights (sorted critical first)")
    for ins in filtered:
        if ins.severity == "critical":
            bg = "#FEF2F2"; border = "#FECACA"; icon = "🔴"; color = "#991B1B"; badge = "badge-red"
        elif ins.severity == "warning":
            bg = "#FFFBEB"; border = "#FDE68A"; icon = "⚠️"; color = "#92400E"; badge = "badge-amber"
        else:
            bg = "#EEF2FF"; border = "#C7D2FE"; icon = "ℹ️"; color = "#4338CA"; badge = "badge-indigo"

        st.markdown(f"""
        <div style="background:{bg}; border:1px solid {border}; border-left:4px solid {color}; border-radius:14px; padding:18px; margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:10px;">
                <div style="font-weight:800; font-size:14px; color:{color};">{icon} {ins.finding}</div>
                <span class="badge {badge}">{ins.severity}</span>
            </div>
            <div style="background:white; border-radius:10px; padding:12px; margin-bottom:10px;">
                <div style="font-size:11px; font-weight:700; color:#64748B; letter-spacing:0.05em; margin-bottom:4px;">📊 EVIDENCE (actual calc)</div>
                <div style="font-size:12px; color:#334155; font-family:JetBrains Mono; background:#F8FAFC; padding:8px; border-radius:6px;">{ins.evidence}</div>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
                <div>
                    <div style="font-size:11px; font-weight:700; color:#64748B; margin-bottom:4px;">🧠 BUSINESS MEANING</div>
                    <div style="font-size:12px; color:#475569; line-height:1.5;">{ins.business_meaning}</div>
                </div>
                <div>
                    <div style="font-size:11px; font-weight:700; color:#065F46; margin-bottom:4px;">✅ RECOMMENDATION</div>
                    <div style="font-size:12px; color:#065F46; line-height:1.5; background:#ECFDF5; padding:8px; border-radius:8px; border:1px solid #A7F3D0;">{ins.recommendation}</div>
                </div>
            </div>
            <div style="margin-top:12px; display:flex; gap:8px; flex-wrap:wrap;">
                <span class="badge badge-gray">Source: {ins.source}</span>
                <span class="badge badge-gray">Confidence: {ins.confidence}</span>
                <span class="badge badge-gray">Type: {ins.type}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.markdown("### 🤖 Optional LLM Interpretation Layer (With Guardrails)")
st.caption("Deterministic engine above is primary. LLM wrapper optional, sends ONLY aggregated metrics (no raw PII rows), prompt: 'Only use provided numbers, never invent'")

metrics_context = build_metrics_context(result)
with st.expander("🔍 View Safe Metrics Context (Sent to LLM, if enabled)"):
    st.json(metrics_context)

llm_question = st.text_input("💬 Ask AI about this dataset (uses only metrics context)", placeholder="What are biggest risks? Which region underperforming? What should management focus?")

if llm_question:
    with st.spinner("🤖 Calling LLM with guardrails..."):
        llm_result = call_llm_if_configured(llm_question, metrics_context)
        if not llm_result.get('available'):
            st.info(f"LLM not available: {llm_result.get('reason')} — Deterministic insights above still valid.")
        else:
            st.success(f"LLM Response (provider: {llm_result.get('provider')}):")
            st.markdown(llm_result.get('response'))

c1,c2 = st.columns(2)
with c1:
    if st.button("💬 Continue to Ask Your Data →", type="primary", use_container_width=True):
        st.switch_page("pages/11_Ask_Data.py")
with c2:
    if st.button("← Back to Time Series", use_container_width=True):
        st.switch_page("pages/09_TimeSeries.py")
