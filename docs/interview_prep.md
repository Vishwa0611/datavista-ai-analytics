# Interview Preparation — InsightForge Project

## Project Explanation (For Recruiter)

**30-sec:** Upload any CSV → profiling, quality audit 0-100, cleaning log, domain-aware KPIs, stats, segmentation, time-series, traceable AI insights, SQL lab, report. Python, DuckDB, Plotly, Streamlit, deployed HF Spaces.

**1-min:** Built from 328 real JDs research — Excel 81%, SQL 60%, Power BI 43%, Python 41% (59% in 7LPA+). Solves SMEs get CSVs but no analyst. Self-service workbench mimics Junior Analyst week 1. Differentiator: traceable insights (Finding→Evidence→Action), no hallucinated numbers, domain adaptation, SQL showcase queries.

**3-min:** Architecture modular monolith, why Streamlit (2026 default, 45 lines KPI vs Dash 80, 16GB free HF), DuckDB (OLAP, Window, DATE_TRUNC) vs SQLite, deterministic insight engine first (no API key, free deploy, trustworthy) + optional LLM wrapper (only aggregated metrics, strict prompt, consent), transformation log (original immutable, lineage), quality score weighted transparent 40/20/20/20, domain detection keyword scoring not ML (explainable), PII conservative only object columns, honest limitations (200MB max, forecasts estimates, segmentation conditional). Testing pytest, reproducibility manifest, deployment comparison.

## Technical Questions & Strong Answers

### Python / Pandas

**Q: Why pandas over Polars?**
A: Pandas is recruiter expectation 41% JDs, more known, easier for fresher to explain. For large files I'd use Polars (lazy, faster) — mentioned in docs as future. MVP uses pandas for readability.

**Q: How did you handle encoding?**
A: Try utf-8, then latin1, ISO-8859-1, cp1252, fallback errors='replace'. Show file metadata encoding used.

**Q: How prevent memory OOM?**
A: File size validation 200MB MVP, memory usage display, preview first 100 rows, sampling for heavy charts (>50k points sample with disclaimer), DuckDB aggregations for KPIs using full data fast columnar, caching via st.cache_data.

### SQL

**Q: Why DuckDB?**
A: In-process OLAP, columnar, faster aggregations than SQLite, native WINDOW (RANK, LAG) and DATE_TRUNC which SQLite lacks or needs workaround. Zero setup for portfolio, demonstrates SQL skills (JOIN, CTE, Window) covering 60% JDs. Production would swap to BigQuery/Snowflake same queries.

**Q: Show CTE example**
A: `WITH customer_totals AS (SELECT customer_id, SUM(revenue) as total FROM cleaned_data GROUP BY customer_id) SELECT * FROM customer_totals ORDER BY total DESC LIMIT 10;` — CTE improves readability, modular, used for top customers.

**Q: Window Functions difference RANK vs ROW_NUMBER?**
A: RANK gives same rank for ties and skips next (1,2,2,4), ROW_NUMBER always unique (1,2,3,4). I used RANK for top customers to handle tie revenue, LAG for MoM growth to compare previous month.

**Q: How prevent SQL injection?**
A: Custom SQL validated: only SELECT/WITH allowed, block DROP/DELETE/INSERT/UPDATE/ALTER, whitelist tables raw_data/cleaned_data, length limit 5000, limit 5000 rows. NL-to-SQL uses column whitelist + template SQL, no exec of user code.

### Statistics

**Q: Why Pearson vs Spearman?**
A: Pearson linear, sensitive to outliers, interval data; Spearman rank, robust, ordinal/monotonic. I show both — if Pearson high but Spearman low, suggests outlier-driven linear. Correlation ≠ causation disclaimer in UI and report.

**Q: When use chi-square test?**
A: Categorical vs categorical association (e.g., product category vs region). Null independent, Alt associated. Need contingency >=2x2, expected >=5. I auto-suggest if cat cols unique <=10.

**Q: What is p-value?**
A: Probability of observing test statistic as extreme assuming H0 true. Small p (<0.05) suggests data unlikely under H0, so we reject H0 — but not proof H1 true, and practical importance needs effect size.

**Q: Why Welch's t-test not Student's?**
A: Student's assumes equal variance; Welch's does not (equal_var=False) — safer for real data where variance may differ, e.g., profit North vs South.

**Q: What is effect size and why?**
A: p-value tells significance, not magnitude. Cohen's d = (mean1-mean2)/pooled_std. <0.2 negligible, <0.5 small, <0.8 medium, >=0.8 large. I include to avoid p-hacking and show business relevance.

### EDA / Data Cleaning

**Q: How handle missing data?**
A: Detect missing %, show per column, worst 5. Suggest median for numeric <30% missing, mode for categorical, or drop rows if "all". Never silently drop — transformation log shows before/after and rows affected. If missing >30%, suggest collect more data rather than impute.

**Q: How detect outliers?**
A: IQR method default (Q1-1.5IQR, Q3+1.5IQR) — robust, no normality assumption. Also Z-score option (mean±3std) assumes normality. Show count, pct, example records. User can choose Keep/Remove/Cap/Winsorize — never auto-delete without explanation.

**Q: How decide which charts to generate?**
A: Smart selection based on dtype and purpose — not 50 charts. Numerical → histogram + box, Categorical unique <50 → bar, Date + numeric → line trend, >1 numeric → heatmap, Pareto if applicable. Each chart has reason tooltip.

### Visualization / Power BI

**Q: Power BI vs Plotly?**
A: Power BI 43% JDs India, but can't embed easily in free Python app. I simulate BI thinking via Plotly interactive dashboard (cards, metrics, filters, tooltips) and mention Power BI equivalent in docs. For portfolio, Plotly shows visualization skill transferable to Power BI.

### AI / Responsible AI

**Q: How prevent AI hallucinations?**
A: Deterministic engine first — insights from calculated metrics only, no LLM. Each insight has Finding→Evidence (actual calc dict)→Meaning→Action. Evidence includes metric, value, formula. LLM wrapper optional — system prompt "Only use provided numbers", sends only aggregated JSON (quality_score, kpis, correlations) never raw PII rows, consent toggle, label "AI-generated interpretation — verify".

**Q: What if dataset contains PII?**
A: PII detection via regex (email, phone strict) only on object columns (skip numeric metrics like spend), conservative to avoid flagging revenue as phone. Warning banner "Potential PII in email — not sent to external AI", mask display, never log raw rows, optional AI disabled unless consent.

### System Design / Deployment

**Q: How handle 10 million rows?**
A: MVP 200MB limit. Production: chunk reading (pandas chunksize), Polars lazy evaluation, DuckDB out-of-core aggregations, sampling for EDA heavy charts, move to BigQuery/Snowflake for warehouse, Streamlit caching, horizontal scaling with multiple instances behind load balancer (Streamlit not multi-process). Explain in docs limitations honestly.

**Q: How would you productionize?**
A: Add auth (Streamlit authenticator), user file storage (S3), job queue (Celery) for long pipelines, monitoring (logging, alerts for quality drop), data quality monitoring (save profile, compare new upload), CI/CD GitHub Actions pytest, Docker + Kubernetes if scale, but for internal analytics tool modular monolith is sufficient.

**Q: Deployment architecture?**
A: Primary HF Spaces — Streamlit SDK, 2 CPU, 16GB RAM, 50GB disk free, no sleep, auto-build from git push, secrets via Space variables. Secondary Streamlit Cloud 1GB RAM sleeps 7 days. Docker for Render. Entry streamlit_app.py runs on 7860 (HF) or 8501.

### Testing / Code Quality

**Q: Testing strategy?**
A: pytest unit tests for ingestion (valid CSV, invalid ext, empty, Excel, JSON), quality (missing, duplicates, perfect score), KPI (revenue sum, AOV, missing cols), stats (correlation strong, t-test significant), cleaning (dedupe, fillna, trim), SQL (register + query, showcase generation). Edge cases: empty dataset, one-column, missing, dupes, invalid dates, mixed types, very small, large, no numeric, no categorical.

**Q: Why modular code with typed dataclasses?**
A: Professional, testable, interview-explainable — each module returns ModuleResult/KPIResult/Insight dataclass, pure functions, clear responsibilities, no 2000-line file, type hints, docstrings.

## Business / Behavioral

**Q: Revenue dropped 15% — walk through investigation?**
A: Structured: 1) Confirm period, check data quality, 2) Segment by category/region/product/channel to find where drop, 3) Check KPI funnel (impressions→clicks→conversions), 4) Compare MoM/YoY, 5) Statistical test if significant, 6) Check external factors (campaign spend, seasonality, discount), 7) Recommend action — exactly what InsightForge automates via comparison mode + segmentation + time-series + insights.

**Q: How translate findings to non-technical stakeholders?**
A: Executive summary, KPI cards with formula + plain English, Finding→Evidence→Meaning→Action structure, avoid jargon, show "So what?" for each finding, methodology and limitations honest.

## Follow-up Recruiters May Ask

- Show me SQL query with Window Function? (Open SQL Lab)
- Explain quality score 87 — why? (Breakdown completeness etc.)
- What happens if dataset has no date column? (Time series shows unavailable reason)
- How would you add funnel analysis? (Need event/stage columns, conditional activation similar to segmentation)
- What is biggest weakness of project? (200MB limit, heuristic domain detection, forecasts simple, no auth — documented honestly, future improvements listed)

