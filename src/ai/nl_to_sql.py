"""
Natural Language to SQL — Fixed v2
Handles:
- Metric prefers numeric, dimension prefers categorical
- "X by Y" both orders: products by profit AND count orders by payment method
- Underscore vs space: payment_method matches "payment method"
- Date casting: CAST(date_col AS DATE) for VARCHAR dates
- No SUM(text) or AVG(categorical) — fallback to COUNT
"""
import re
from typing import Dict, Any, List, Optional

def _normalize(s: str) -> str:
    return s.lower().replace('_', ' ').replace('-', ' ').strip()

def detect_intent(
    query: str, 
    columns: List[str],
    numeric_cols: List[str] = None,
    categorical_cols: List[str] = None,
    date_cols: List[str] = None
) -> Dict[str, Any]:
    q_lower = query.lower()
    q_normalized = _normalize(query)
    
    numeric_cols = numeric_cols or []
    categorical_cols = categorical_cols or []
    date_cols = date_cols or []
    
    intent = {
        "metric": None, 
        "dimension": None, 
        "aggregation": "sum", 
        "time_grain": None, 
        "filter": None, 
        "top_n": None, 
        "chart_type": "bar"
    }

    cols_lower = {c.lower(): c for c in columns}
    cols_norm = {_normalize(c): c for c in columns}
    numeric_lower = {c.lower(): c for c in numeric_cols}
    numeric_norm = {_normalize(c): c for c in numeric_cols}
    categorical_lower = {c.lower(): c for c in categorical_cols}
    categorical_norm = {_normalize(c): c for c in categorical_cols}
    date_lower = {c.lower(): c for c in date_cols}
    date_norm = {_normalize(c): c for c in date_cols}

    # Time grain
    if "monthly" in q_lower or " per month" in q_lower:
        intent["time_grain"] = "month"
        intent["chart_type"] = "line"
    elif "weekly" in q_lower:
        intent["time_grain"] = "week"
        intent["chart_type"] = "line"
    elif "yearly" in q_lower or " annual" in q_lower:
        intent["time_grain"] = "year"
        intent["chart_type"] = "line"
    elif "daily" in q_lower:
        intent["time_grain"] = "day"
        intent["chart_type"] = "line"

    # Aggregation
    if "average" in q_lower or " avg " in q_lower:
        intent["aggregation"] = "avg"
    elif re.search(r'\bcount\b', q_lower):
        intent["aggregation"] = "count"
    elif "max" in q_lower or "maximum" in q_lower or "highest" in q_lower:
        intent["aggregation"] = "max"
    elif "min" in q_lower or "minimum" in q_lower or "lowest" in q_lower:
        intent["aggregation"] = "min"
    else:
        intent["aggregation"] = "sum"

    # Top N
    top_match = re.search(r'top\s+(\d+)', q_lower)
    if top_match:
        intent["top_n"] = int(top_match.group(1))
        intent["chart_type"] = "bar"
    elif "top" in q_lower:
        intent["top_n"] = 10

    if "growth" in q_lower or "trend" in q_lower:
        intent["chart_type"] = "line"
        intent["time_grain"] = intent["time_grain"] or "month"

    # Helper to find column in text (handles underscore vs space)
    def find_cols_in_text(text: str, col_dict_lower: dict, col_dict_norm: dict) -> List[str]:
        found = []
        for low, orig in col_dict_lower.items():
            if low in text:
                found.append(orig)
        for norm, orig in col_dict_norm.items():
            if norm in text and orig not in found:
                found.append(orig)
        return found

    # Parse "X by Y"
    by_parts = q_lower.split(" by ")
    by_parts_norm = q_normalized.split(" by ")
    
    if len(by_parts) == 2:
        before_by = by_parts[0]
        after_by = by_parts[1]
        before_norm = by_parts_norm[0]
        after_norm = by_parts_norm[1]
        
        numeric_in_before = find_cols_in_text(before_by, numeric_lower, numeric_norm) + find_cols_in_text(before_norm, numeric_lower, numeric_norm)
        numeric_in_after = find_cols_in_text(after_by, numeric_lower, numeric_norm) + find_cols_in_text(after_norm, numeric_lower, numeric_norm)
        categorical_in_before = find_cols_in_text(before_by, categorical_lower, categorical_norm) + find_cols_in_text(before_norm, categorical_lower, categorical_norm)
        categorical_in_after = find_cols_in_text(after_by, categorical_lower, categorical_norm) + find_cols_in_text(after_norm, categorical_lower, categorical_norm)
        
        # Deduplicate
        numeric_in_before = list(dict.fromkeys(numeric_in_before))
        numeric_in_after = list(dict.fromkeys(numeric_in_after))
        categorical_in_before = list(dict.fromkeys(categorical_in_before))
        categorical_in_after = list(dict.fromkeys(categorical_in_after))
        
        has_count = "count" in q_lower or "number of" in q_lower
        
        metric_candidate = None
        dimension_candidate = None
        
        # Heuristic 1: after has categorical and before has count/numeric -> after is dimension (count orders by payment method)
        if categorical_in_after and (numeric_in_before or has_count):
            dimension_candidate = categorical_in_after[0]
            if numeric_in_before:
                metric_candidate = numeric_in_before[0]
        # Heuristic 2: before has categorical and after has numeric -> before dimension, after metric (products by profit)
        elif categorical_in_before and numeric_in_after:
            dimension_candidate = categorical_in_before[0]
            metric_candidate = numeric_in_after[0]
        # Heuristic 3: before has categorical, after has nothing, but has_count -> dimension is after, count
        elif has_count and categorical_in_after:
            dimension_candidate = categorical_in_after[0]
        elif has_count and categorical_in_before and not numeric_in_before:
            # "Count orders by payment method" where orders is not detected as numeric but count present
            # If before contains "order" and after contains payment_method, dimension = payment_method
            if categorical_in_after:
                dimension_candidate = categorical_in_after[0]
            elif categorical_in_before:
                # If multiple categorical in before, pick the one that is not order-like?
                # For "count orders by payment method", before has order_id (contains order) and maybe payment?
                # We want payment method
                # So if categorical_in_before has more than 1, prefer the one that appears after "by" in original
                dimension_candidate = categorical_in_after[0] if categorical_in_after else (categorical_in_before[0] if categorical_in_before else None)
        
        # Fallback: if still not found, try general
        if not metric_candidate and not dimension_candidate:
            # Try to find metric in after, dimension in before (original)
            if numeric_in_after:
                metric_candidate = numeric_in_after[0]
            if categorical_in_before and not dimension_candidate:
                dimension_candidate = categorical_in_before[0]
            if not dimension_candidate and categorical_in_after:
                dimension_candidate = categorical_in_after[0]
            if not metric_candidate and numeric_in_before and not dimension_candidate:
                metric_candidate = numeric_in_before[0]
        
        if metric_candidate or dimension_candidate:
            intent["metric"] = metric_candidate
            intent["dimension"] = dimension_candidate
            return intent

    # No "by" pattern — general search with type preference
    # Metric: prefer numeric
    for low, orig in numeric_lower.items():
        if low in q_lower or _normalize(low) in q_normalized:
            intent["metric"] = orig
            break
    # Also check normalized
    if not intent["metric"]:
        for norm, orig in numeric_norm.items():
            if norm in q_normalized:
                intent["metric"] = orig
                break
    
    # Dimension: prefer categorical
    for low, orig in categorical_lower.items():
        if (low in q_lower or _normalize(low) in q_normalized) and orig != intent["metric"]:
            intent["dimension"] = orig
            break
    if not intent["dimension"]:
        for norm, orig in categorical_norm.items():
            if norm in q_normalized and orig != intent["metric"]:
                intent["dimension"] = orig
                break
    
    # Date as dimension fallback
    if not intent["dimension"]:
        for low, orig in date_lower.items():
            if low in q_lower or _normalize(low) in q_normalized:
                if orig != intent["metric"]:
                    intent["dimension"] = orig
                    break

    return intent

def intent_to_sql(
    intent: Dict[str, Any], 
    table_name: str = "cleaned_data", 
    columns: List[str] = None,
    numeric_cols: List[str] = None,
    categorical_cols: List[str] = None,
    date_cols: List[str] = None
) -> Optional[str]:
    metric = intent.get("metric")
    dimension = intent.get("dimension")
    agg = intent.get("aggregation", "sum")
    grain = intent.get("time_grain")
    top_n = intent.get("top_n")

    numeric_cols = numeric_cols or []
    categorical_cols = categorical_cols or []
    date_cols = date_cols or []

    def safe_col(col_name: str) -> str:
        if ' ' in col_name or '-' in col_name:
            return f'"{col_name}"'
        return col_name

    def is_date_col(col_name: str) -> bool:
        return col_name in date_cols

    def is_numeric_col(col_name: str) -> bool:
        return col_name in numeric_cols

    def is_categorical_col(col_name: str) -> bool:
        return col_name in categorical_cols

    if not metric and not dimension and not grain:
        return None

    # Ensure metric is numeric for sum/avg/max/min
    if metric and agg != "count" and not is_numeric_col(metric):
        # If metric is not numeric, treat as dimension and use COUNT
        if not dimension:
            dimension = metric
        metric = None
        agg = "count"

    # Time series
    if grain:
        date_col = None
        if dimension and is_date_col(dimension):
            date_col = dimension
            dimension = None
        elif date_cols:
            date_col = date_cols[0]
        
        if date_col:
            date_col_casted = f"CAST({safe_col(date_col)} AS DATE)"
            if metric:
                if agg == "avg":
                    agg_func = f"AVG({safe_col(metric)})"
                elif agg == "count":
                    agg_func = f"COUNT(*)"
                elif agg == "max":
                    agg_func = f"MAX({safe_col(metric)})"
                elif agg == "min":
                    agg_func = f"MIN({safe_col(metric)})"
                else:
                    agg_func = f"SUM({safe_col(metric)})"
                sql = f"SELECT DATE_TRUNC('{grain}', {date_col_casted}) as period, {agg_func} as value FROM {table_name} WHERE {date_col_casted} IS NOT NULL GROUP BY period ORDER BY period"
            else:
                sql = f"SELECT DATE_TRUNC('{grain}', {date_col_casted}) as period, COUNT(*) as count FROM {table_name} WHERE {date_col_casted} IS NOT NULL GROUP BY period ORDER BY period"
            return sql

    # Dimension + Metric
    if dimension and metric:
        # Swap check: if dimension is numeric and metric is categorical, swap
        if is_numeric_col(dimension) and is_categorical_col(metric):
            dimension, metric = metric, dimension

        if agg == "avg":
            agg_func = f"AVG({safe_col(metric)})"
        elif agg == "count":
            agg_func = f"COUNT(*)"
        elif agg == "max":
            agg_func = f"MAX({safe_col(metric)})"
        elif agg == "min":
            agg_func = f"MIN({safe_col(metric)})"
        else:
            agg_func = f"SUM({safe_col(metric)})"

        limit_clause = f" LIMIT {top_n}" if top_n else ""
        sql = f"SELECT {safe_col(dimension)}, {agg_func} as value FROM {table_name} GROUP BY {safe_col(dimension)} ORDER BY value DESC{limit_clause}"
        return sql

    # Metric only
    if metric and not dimension:
        if agg == "avg":
            sql = f"SELECT AVG({safe_col(metric)}) as value FROM {table_name}"
        elif agg == "count":
            sql = f"SELECT COUNT(*) as count FROM {table_name}"
        elif agg == "sum":
            sql = f"SELECT SUM({safe_col(metric)}) as total FROM {table_name}"
        elif agg == "max":
            sql = f"SELECT MAX({safe_col(metric)}) as max_value FROM {table_name}"
        elif agg == "min":
            sql = f"SELECT MIN({safe_col(metric)}) as min_value FROM {table_name}"
        else:
            sql = f"SELECT {agg.upper()}({safe_col(metric)}) as value FROM {table_name}"
        return sql

    # Dimension only
    if dimension and not metric:
        limit_clause = f" LIMIT {top_n}" if top_n else " LIMIT 20"
        sql = f"SELECT {safe_col(dimension)}, COUNT(*) as count FROM {table_name} GROUP BY {safe_col(dimension)} ORDER BY count DESC{limit_clause}"
        return sql

    return None

def nl_to_sql_pipeline(
    query: str, 
    columns: List[str], 
    table_name: str = "cleaned_data", 
    date_columns: List[str] = None,
    numeric_cols: List[str] = None,
    categorical_cols: List[str] = None
) -> Dict[str, Any]:
    date_columns = date_columns or []
    numeric_cols = numeric_cols or []
    categorical_cols = categorical_cols or []
    
    intent = detect_intent(
        query, 
        columns, 
        numeric_cols=numeric_cols,
        categorical_cols=categorical_cols,
        date_cols=date_columns
    )

    sql = intent_to_sql(
        intent, 
        table_name, 
        columns,
        numeric_cols=numeric_cols,
        categorical_cols=categorical_cols,
        date_cols=date_columns
    )

    if not sql:
        return {
            "success": False,
            "sql": None,
            "intent": intent,
            "explanation": "Could not understand query — try 'Show monthly sales', 'Top 10 products by profit', 'Count orders by payment method' (use 'by' to separate dimension and metric)"
        }

    expl = f"Metric: {intent.get('metric')} (numeric), Dimension: {intent.get('dimension')} (categorical), Agg: {intent.get('aggregation')}"
    if intent.get("time_grain"):
        expl += f", Time: {intent.get('time_grain')}"

    return {
        "success": True,
        "sql": sql,
        "intent": intent,
        "explanation": expl
    }
