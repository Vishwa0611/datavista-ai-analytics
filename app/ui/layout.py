"""
Layout helpers.
"""
import streamlit as st
from .theme import CUSTOM_CSS

def apply_custom_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def render_header(title: str, subtitle: str = None):
    st.title(title)
    if subtitle:
        st.caption(subtitle)

def render_stepper(current_step: int, total_steps: int = 9):
    steps = ["Upload", "Profile", "Quality", "Clean", "EDA", "KPIs", "Stats", "Insights", "Report"]
    cols = st.columns(len(steps))
    for idx, step_name in enumerate(steps):
        step_num = idx + 1
        if step_num < current_step:
            label = f"✓ {step_name}"
            badge = "step-done"
        elif step_num == current_step:
            label = f"● {step_name}"
            badge = "step-active"
        else:
            label = step_name
            badge = "step-todo"
        with cols[idx]:
            st.markdown(f"<div class='step {badge}'>{label}</div>", unsafe_allow_html=True)

def render_quality_badge(score: int):
    if score >= 90:
        color = "green"
        text = f"{score}/100 — Excellent"
    elif score >= 70:
        color = "amber"
        text = f"{score}/100 — Good"
    else:
        color = "red"
        text = f"{score}/100 — Needs Attention"
    st.markdown(f"<span class='badge badge-{color}'>{text}</span>", unsafe_allow_html=True)
