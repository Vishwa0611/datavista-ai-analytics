# Methodology

## Data Profiling
- Column type inference: dtype + unique ratio + name hints (id) + PII regex + datetime parsing success >80%
- ID detection: unique_ratio >0.95 + name contains id/code/key, numeric excluded unless ID hint
- PII: only object columns, email loose regex, phone strict 10-digit after cleaning, skip float metrics
- Domain: keyword scoring across 6 domains (ecommerce, marketing, hr, saas, finance, ops)

## Data Quality Score
Weighted 0-100:
- Completeness 40%: 100 - missing_pct
- Uniqueness 20%: 100 - min(50, dupe_pct*5)
- Validity 20%: penalize invalid types, negative suspicious values
- Consistency 20%: blank strings, whitespace, inconsistent casing

## Cleaning
- Each op pure function returns new DF + affected count
- Log: step, column, action, before, after, rows_affected
- Original immutable

## EDA
- Numerical: mean, median, mode, min, max, std, var, q1, q3, IQR, skew, kurtosis, CV, skew interpretation
- Categorical: freq, %, unique, Pareto insight
- Temporal: resample D/W/M/Q/Y, MoM/YoY pct_change, rolling avg, trend via polyfit slope, peak/low idxmax
- Chart selection: only if data supports, limit to avoid chart spam

## KPI Engine
- Domain config: list of KPIs with aliases (list of possible column names)
- Fuzzy match: exact OR substring with len>=3, to avoid single-letter false positives
- Calculation: SUM, COUNT_DISTINCT, AVG, ratio with evidence columns
- Interpretation: rule-based per KPI name/unit

## Statistics
- Correlation: Pearson (linear) + Spearman (rank), p-value via scipy, significance α=0.05, interpretation strength, disclaimer correlation != causation
- Hypothesis: auto-suggest based on categorical + numeric; Welch's t-test (equal_var=False) safe, ANOVA >2 groups, chi-square categorical vs categorical; show H0/H1, stat, p, decision, plain-English, effect size
- CI: t.interval mean ± t*SEM, 95%
- Effect size: Cohen's d

## Segmentation
- RFM: recency days since max date, frequency count, monetary sum; scores 1-5 via qcut, segments Champions/Loyal/New/At Risk/Lost
- Pareto: grouped sum sorted, cumulative %, insight if top 30% categories drive 80%
- Performance: groupby sum/mean/count top 10

## Time Series
- Trend via linear slope vs mean threshold
- Seasonality via monthly avg across years if >=12 months
- Forecast: 3-month moving avg + linear trend, disclaimer estimate

## AI Insights
- Deterministic rules: quality low, missing high, duplicate, low margin, high churn, skew >1, strong correlation >0.5 significant, significant hypothesis, Pareto <30% drives 80%, at-risk customers, decreasing trend MoM<-5%, growth MoM>20%
- Structure: Finding, Evidence (metric, value), Business Meaning, Recommendation, Severity, Confidence, Type, Source
- LLM wrapper: only aggregated metrics JSON, never raw rows, system prompt "Only use provided numbers", labelled interpretation

## SQL Layer
- Queries showcase SELECT, WHERE, GROUP BY, HAVING, CASE WHEN, CTE, Window RANK/LAG, DATE_TRUNC, aggregation DISTINCT/STDDEV
- Safe executor: block DROP/DELETE/INSERT/UPDATE/ALTER, only SELECT/WITH, limit 5000 rows
