"""
Report generator — Jinja2 HTML with embedded insights.
"""
from jinja2 import Template
from typing import Dict, Any
import json
from datetime import datetime

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>DataVista — Analytics Report</title>
<style>
body { font-family: Inter, -apple-system, sans-serif; max-width: 900px; margin: 0 auto; padding: 40px 20px; background: #FAFAFA; color: #111827; line-height: 1.6; }
h1 { font-size: 28px; font-weight: 700; margin-bottom: 8px; }
h2 { font-size: 20px; font-weight: 600; margin-top: 32px; border-bottom: 1px solid #E5E7EB; padding-bottom: 8px; }
h3 { font-size: 16px; font-weight: 600; margin-top: 20px; }
.card { background: white; border: 1px solid #E5E7EB; border-radius: 12px; padding: 20px; margin: 16px 0; }
.metric { display: inline-block; margin: 8px 16px 8px 0; }
.metric-value { font-size: 24px; font-weight: 700; }
.metric-label { font-size: 12px; color: #6B7280; text-transform: uppercase; }
.badge { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 500; }
.badge-green { background: #ECFDF5; color: #065F46; }
.badge-amber { background: #FFFBEB; color: #92400E; }
.badge-red { background: #FEF2F2; color: #991B1B; }
.badge-indigo { background: #EEF2FF; color: #3730A3; }
table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 14px; }
th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #F3F4F6; }
th { font-weight: 600; color: #6B7280; font-size: 12px; text-transform: uppercase; }
.insight { border-left: 4px solid #6366F1; padding-left: 16px; margin: 16px 0; }
.insight-critical { border-left-color: #EF4444; }
.insight-warning { border-left-color: #F59E0B; }
.insight-info { border-left-color: #6366F1; }
.small { font-size: 12px; color: #6B7280; }
</style>
</head>
<body>
<h1>DataVista — Analytics Report</h1>
<p class="small">Generated {{ timestamp }} | App v{{ app_version }} | File {{ file_name }} ({{ rows }} rows, {{ cols }} cols) | Domain: {{ domain }} | Quality Score {{ quality_score }}/100</p>

<div class="card">
<h2>1. Executive Summary</h2>
<p>{{ executive_summary }}</p>
<ul>
{% for kpi in kpis[:5] %}
{% if kpi.available %}
<li><strong>{{ kpi.name }}:</strong> {{ kpi.value }} ({{ kpi.formula }}) — {{ kpi.interpretation }}</li>
{% endif %}
{% endfor %}
</ul>
</div>

<h2>2. Dataset Overview</h2>
<div class="card">
<p>Rows: {{ rows }}, Columns: {{ cols }}, Memory: {{ memory }}. Domain detected: {{ domain }} with confidence {{ domain_confidence }}.</p>
<table><tr><th>Column</th><th>Type</th><th>Missing %</th><th>Unique</th></tr>
{% for col in columns %}
<tr><td>{{ col.name }}</td><td><span class="badge badge-indigo">{{ col.inferred_type }}</span></td><td>{{ col.missing_pct }}%</td><td>{{ col.unique_count }}</td></tr>
{% endfor %}
</table>
</div>

<h2>3. Data Quality</h2>
<div class="card">
<p>Data Quality Score: <strong>{{ quality_score }}/100</strong> — measures completeness, record uniqueness, validity, consistency</p>
<p>Breakdown: Completeness {{ quality_breakdown.completeness }}% (40% weight), Record Uniqueness {{ quality_breakdown.record_uniqueness }}% - no duplicate records (20%), Validity {{ quality_breakdown.validity }}% (20%), Consistency {{ quality_breakdown.consistency }}% (20%)</p>
<table><tr><th>Severity</th><th>Issue</th></tr>
{% for issue in issues %}
<tr><td><span class="badge {% if issue.severity=='critical' %}badge-red{% elif issue.severity=='warning' %}badge-amber{% else %}badge-green{% endif %}">{{ issue.severity }}</span></td><td>{{ issue.description }} {% if issue.column %}({{ issue.column }}){% endif %}</td></tr>
{% endfor %}
</table>
<p style="font-size:12px; color:#6B7280; margin-top:8px;"><b>Note:</b> Data Quality 100/100 means the file is clean (no missing, no duplicates). It does NOT automatically mean statistical analysis is highly reliable.</p>
</div>

<h2>3b. Statistical Reliability</h2>
<div class="card">
<p><strong>Sample Size:</strong> {{ rows }} rows</p>
{% if rows < 30 %}
<p style="background:#FFFBEB; border:1px solid #FDE68A; padding:8px; border-radius:8px;"><b>⚠️ Small Sample Warning:</b> n={{ rows }} is very small. Statistical tests (t-test, ANOVA, chi-square, correlations) have low power and high uncertainty. Results should be treated cautiously and not used for strong business inference. Larger dataset (n>30 ideally >100) recommended for reliable inference.</p>
{% elif rows < 100 %}
<p style="background:#FFFBEB; border:1px solid #FDE68A; padding:8px; border-radius:8px;"><b>⚠️ Moderate Sample:</b> n={{ rows }} is moderate. Some statistical tests may be underpowered. Interpret with caution.</p>
{% else %}
<p style="background:#ECFDF5; border:1px solid #A7F3D0; padding:8px; border-radius:8px;"><b>✓ Sample Size:</b> n={{ rows }} is sufficient for most statistical tests, but always consider context and effect sizes, not just p-values.</p>
{% endif %}
<p><b>Data Quality vs Analysis Reliability:</b> A dataset can be perfectly clean (100/100) while still being too small for reliable statistical inference. Data Quality measures cleanliness; Statistical Reliability measures whether you have enough data for trustworthy conclusions.</p>
</div>

<h2>4. Cleaning Performed</h2>
<div class="card">
{% if cleaning_log %}
<table><tr><th>Step</th><th>Column</th><th>Action</th><th>Before</th><th>After</th><th>Rows Affected</th></tr>
{% for rec in cleaning_log %}
<tr><td>{{ rec.step }}</td><td>{{ rec.column }}</td><td>{{ rec.action }}</td><td>{{ rec.before }}</td><td>{{ rec.after }}</td><td>{{ rec.rows_affected }}</td></tr>
{% endfor %}
</table>
{% else %}
<p>No cleaning operations performed — analysis on original dataset.</p>
{% endif %}
</div>

<h2>5. Exploratory Analysis</h2>
<div class="card">
<h3>Numerical Summary</h3>
<table><tr><th>Column</th><th>Mean</th><th>Median</th><th>Std</th><th>Min</th><th>Max</th><th>Skew</th></tr>
{% for col, stats in eda_numerical.items() %}
<tr><td>{{ col }}</td><td>{{ "%.2f"|format(stats.mean) }}</td><td>{{ "%.2f"|format(stats.median) }}</td><td>{{ "%.2f"|format(stats.std) }}</td><td>{{ stats.min }}</td><td>{{ stats.max }}</td><td>{{ "%.2f"|format(stats.skew) }} ({{ stats.skew_interpretation }})</td></tr>
{% endfor %}
</table>

<h3>Categorical Top Values</h3>
{% for col, stats in eda_categorical.items() %}
<p><strong>{{ col }}</strong> (Unique: {{ stats.unique }}): Top = {{ stats.most_common }} ({{ stats.most_common_count }}). {% if stats.pareto_insight %}{{ stats.pareto_insight }}{% endif %}</p>
{% endfor %}
</div>

<h2>6. KPI Analysis</h2>
<div class="card">
<table><tr><th>KPI</th><th>Formula</th><th>Value</th><th>Interpretation</th></tr>
{% for kpi in kpis %}
{% if kpi.available %}
<tr><td>{{ kpi.name }}</td><td>{{ kpi.formula }}</td><td>{{ kpi.value }}</td><td>{{ kpi.interpretation }}</td></tr>
{% endif %}
{% endfor %}
</table>
</div>

<h2>7. Statistical Analysis</h2>
<div class="card">
<h3>Correlations</h3>
{% if correlations %}
<table><tr><th>Col1</th><th>Col2</th><th>Pearson r (p)</th><th>Spearman ρ (p)</th><th>Significant</th><th>Interpretation</th></tr>
{% for c in correlations[:5] %}
<tr><td>{{ c.col1 }}</td><td>{{ c.col2 }}</td><td>{{ "%.2f"|format(c.pearson_r) }} ({% if c.pearson_p < 0.001 %}p &lt; 0.001{% else %}p = {{"%.4f"|format(c.pearson_p)}}{% endif %})</td><td>{{ "%.2f"|format(c.spearman_r) }} ({% if c.spearman_p < 0.001 %}p &lt; 0.001{% else %}p = {{"%.4f"|format(c.spearman_p)}}{% endif %})</td><td>{{ "Yes" if c.is_significant else "No" }}</td><td>{{ c.interpretation }}</td></tr>
{% endfor %}
</table>
{% else %}
<p>No significant correlations or insufficient numeric columns.</p>
{% endif %}

<h3>Hypothesis Tests</h3>
{% for test in hypothesis_tests %}
<div style="margin:12px 0; padding:12px; border:1px solid #E5E7EB; border-radius:8px;">
<strong>{{ test.test_name }}</strong> ({{ test.decision }}, {% if test.p_value < 0.001 %}p &lt; 0.001{% else %}p = {{"%.4f"|format(test.p_value)}}{% endif %})<br>
H0: {{ test.null_hypothesis }}<br>
H1: {{ test.alt_hypothesis }}<br>
Interpretation: {{ test.interpretation }}
{% if test.effect_size %}<br>Effect size: {{ "%.2f"|format(test.effect_size) }} ({{ test.effect_interpretation }}){% endif %}
</div>
{% endfor %}
</div>

<h2>8. Key Findings</h2>
<div class="card">
{% for ins in insights %}
<div class="insight insight-{{ ins.severity }}">
<strong>{{ ins.finding }}</strong><br>
Evidence: {{ ins.evidence }}<br>
Meaning: {{ ins.business_meaning }}<br>
Recommendation: {{ ins.recommendation }}<br>
<span class="small">Source: {{ ins.source }} | Confidence: {{ ins.confidence }} | Type: {{ ins.type }}</span>
</div>
{% endfor %}
</div>

<h2>9. Methodology</h2>
<div class="card small">
<p>Tools: Python pandas, DuckDB, SciPy, Plotly. Tests: Pearson/Spearman correlation, Welch's t-test, ANOVA, Chi-square, 95% CI via t-distribution, Cohen's d for effect size. Outliers via IQR. Quality score weighted: Completeness 40%, Uniqueness 20%, Validity 20%, Consistency 20%. All AI interpretations traceable to calculated metrics, labelled as such. No causation claimed without evidence.</p>
</div>

<h2>10. Limitations</h2>
<div class="card small">
<ul>
<li>Analysis based on provided dataset only — no external validation.</li>
<li>Forecasts (if any) are estimates, not guaranteed.</li>
<li>Correlation does not imply causation.</li>
<li>Domain detection heuristic — verify KPIs match business definitions.</li>
<li>Missing data handling may bias results if not random.</li>
<li>Segmentation requires sufficient columns — some modules may be unavailable.</li>
</ul>
</div>

<p class="small">Report generated by DataVista v{{ app_version }} | Reproducibility manifest: {{ manifest }}</p>
</body>
</html>
"""

def generate_html_report(pipeline_data: Dict[str, Any]) -> str:
    """
    pipeline_data should contain aggregated results from orchestrator.
    """
    try:
        profile = pipeline_data.get('profile')
        quality = pipeline_data.get('quality')
        cleaning = pipeline_data.get('cleaning')
        eda = pipeline_data.get('eda', {})
        kpi = pipeline_data.get('kpi', {})
        stats_data = pipeline_data.get('statistics', {})
        insights = pipeline_data.get('insights', [])
        metadata = pipeline_data.get('metadata', {})

        template = Template(HTML_TEMPLATE)

        html = template.render(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            app_version=pipeline_data.get('app_version', '0.1.0'),
            file_name=metadata.get('file_name', 'dataset'),
            rows=profile.row_count if profile else 0,
            cols=profile.column_count if profile else 0,
            memory=f"{profile.memory_usage_mb} MB" if profile else "unknown",
            domain=profile.detected_domain if profile else "unknown",
            domain_confidence=profile.domain_confidence if profile else 0,
            quality_score=quality.score if quality else 0,
            quality_breakdown=quality.score_breakdown if quality else {},
            issues=quality.issues if quality else [],
            columns=profile.columns if profile else [],
            cleaning_log=cleaning.log if cleaning else [],
            eda_numerical=eda.get('numerical', {}) if isinstance(eda, dict) else {},
            eda_categorical=eda.get('categorical', {}) if isinstance(eda, dict) else {},
            kpis=kpi.get('kpis', []) if isinstance(kpi, dict) else [],
            correlations=stats_data.get('correlation', {}).get('results', []) if isinstance(stats_data, dict) else [],
            hypothesis_tests=stats_data.get('hypothesis_tests', []) if isinstance(stats_data, dict) else [],
            insights=insights,
            executive_summary=f"Dataset {metadata.get('file_name')} contains {profile.row_count if profile else 0} rows with quality score {quality.score if quality else 0}/100. Domain detected as {profile.detected_domain if profile else 'unknown'}. {len(insights)} key insights identified, with {sum(1 for i in insights if i.severity=='critical')} critical issues requiring attention.",
            manifest=json.dumps(metadata, default=str)
        )

        return html

    except Exception as e:
        return f"<html><body><h1>Report generation failed: {e}</h1></body></html>"
