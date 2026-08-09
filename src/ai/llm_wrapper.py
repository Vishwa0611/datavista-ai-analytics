"""
Optional LLM wrapper — with strict hallucination guards.
Only sends aggregated metrics, never raw PII rows.
"""
import os
from typing import Dict, Any, List, Optional

SYSTEM_PROMPT = """
You are a Senior Data Analyst Assistant inside InsightForge — Intelligent Analytics Workbench.

CRITICAL RULES — MUST FOLLOW:
1. You may ONLY use numbers provided in the JSON metrics context. Never invent metrics, rows, or statistical results.
2. Every insight must reference evidence: which metric, which value, from which calculation.
3. Never claim causation without evidence. Say "correlation does not imply causation" where appropriate.
4. If evidence insufficient, say "Evidence insufficient — requires further analysis".
5. Do NOT make high-stakes decisions about individuals (hiring, firing, lending).
6. Avoid PII conclusions.
7. Structure each insight as: Finding → Evidence → Business Meaning → Recommended Action.
8. Use plain business language, not hype.
9. Clearly label that you are interpretation layer over calculated results.

You will receive JSON with:
- quality_score
- kpis (name, value, formula)
- top correlations
- significant tests
- segmentation hints
- time series trends

Your task: provide 3-5 top executive insights based ONLY on that JSON.

If user asks a generic question not covered by metrics, answer based on metrics or say insufficient evidence.
"""

def build_metrics_context(pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build safe context — only aggregated metrics, no raw rows.
    """
    context = {}
    try:
        quality = pipeline_data.get('quality')
        if quality:
            context['quality_score'] = quality.score
            context['quality_breakdown'] = quality.score_breakdown
            context['top_issues'] = [{"col": i.column, "desc": i.description} for i in quality.issues[:5]]

        kpi_data = pipeline_data.get('kpi')
        if kpi_data:
            context['kpis'] = [{"name": k.name, "value": str(k.value), "formula": k.formula, "available": k.available} for k in kpi_data.get('kpis', [])[:10] if k.available]

        stats_data = pipeline_data.get('statistics')
        if stats_data:
            corr = stats_data.get('correlation', {})
            context['top_correlations'] = [{"col1": c.col1, "col2": c.col2, "r": c.pearson_r, "p": c.pearson_p} for c in corr.get('results', [])[:3]]
            context['hypothesis_tests'] = [{"test": t.test_name, "p": t.p_value, "decision": t.decision} for t in stats_data.get('hypothesis_tests', [])[:3]]

        seg_data = pipeline_data.get('segmentation')
        if seg_data:
            # Only summary, not full RFM table
            rfm = seg_data.get('rfm', {})
            if rfm.get('available'):
                context['segmentation'] = {"rfm_segments": rfm.get('segment_counts', {})}

        ts_data = pipeline_data.get('timeseries')
        if ts_data:
            trends = ts_data.get('trends', {}).get('trends', {})
            context['time_trends'] = [{"key": k, "trend": v.get('trend'), "mom": v.get('mom_growth')} for k,v in list(trends.items())[:2]]

    except Exception as e:
        context['error'] = str(e)

    return context

def call_llm_if_configured(prompt: str, metrics_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calls OpenAI or Groq if API key present in env. Otherwise returns fallback.
    """
    api_key_openai = os.getenv("OPENAI_API_KEY")
    api_key_groq = os.getenv("GROQ_API_KEY")

    # If no keys, return deterministic fallback
    if not api_key_openai and not api_key_groq:
        return {
            "available": False,
            "reason": "No LLM API key configured — using deterministic insights engine. Add OPENAI_API_KEY in .env to enable AI interpretation.",
            "response": None
        }

    # Build final prompt
    import json
    context_str = json.dumps(metrics_context, indent=2, default=str)
    full_prompt = f"{SYSTEM_PROMPT}\n\nMETRICS CONTEXT (ONLY USE THESE NUMBERS):\n{context_str}\n\nUSER QUESTION: {prompt}\n\nProvide insights as per structure. If asked generic question, answer using only context numbers."

    # Try OpenAI
    try:
        if api_key_openai:
            from openai import OpenAI
            client = OpenAI(api_key=api_key_openai)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.2,
                max_tokens=800
            )
            return {"available": True, "response": response.choices[0].message.content, "provider": "openai"}

        if api_key_groq:
            from openai import OpenAI
            client = OpenAI(api_key=api_key_groq, base_url="https://api.groq.com/openai/v1")
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.2,
                max_tokens=800
            )
            return {"available": True, "response": response.choices[0].message.content, "provider": "groq"}

    except Exception as e:
        return {"available": False, "reason": f"LLM call failed: {e}", "response": None}

    return {"available": False, "reason": "No provider succeeded", "response": None}
