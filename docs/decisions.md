# Architecture Decision Records (ADRs)

## ADR 1: Streamlit vs Dash vs Gradio
- Decision: Streamlit
- Context: Need fast shipping, SaaS UI, free deployment, multipage workflow
- Options: Dash (enterprise, fine callbacks, but days to build), Gradio (model demos, not analytics), Streamlit (2026 default for data apps)
- Reason: Streamlit ~45 lines for KPI dashboard vs Dash ~80 lines, 1-3 days vs 1-2 weeks, file-based multipage matches 14-page workflow, 16GB RAM on HF Spaces free vs Streamlit Cloud 1GB
- Consequences: Less fine callback control, but acceptable for fresher; can explain tradeoffs in interview

## ADR 2: DuckDB vs SQLite
- Decision: DuckDB
- Context: Need SQL analytics layer to demonstrate SQL skills (JOIN, CTE, Window)
- Reason: DuckDB columnar OLAP, faster aggregations, native WINDOW functions (ROW_NUMBER, RANK, LAG), DATE_TRUNC, zero setup in-process, vs SQLite lacks WINDOW in older versions and DATE_TRUNC
- Interview: "I chose DuckDB because it's OLAP optimized for analytics, shows I understand modern data stack (Parquet, analytical DB). Production would swap to BigQuery/Snowflake with same queries."

## ADR 3: Deterministic Insight Engine First
- Decision: Rule-based engine first, optional LLM wrapper second
- Context: Need AI-assisted analytics but avoid hallucination
- Reason: Deterministic guarantees no invented numbers, no API key needed, free deployment, traceable Finding→Evidence. LLM only as interpreter with guardrail prompt "Only use provided numbers"
- Consequences: Less "magic" but more trustworthy — major differentiator vs typical fresher "AI-powered" projects that hallucinate

## ADR 4: Transformation Log Over Silent Cleaning
- Decision: Keep original immutable, log all transforms
- Context: Real company practice requires audit trail
- Reason: Reproducibility, data lineage, shows maturity beyond df.fillna(inplace=True)
- Consequences: Extra memory for log, but worth for portfolio

## ADR 5: Quality Score Weighted Transparent
- Decision: Weighted formula 40/20/20/20, explained breakdown
- Context: Need to quantify quality
- Reason: Explainable, interview-discussable, not black-box. Shows KPI design thinking
- Consequences: Weights subjective but documented — can argue in interview

## ADR 6: Domain Detection Keyword Scoring (Not ML)
- Decision: Simple keyword scoring + fuzzy column matching
- Context: Need to adapt KPIs to dataset domain
- Reason: Transparent, no training data needed, works offline, easy to extend. ML classifier would be overengineering, hard to explain for fresher
- Consequences: May misclassify edge cases, but confidence score indicates uncertainty

## ADR 7: Parquet Optional via pyarrow
- Decision: Support Parquet optionally, handle missing pyarrow gracefully
- Context: Modern data stack uses Parquet
- Reason: Shows awareness without forcing heavy dependency
- Consequences: If pyarrow not installed, error message guides user

## ADR 8: No Authentication / Multi-tenancy
- Decision: Single-session, no auth
- Context: Portfolio project, free hosting
- Reason: Adding auth would require DB, complexity, not needed for demo. Keeps code understandable for fresher
- Limitations documented honestly
