"""
Deterministic Insight Engine — rule-based, no hallucination.
Generates Finding → Evidence → Meaning → Action from calculated metrics.
"""
from typing import List, Dict, Any
from ..validation.schema import Insight
import pandas as pd

def generate_insights(pipeline_data: Dict[str, Any]) -> List[Insight]:
    """
    pipeline_data contains: profile, quality, kpis, stats, segmentation, timeseries, eda
    """
    insights: List[Insight] = []

    try:
        # --- Business KPIs Insights (NEW: More business-oriented) ---
        kpi_data = pipeline_data.get('kpi')
        if kpi_data and kpi_data.get('kpis'):
            total_sales_kpi = next((k for k in kpi_data['kpis'] if 'sales' in k.name.lower() and k.available), None)
            total_profit_kpi = next((k for k in kpi_data['kpis'] if 'profit' in k.name.lower() and 'margin' not in k.name.lower() and k.available), None)
            margin_kpi = next((k for k in kpi_data['kpis'] if 'margin' in k.name.lower() and k.available), None)
            
            if total_sales_kpi and total_profit_kpi and margin_kpi:
                insights.append(Insight(
                    finding=f"The business generated ${total_profit_kpi.value:,.0f} profit on ${total_sales_kpi.value:,.0f} in sales, producing a {margin_kpi.value:.2f}% overall profit margin.",
                    evidence={"total_sales": total_sales_kpi.value, "total_profit": total_profit_kpi.value, "margin": margin_kpi.value, "formula": f"{total_profit_kpi.formula} and {total_sales_kpi.formula}"},
                    business_meaning="Profitability overview — baseline for executive dashboard. Compare with industry benchmarks and track over time.",
                    recommendation="Use this as baseline for profitability analysis. Investigate margin by category/region to find optimization opportunities.",
                    severity="info",
                    confidence="high",
                    type="CalculatedInsight",
                    source="kpi"
                ))

        # --- Quality Insights ---
        quality = pipeline_data.get('quality')
        if quality:
            score = quality.score
            if score < 70:
                insights.append(Insight(
                    finding=f"Data quality is low — score {score}/100",
                    evidence={"score": score, "breakdown": quality.score_breakdown, "missing_pct": quality.missing.missing_pct},
                    business_meaning="Low quality may lead to unreliable analysis and poor business decisions. Stakeholders may question credibility.",
                    recommendation="Prioritize cleaning: handle missing values, deduplicate, standardize labels before reporting KPIs.",
                    severity="critical",
                    confidence="high",
                    type="CalculatedInsight",
                    source="quality"
                ))
            # Missing
            for col, info in quality.missing.per_column.items():
                if info['pct'] > 20:
                    insights.append(Insight(
                        finding=f"High missing values in {col} — {info['pct']}%",
                        evidence={"column": col, "missing_pct": info['pct'], "missing_count": info['count']},
                        business_meaning=f"Analysis on {col} will be incomplete and may be biased if missing is not random.",
                        recommendation=f"Investigate why {col} is missing. Consider median/mode imputation if <30% or collect more data.",
                        severity="warning",
                        confidence="high",
                        type="CalculatedInsight",
                        source="quality"
                    ))
            # Duplicates
            if quality.duplicates.duplicate_row_count > 0:
                insights.append(Insight(
                    finding=f"{quality.duplicates.duplicate_row_count} duplicate rows detected ({quality.duplicates.duplicate_pct}%)",
                    evidence={"duplicates": quality.duplicates.duplicate_row_count, "pct": quality.duplicates.duplicate_pct},
                    business_meaning="Duplicates inflate counts and distort revenue/customer metrics — leads to over-reporting.",
                    recommendation="Remove duplicates, verify if duplicate is valid (e.g., same customer multiple orders same day).",
                    severity="warning",
                    confidence="high",
                    type="CalculatedInsight",
                    source="quality"
                ))

        # --- KPI Insights ---
        kpi_data = pipeline_data.get('kpi')
        if kpi_data and kpi_data.get('kpis'):
            kpis = kpi_data['kpis']
            # Find low margin if exists
            for kpi in kpis:
                if not kpi.available:
                    continue
                if "margin" in kpi.name.lower() and isinstance(kpi.value, (int,float)):
                    if kpi.value < 10:
                        insights.append(Insight(
                            finding=f"Low {kpi.name}: {kpi.value:.1f}%",
                            evidence={"kpi": kpi.name, "value": kpi.value, "formula": kpi.formula, "columns": kpi.evidence_columns},
                            business_meaning="Low margin means revenue not converting to profit — potential discounting or cost issue.",
                            recommendation="Audit discount strategy, product mix, and fulfillment costs by segment.",
                            severity="critical",
                            confidence="high",
                            type="CalculatedInsight",
                            source="kpi"
                        ))
                if "churn" in kpi.name.lower() or "attrition" in kpi.name.lower():
                    if isinstance(kpi.value, (int,float)) and kpi.value > 20:
                        insights.append(Insight(
                            finding=f"High {kpi.name}: {kpi.value:.1f}%",
                            evidence={"kpi": kpi.name, "value": kpi.value},
                            business_meaning="High churn indicates retention problem — impacts long-term revenue.",
                            recommendation="Segment churn by tenure/department, run exit survey analysis, improve engagement.",
                            severity="critical",
                            confidence="high",
                            type="CalculatedInsight",
                            source="kpi"
                        ))

        # --- EDA Insights — Skew ---
        eda_data = pipeline_data.get('eda')
        if eda_data:
            numerical = eda_data.get('numerical', {})
            for col, stats in numerical.items():
                skew = stats.get('skew', 0)
                if abs(skew) > 1:
                    insights.append(Insight(
                        finding=f"{col} distribution is {'right' if skew>0 else 'left'} skewed (skew={skew:.2f})",
                        evidence={"column": col, "skew": skew, "mean": stats.get('mean'), "median": stats.get('median')},
                        business_meaning="Mean is pulled by extreme values — median may be better for typical value. Outliers present.",
                        recommendation=f"Investigate high/low {col} values — check if extreme values are valid. For small samples (n<20), median may be more reliable than mean for reporting.",
                        severity="info",
                        confidence="medium",
                        type="CalculatedInsight",
                        source="eda"
                    ))

        # --- Statistical Insights ---
        stats_data = pipeline_data.get('statistics')
        if stats_data:
            corr = stats_data.get('correlation', {})
            for corr_res in corr.get('results', [])[:3]:  # top 3
                if corr_res.is_significant and abs(corr_res.pearson_r) > 0.5:
                    insights.append(Insight(
                        finding=f"Strong correlation between {corr_res.col1} and {corr_res.col2} (r={corr_res.pearson_r:.2f})",
                        evidence={"col1": corr_res.col1, "col2": corr_res.col2, "pearson_r": corr_res.pearson_r, "p_value": corr_res.pearson_p},
                        business_meaning=f"{corr_res.col1} moves with {corr_res.col2} — useful for forecasting but correlation does NOT imply causation.",
                        recommendation="Explore causal drivers, use for prediction but validate with domain knowledge.",
                        severity="info",
                        confidence="medium",
                        type="CalculatedInsight",
                        source="statistics"
                    ))
            # Hypothesis tests significant
            for test in stats_data.get('hypothesis_tests', [])[:2]:
                if test.p_value < 0.05:
                    insights.append(Insight(
                        finding=f"Statistically significant difference found: {test.test_name} (p={test.p_value:.4f})",
                        evidence={"test": test.test_name, "p_value": test.p_value, "stat": test.test_statistic, "effect_size": test.effect_size},
                        business_meaning=test.interpretation,
                        recommendation="Investigate business reason for difference — pricing, region, product, process variation?",
                        severity="info",
                        confidence="high",
                        type="CalculatedInsight",
                        source="statistics"
                    ))

        # --- Segmentation Insights ---
        seg_data = pipeline_data.get('segmentation')
        if seg_data:
            pareto_dict = seg_data.get('pareto', {})
            for key, pareto_res in pareto_dict.items():
                if pareto_res.get('available') and pareto_res.get('pct_categories_80', 100) < 30:
                    insights.append(Insight(
                        finding=f"Pareto principle in {key}: {pareto_res['pct_categories_80']:.1f}% categories drive 80% of value",
                        evidence={"key": key, "pct": pareto_res['pct_categories_80'], "insight": pareto_res['insight']},
                        business_meaning="Concentration risk/opportunity — focus on top categories/customers yields high impact.",
                        recommendation="Prioritize top categories for retention/growth, investigate low performers.",
                        severity="info",
                        confidence="high",
                        type="CalculatedInsight",
                        source="segmentation"
                    ))
            rfm = seg_data.get('rfm', {})
            if rfm.get('available'):
                counts = rfm.get('segment_counts', {})
                if counts.get('At Risk', 0) > 0:
                    insights.append(Insight(
                        finding=f"{counts.get('At Risk',0)} customers classified as At Risk based on RFM segmentation model",
                        evidence={"segment_counts": counts},
                        business_meaning="At Risk segment: customers previously valuable but with low recent activity. This is a model-derived classification based on Recency, Frequency, Monetary scores, not directly in raw data.",
                        recommendation="Launch re-engagement campaign for at-risk, analyze last purchase reasons.",
                        severity="warning",
                        confidence="medium",
                        type="CalculatedInsight",
                        source="segmentation"
                    ))

        # --- Time Series Insights ---
        ts_data = pipeline_data.get('timeseries')
        if ts_data:
            trends = ts_data.get('trends', {}).get('trends', {})
            for key, trend_info in trends.items():
                trend = trend_info.get('trend')
                mom = trend_info.get('mom_growth')
                if trend == "decreasing" and mom is not None and mom < -5:
                    insights.append(Insight(
                        finding=f"Decreasing trend in {trend_info['metric']} — MoM {mom:.1f}%",
                        evidence={"metric": trend_info['metric'], "trend": trend, "mom": mom, "peak": str(trend_info.get('peak'))},
                        business_meaning="Declining metric needs immediate attention — could be seasonality or real drop.",
                        recommendation="Investigate drivers: compare categories, regions, check marketing spend, seasonality.",
                        severity="warning",
                        confidence="high",
                        type="CalculatedInsight",
                        source="timeseries"
                    ))
                if mom is not None and mom > 20:
                    insights.append(Insight(
                        finding=f"Strong growth in {trend_info['metric']} — MoM +{mom:.1f}%",
                        evidence={"metric": trend_info['metric'], "mom": mom},
                        business_meaning="Positive momentum — opportunity to double down.",
                        recommendation="Identify growth drivers, replicate successful tactics to other segments.",
                        severity="info",
                        confidence="high",
                        type="CalculatedInsight",
                        source="timeseries"
                    ))

        # Deduplicate and limit to top
        # Sort by severity critical first
        severity_order = {"critical":0, "warning":1, "info":2}
        insights_sorted = sorted(insights, key=lambda x: severity_order.get(x.severity, 3))

        return insights_sorted[:12]  # limit

    except Exception as e:
        # Return error insight
        return [Insight(
            finding=f"Insight generation partially failed: {e}",
            evidence={"error": str(e)},
            business_meaning="Some insights may be missing due to data issues.",
            recommendation="Check data quality and ensure sufficient numeric/categorical columns.",
            severity="warning",
            confidence="low",
            type="CalculatedInsight",
            source="insight_engine"
        )]
