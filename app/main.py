"""
DataVista — Fullstack SaaS Design
Complete rebuild — Linear/Stripe/Vercel inspired, not AI-looking
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from app.ui.theme import CUSTOM_CSS
from app.components.sidebar import render_sidebar
from src.ingestion.sample_loader import get_sample_list

st.set_page_config(
    page_title="DataVista — AI Analytics",
    page_icon="◼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    if 'current_step' not in st.session_state:
        st.session_state['current_step'] = 1
    if 'uploaded_file_bytes' not in st.session_state:
        st.session_state['uploaded_file_bytes'] = None

    render_sidebar(current_page_file="streamlit_app.py")

    # FULLSTACK HEADER — custom, like Vercel
    st.markdown("""
    <div class="fullstack-header">
        <div style="display:flex; align-items:center; gap:16px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="width:28px; height:28px; background:#09090B; border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-weight:700; font-size:13px; font-family:Space Grotesk;">DV</div>
                <span style="font-weight:600; font-size:14px; letter-spacing:-0.02em;">DataVista</span>
                <span style="background:#F4F4F5; border:1px solid #E4E4E7; padding:2px 8px; border-radius:6px; font-size:10px; font-weight:600; letter-spacing:0.05em;">BETA</span>
            </div>
            <div style="height:20px; width:1px; background:#E4E4E7;"></div>
            <div style="font-size:13px; color:#71717A;">Analytics Workbench</div>
        </div>
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="font-size:12px; color:#6B7280;">v0.2 • Ready to use</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # HERO — fullstack bento with code preview
    st.markdown("""
    <div class="hero-fullstack">
        <div class="hero-grid"></div>
        <div class="hero-orb"></div>
        <div class="hero-orb-2"></div>
        <div class="hero-content">
            <div>
                <div style="display:inline-flex; align-items:center; gap:8px; background:#F4F4F5; border:1px solid #E4E4E7; padding:4px 12px; border-radius:999px; font-size:11px; font-weight:600; letter-spacing:0.02em; margin-bottom:20px;">
                    <span style="width:6px; height:6px; background:#10B981; border-radius:50%; display:inline-block;"></span>
                    NOW SUPPORTS 7 DOMAINS
                </div>
                <div class="hero-title">Turn CSVs into<br><span>dashboards & reports.</span></div>
                <div class="hero-subtitle">Upload any business file — sales, marketing, HR, sports. Get quality score, cleaning log, KPIs, stats and clear recommendations. No code, no AI hallucination, just your data.</div>
                <div class="hero-stats">
                    <div class="hero-stat">
                        <div class="hero-stat-icon">⚡</div>
                        <div><div style="font-weight:600; font-size:13px;">5 sec demo</div><div style="font-size:11px; color:#71717A;">No upload needed</div></div>
                    </div>
                    <div class="hero-stat">
                        <div class="hero-stat-icon">🛡️</div>
                        <div><div style="font-weight:600; font-size:13px;">0 hallucinated</div><div style="font-size:11px; color:#71717A;">Traceable only</div></div>
                    </div>
                </div>
            </div>
            <div style="background:#09090B; border-radius:16px; padding:16px; border:1px solid #27272A; box-shadow: 0 20px 40px rgba(0,0,0,0.15); font-family:JetBrains Mono; font-size:11px; color:#A1A1AA; line-height:1.6;">
                <div style="display:flex; gap:6px; margin-bottom:12px;"><div style="width:10px; height:10px; border-radius:50%; background:#EF4444;"></div><div style="width:10px; height:10px; border-radius:50%; background:#F59E0B;"></div><div style="width:10px; height:10px; border-radius:50%; background:#10B981;"></div></div>
                <div><span style="color:#71717A;">$</span> datavista --upload Superstore.csv</div>
                <div style="color:#E4E4E7;">→ Profiling 21 columns... <span style="color:#10B981;">done</span></div>
                <div style="color:#E4E4E7;">→ Quality: <span style="color:#6366F1;">99/100</span> no duplicates, 0 missing</div>
                <div style="color:#E4E4E7;">→ KPIs: Total Sales, Profit, AOV, Margin calculated</div>
                <div style="color:#E4E4E7;">→ Insights: <span style="color:#F59E0B;">122 at-risk</span> customers classified</div>
                <div style="color:#E4E4E7;">→ Report: <span style="color:#10B981;">Superstore_fixed_report.html</span> ready</div>
                <div style="margin-top:12px; background:#18181B; border-radius:8px; padding:10px; border:1px solid #27272A;">
                    <div style="color:#71717A; font-size:10px; letter-spacing:0.05em; margin-bottom:4px;">SELECTED INSIGHT</div>
                    <div style="color:white; font-size:12px;">Discount ↑ → Profit ↓ (r=-0.22, Spearman -0.54)</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # BENTO STATS — like Stripe dashboard
    st.markdown("""
    <div class="bento-grid">
        <div class="bento-card bento-4">
            <div class="bento-label">Analysis Coverage</div>
            <div class="bento-value">14 steps</div>
            <div class="bento-sub"><span class="bento-trend-up">● Complete flow</span> Upload → Report</div>
        </div>
        <div class="bento-card bento-4">
            <div class="bento-label">Domains Supported</div>
            <div class="bento-value">7 types</div>
            <div class="bento-sub"><span class="bento-trend-neutral">E-com, Marketing, HR, SaaS, Sports...</span></div>
        </div>
        <div class="bento-card bento-4">
            <div class="bento-label">Quality Engine</div>
            <div class="bento-value">0-100 score</div>
            <div class="bento-sub"><span class="bento-trend">Completeness 40% • Uniqueness 20% • Validity 20% • Consistency 20%</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # DEMO — bento style, not 3 equal cards
    st.markdown("#### Try sample — 1 click, no upload")
    b1,b2 = st.columns([2,1])
    samples = get_sample_list()
    
    with b1:
        # Large bento for ecommerce
        sample = samples[0]
        st.markdown(f"""
        <div class="demo-bento" style="border-color:#09090B;">
            <div class="demo-bento-header">
                <div style="display:flex; align-items:center; gap:12px;">
                    <div style="width:40px; height:40px; background:#09090B; border-radius:10px; display:flex; align-items:center; justify-content:center; color:white; font-size:20px;">🛒</div>
                    <div><div style="font-weight:700; font-size:14px; letter-spacing:-0.01em;">{sample['title']}</div><div style="font-size:11px; color:#71717A;">{sample['rows']} rows • {sample['domain']} • 7 KPIs • 99/100 quality</div></div>
                </div>
                <span class="badge badge-black">Recommended</span>
            </div>
            <div class="demo-bento-body">
                <div style="font-size:13px; color:#52525B; line-height:1.5; margin-bottom:16px;">{sample['description']} — Has intentional quality issues (7% missing, 12 dupes) to show quality features. Best for full demo.</div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; font-size:12px;">
                    <div style="background:#FAFAF9; border:1px solid #F4F4F5; border-radius:8px; padding:10px;"><div style="font-weight:600;">Sales & Profit</div><div style="color:#71717A;">KPIs calculated</div></div>
                    <div style="background:#FAFAF9; border:1px solid #F4F4F5; border-radius:8px; padding:10px;"><div style="font-weight:600;">Quality Score</div><div style="color:#71717A;">0-100 audit</div></div>
                </div>
            </div>
            <div class="demo-bento-footer">
                <span class="badge badge-gray">📊 21 cols</span>
                <span class="badge badge-gray">📅 Time series</span>
                <span class="badge badge-gray">🧩 RFM 793 customers</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Load {sample['id']} → Full demo", key="demo_ecom_large", type="primary", use_container_width=True):
            from src.ingestion.loader import read_file
            from src.ingestion.sample_loader import get_sample_path
            path = get_sample_path(sample['id'])
            with open(path, 'rb') as f:
                file_bytes = f.read()
            st.session_state['uploaded_file_bytes'] = file_bytes
            st.session_state['uploaded_file_name'] = f"{sample['id']}.csv"
            result = read_file(file_bytes, f"{sample['id']}.csv")
            st.session_state['ingestion_result'] = result
            from src.orchestrator.pipeline import run_full_pipeline
            pipeline_result = run_full_pipeline(result.df, result.metadata, app_version="0.1.0")
            st.session_state['pipeline_result'] = pipeline_result
            st.switch_page("pages/02_Profiling.py")

    with b2:
        for idx in [1,2]:
            sample = samples[idx]
            icon = ["📣","💳"][idx-1]
            st.markdown(f"""
            <div class="demo-bento" style="margin-bottom:16px;">
                <div class="demo-bento-header" style="padding:12px 16px;">
                    <div style="display:flex; align-items:center; gap:8px;"><div style="font-size:18px;">{icon}</div><div style="font-weight:600; font-size:13px;">{sample['title'].split()[0]}</div></div>
                    <span class="badge badge-gray">{sample['rows']} rows</span>
                </div>
                <div class="demo-bento-body" style="padding:16px;">
                    <div style="font-size:11px; color:#71717A; line-height:1.4;">{sample['description'][:70]}...</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Load {sample['id']}", key=f"demo_small_{sample['id']}", use_container_width=True):
                from src.ingestion.loader import read_file
                from src.ingestion.sample_loader import get_sample_path
                path = get_sample_path(sample['id'])
                with open(path, 'rb') as f:
                    file_bytes = f.read()
                st.session_state['uploaded_file_bytes'] = file_bytes
                st.session_state['uploaded_file_name'] = f"{sample['id']}.csv"
                result = read_file(file_bytes, f"{sample['id']}.csv")
                st.session_state['ingestion_result'] = result
                from src.orchestrator.pipeline import run_full_pipeline
                pipeline_result = run_full_pipeline(result.df, result.metadata, app_version="0.1.0")
                st.session_state['pipeline_result'] = pipeline_result
                st.switch_page("pages/02_Profiling.py")

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # FEATURES — bento asymmetric
    st.markdown("#### What you get — not just charts")
    st.markdown("""
    <div class="bento-grid">
        <div class="bento-card bento-6">
            <div style="display:flex; gap:12px; align-items:start;">
                <div style="width:36px; height:36px; background:#F4F4F5; border:1px solid #E4E4E7; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">🔍</div>
                <div>
                    <div style="font-weight:600; font-size:14px; margin-bottom:4px;">Data quality, not just missing %</div>
                    <div style="font-size:13px; color:#52525B; line-height:1.5;">Score 0-100 with breakdown: Completeness 40%, Record Uniqueness 20%, Validity 20%, Consistency 20%. Finds duplicates, outliers via IQR (flagged as anomaly, not error), blank spaces, inconsistent labels like US vs us.</div>
                </div>
            </div>
        </div>
        <div class="bento-card bento-6">
            <div style="display:flex; gap:12px; align-items:start;">
                <div style="width:36px; height:36px; background:#F4F4F5; border:1px solid #E4E4E7; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">🎯</div>
                <div>
                    <div style="font-weight:600; font-size:14px; margin-bottom:4px;">KPIs that match your data</div>
                    <div style="font-size:13px; color:#52525B; line-height:1.5;">Detects 7 domains: sales → Total Sales, Total Profit, AOV, Margin; marketing → CTR, ROAS; sports → Goals, assists. Uses actual column names from your file.</div>
                </div>
            </div>
        </div>
        <div class="bento-card bento-4">
            <div style="font-weight:600; font-size:13px; margin-bottom:8px;">📈 Stats that matter</div>
            <div style="font-size:12px; color:#52525B; line-height:1.5;">Pearson/Spearman, t-test, ANOVA, chi-square with p < 0.001 formatting, effect size. Correlation ≠ causation always warned.</div>
            <div style="margin-top:12px; background:#F4F4F5; border-radius:8px; padding:8px 10px; font-family:JetBrains Mono; font-size:11px;">r=-0.22, Spearman -0.54, p < 0.001</div>
        </div>
        <div class="bento-card bento-4">
            <div style="font-weight:600; font-size:13px; margin-bottom:8px;">🧩 Segmentation fixed</div>
            <div style="font-size:12px; color:#52525B; line-height:1.5;">RFM now includes all customers: 793/793 (was 729). Champions, Loyal, At Risk (154) classified via RFM model — not just "122 at risk".</div>
            <div style="margin-top:12px; display:flex; gap:4px; flex-wrap:wrap;"><span class="badge badge-gray">Lost 162</span><span class="badge badge-gray">At Risk 154</span><span class="badge badge-black">Champions 106</span></div>
        </div>
        <div class="bento-card bento-4">
            <div style="font-weight:600; font-size:13px; margin-bottom:8px;">🗄️ SQL you can show in interview</div>
            <div style="font-size:12px; color:#52525B; line-height:1.5;">10+ queries: CTEs, window RANK/LAG, GROUP BY, DATE_TRUNC. Safe executor, only SELECT, limit 5000.</div>
            <div style="margin-top:12px; background:#09090B; color:#A1A1AA; border-radius:8px; padding:8px 10px; font-family:JetBrains Mono; font-size:10px;">WITH sales AS (SELECT ...)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📌 Quick guide — 1 min before upload")
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 What it does", "📂 What data works", "🔬 How it works", "⚠️ Limits"])

    with tab1:
        st.markdown("**5 steps:**\n1. Checks columns (numbers, categories, dates)\n2. Scores quality 0-100\n3. Cleans with log (original never changed)\n4. Shows charts, KPIs, insights like *What found → Why matters → What to do*\n5. Ask in English + SQL + download report\n\n*No hallucination — every number from your file.*")

    with tab2:
        st.markdown("""
        **File types:** CSV, Excel (pick sheet), JSON, Parquet — up to 200MB  
        **Best if:** 1 number (sales/profit) + 1 category (product/region) + 1 date + IDs  
        **Works great:** E-commerce, Superstore, Marketing, HR, SaaS, Sports, Finance  
        **If only 1 col:** Shows reason, not fake charts  
        **Tip:** Use clear names like `Sales, Profit, Order_Date`
        """)

    with tab3:
        st.markdown("""
        **Pandas:** Reads messy files  
        **DuckDB:** SQL fast — CTEs, RANK/LAG, DATE_TRUNC  
        **Plotly:** Interactive charts  
        **SciPy:** Pearson/Spearman, t-test, ANOVA  
        **Outliers:** IQR, flagged as anomaly not error  
        **RFM:** Recency/Frequency/Monetary → Champions/At Risk — now 793/793 fixed  
        **Time:** MoM/YoY, peak, forecast = estimate
        """)

    with tab4:
        st.markdown("""
        - **200MB max** — for 10M+ need BigQuery
        - **No login** — data in memory, disappears after close
        - **PII:** Detects email/phone, not names — handle Customer Name carefully
        - **Postal codes:** Now category not number (fixed)
        - **p-values:** Shows `p < 0.001` not `0.0000`
        - **Correlation ≠ causation** always warned
        """)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
    c1,c2 = st.columns([2,1])
    with c1:
        if st.button("🚀 Start with Upload →", type="primary", use_container_width=True):
            st.switch_page("pages/01_Upload.py")
    with c2:
        if st.button("📄 See Sample Report", use_container_width=True):
            st.switch_page("pages/13_Report.py")

if __name__ == "__main__":
    main()
