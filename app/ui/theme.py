"""
DataVista — Fullstack Design v3
Light premium sidebar — correct palette, no dark black
No light/dark toggle, no Cmd+K — clean single navigation
Perfect alignment, animations, fullstack bento
"""
PRIMARY = "#111827"
ACCENT = "#6366F1"
ACCENT_2 = "#06B6D4"

CHART_PALETTE = ["#6366F1", "#06B6D4", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899"]

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@600;700&display=swap');

#MainMenu, footer, header {display: none !important;}
html {scroll-behavior: smooth;}
* { -webkit-font-smoothing: antialiased; }

.stApp {
    background: #FAFBFC !important;
    font-family: 'Inter', sans-serif !important;
}

/* LIGHT PREMIUM SIDEBAR — correct, not dark black */
section[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E5E7EB !important;
    box-shadow: 1px 0 0 rgba(0,0,0,0.02), 4px 0 24px rgba(0,0,0,0.02) !important;
}
section[data-testid="stSidebar"] > div {
    padding-top: 12px !important;
}
section[data-testid="stSidebar"] .block-container {
    padding: 16px 14px !important;
}

/* Hide default Streamlit nav — we use custom sidebar */
[data-testid="stSidebarNav"] {display: none !important;}

.block-container {
    max-width: 1400px !important;
    padding: 0 28px 40px 28px !important;
}

/* TOP BAR */
.fullstack-header {
    height: 56px;
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(16px) saturate(180%);
    border-bottom: 1px solid #E5E7EB;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    position: sticky;
    top: 0;
    z-index: 100;
    margin: -1rem -28px 20px -28px;
}

/* HERO */
.hero-fullstack {
    position: relative;
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 24px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02), 0 4px 12px rgba(0,0,0,0.03);
}
.hero-grid {
    position: absolute;
    inset: 0;
    background-image: 
        linear-gradient(rgba(0,0,0,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,0,0,0.02) 1px, transparent 1px);
    background-size: 28px 28px;
    mask: radial-gradient(ellipse at 30% 0%, black 50%, transparent 80%);
    opacity: 0.6;
}
.hero-orb {
    position: absolute;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle at center, rgba(99,102,241,0.08) 0%, rgba(6,182,214,0.06) 40%, transparent 70%);
    top: -160px;
    right: -80px;
    border-radius: 50%;
    filter: blur(30px);
    animation: orbFloat 10s ease-in-out infinite;
}
@keyframes orbFloat {
    0%, 100% { transform: translate(0,0) scale(1); }
    50% { transform: translate(-12px, 8px) scale(1.05); }
}
.hero-content {
    position: relative;
    z-index: 2;
    padding: 40px 36px;
    display: grid;
    grid-template-columns: 1.15fr 0.85fr;
    gap: 32px;
    align-items: center;
}
@media (max-width: 1024px) {
    .hero-content { grid-template-columns: 1fr; padding: 28px 20px; }
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 44px !important;
    font-weight: 700 !important;
    line-height: 0.95 !important;
    letter-spacing: -0.03em !important;
    color: #111827 !important;
    margin-bottom: 12px !important;
}
.hero-title span {
    background: linear-gradient(135deg, #6366F1 0%, #06B6D4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-subtitle {
    font-size: 14px !important;
    line-height: 1.6 !important;
    color: #6B7280 !important;
    max-width: 480px;
}
.hero-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 20px;
}
.hero-stat {
    background: #F9FAFB;
    border: 1px solid #F3F4F6;
    border-radius: 10px;
    padding: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.hero-stat-icon {
    width: 32px;
    height: 32px;
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
}

/* BENTO GRID */
.bento-grid {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 14px;
    margin-bottom: 24px;
}
.bento-3 { grid-column: span 3; }
.bento-4 { grid-column: span 4; }
.bento-6 { grid-column: span 6; }
.bento-8 { grid-column: span 8; }
.bento-12 { grid-column: span 12; }
@media (max-width: 1024px) {
    .bento-3, .bento-4, .bento-6, .bento-8 { grid-column: span 12; }
}

.bento-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    padding: 18px;
    position: relative;
    overflow: hidden;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    height: 100%;
}
.bento-card:hover {
    border-color: #D1D5DB;
    box-shadow: 0 6px 20px rgba(0,0,0,0.04), 0 2px 6px rgba(0,0,0,0.03);
    transform: translateY(-2px);
}
.bento-card-dark {
    background: #111827;
    border-color: #1F2937;
    color: white;
}
.bento-card-dark * { color: white !important; }
.bento-card-dark .bento-label { color: #9CA3AF !important; }
.bento-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: #6B7280;
    margin-bottom: 6px;
}
.bento-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1;
    margin-bottom: 4px;
}
.bento-sub {
    font-size: 11px;
    color: #6B7280;
}
.bento-trend {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: #F0FDF4;
    color: #15803D;
    border: 1px solid #BBF7D0;
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 600;
}

/* Demo bento */
.demo-bento {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    height: 100%;
    display: flex;
    flex-direction: column;
}
.demo-bento:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px rgba(0,0,0,0.06);
    border-color: #D1D5DB;
}
.demo-bento-header {
    padding: 14px 18px;
    border-bottom: 1px solid #F3F4F6;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.demo-bento-body { padding: 18px; flex: 1; }
.demo-bento-footer {
    padding: 12px 18px;
    background: #F9FAFB;
    border-top: 1px solid #F3F4F6;
    display: flex;
    gap: 6px;
}

/* Buttons */
.stButton > button {
    border-radius: 9px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    height: 36px !important;
    letter-spacing: -0.01em !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
.stButton > button[kind="primary"] {
    background: #111827 !important;
    color: white !important;
    border: 1px solid #111827 !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
}
.stButton > button[kind="primary"]:hover {
    background: #1F2937 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
}
.stButton > button[kind="secondary"] {
    background: white !important;
    border: 1px solid #E5E7EB !important;
    color: #111827 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #F9FAFB !important;
    border-color: #D1D5DB !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: white !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
}
[data-testid="stMetric"] label {
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    color: #6B7280 !important;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 20px !important;
    font-weight: 700 !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: white;
    border: 1px dashed #D1D5DB;
    border-radius: 14px;
    padding: 20px;
}
[data-testid="stFileUploader"]:hover {
    border-color: #111827;
    background: #F9FAFB;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #F3F4F6;
    border-radius: 10px;
    padding: 3px;
    gap: 3px;
    border: 1px solid #E5E7EB;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 500;
    font-size: 13px;
    padding: 7px 14px !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    color: #111827 !important;
    border: 1px solid #E5E7EB !important;
}

/* Code */
code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    background: #F3F4F6 !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 6px !important;
    padding: 2px 6px !important;
}

/* Badges */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 500;
    border: 1px solid transparent;
}
.badge-green { background: #F0FDF4; color: #15803D; border-color: #BBF7D0; }
.badge-amber { background: #FFFBEB; color: #B45309; border-color: #FDE68A; }
.badge-red { background: #FEF2F2; color: #991B1B; border-color: #FECACA; }
.badge-indigo { background: #EEF2FF; color: #4338CA; border-color: #C7D2FE; }
.badge-gray { background: #F3F4F6; color: #52525B; border-color: #E5E7EB; }
.badge-black { background: #111827; color: white; border-color: #111827; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-thumb { background: #D1D5DB; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #9CA3AF; }

/* Animations */
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.bento-card, [data-testid="stMetric"] { animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) both; }

/* Premium card compat */
.premium-card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    padding: 18px;
    transition: all 0.25s ease;
    height: 100%;
}
.premium-card:hover {
    border-color: #D1D5DB;
    box-shadow: 0 6px 20px rgba(0,0,0,0.04);
    transform: translateY(-2px);
}
.feature-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    border: 1px solid #E5E7EB;
    background: white;
}
.icon-indigo { background: #EEF2FF; }
.icon-green { background: #F0FDF4; }
.icon-amber { background: #FFFBEB; }
.demo-card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    padding: 18px;
    transition: all 0.25s ease;
    height: 100%;
}
.demo-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px rgba(0,0,0,0.06);
}
</style>
"""
