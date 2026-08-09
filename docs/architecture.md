# Architecture — InsightForge

## Overview
Modular Monolith — Streamlit frontend + domain-driven core modules in `src/`.

## Data Flow
Upload → Profile → Quality → Clean → EDA → KPI → Stats → Segmentation → TimeSeries → Insights → Report

## Modules
- ingestion: file handling with encoding fallback
- profiling: column classification (numerical, categorical, datetime, ID, PII, constant)
- quality: scoring 0-100 weighted, missing, duplicates, outliers, consistency
- cleaning: pure functions, transformation log, original immutable
- eda: numerical stats, categorical freq, temporal trends, smart chart selection
- kpi: domain detection via keyword scoring, fuzzy column matching, interpretable formulas
- statistics: Pearson/Spearman, t-tests, ANOVA, chi-square, CI, Cohen's d
- segmentation: RFM, Pareto, performance ranking
- timeseries: trend, MoM/YoY, rolling, peak/low, simple forecast (estimate label)
- sql: DuckDB in-memory, showcase queries covering CTEs, Windows, GROUP BY, HAVING, CASE WHEN, DATE_TRUNC
- ai: deterministic rule engine (Finding→Evidence→Meaning→Action) + optional LLM wrapper with hallucination guard
- reporting: Jinja2 HTML report
- visualization: Plotly wrappers with muted palette

## Database Design
DuckDB in-process OLAP:
- raw_data table (original)
- cleaned_data table (after cleaning)
- _metadata, _query_log for reproducibility

Why DuckDB over SQLite: columnar, analytical, faster aggregations, native WINDOW, DATE_TRUNC.

## Security
- File extension & size validation, magic byte check
- No eval/exec of user code
- NL-to-SQL uses column whitelist + template SQL only
- PII detection via regex, conservative, only object columns, warning banner, never sent to external LLM without consent
- Secrets via st.secrets / .env, no hardcoded keys
- Jinja2 autoescape for report

## Deployment
- Primary: Hugging Face Spaces — Streamlit SDK, 2 CPU, 16GB RAM, 50GB disk free, no sleep
- Secondary: Streamlit Community Cloud — 1GB RAM, sleeps after 7 days
- Tertiary: Render/Docker

## Reproducibility
Manifest JSON: file hash, timestamp, domain, quality, cleaning log, config, version.
