"""
Generate showcase SQL queries demonstrating SQL skills.
"""
from typing import List, Dict, Any
import pandas as pd

def generate_showcase_queries(
    df: pd.DataFrame,
    table_name: str = "raw_data",
    numeric_cols: List[str] = None,
    categorical_cols: List[str] = None,
    date_cols: List[str] = None
) -> List[Dict[str, Any]]:
    numeric_cols = numeric_cols or []
    categorical_cols = categorical_cols or []
    date_cols = date_cols or []

    queries = []

    # 1. Basic SELECT + WHERE
    if numeric_cols:
        col = numeric_cols[0]
        queries.append({
            "title": "Basic Filtering (SELECT + WHERE)",
            "category": "SELECT/WHERE",
            "description": f"Filter rows where {col} is above average — demonstrates WHERE and aggregation in subquery",
            "sql": f"SELECT * FROM {table_name} WHERE {col} > (SELECT AVG({col}) FROM {table_name}) LIMIT 100;"
        })

    # 2. GROUP BY + Aggregation
    if categorical_cols and numeric_cols:
        cat = categorical_cols[0]
        num = numeric_cols[0]
        queries.append({
            "title": "Revenue by Category (GROUP BY)",
            "category": "GROUP BY",
            "description": "GROUP BY with SUM, AVG, COUNT — core business reporting",
            "sql": f"SELECT {cat}, COUNT(*) as count, SUM({num}) as total_{num}, AVG({num}) as avg_{num} FROM {table_name} GROUP BY {cat} ORDER BY total_{num} DESC;"
        })

    # 3. HAVING
    if categorical_cols and numeric_cols:
        cat = categorical_cols[0]
        num = numeric_cols[0]
        queries.append({
            "title": "HAVING — Filter Groups",
            "category": "HAVING",
            "description": "HAVING filters after GROUP BY — finds categories with high volume",
            "sql": f"SELECT {cat}, SUM({num}) as total FROM {table_name} GROUP BY {cat} HAVING SUM({num}) > 1000 ORDER BY total DESC;"
        })

    # 4. CASE WHEN
    if numeric_cols:
        num = numeric_cols[0]
        queries.append({
            "title": "Segmentation with CASE WHEN",
            "category": "CASE WHEN",
            "description": "CASE WHEN creates buckets — e.g., low/medium/high value",
            "sql": f"SELECT {num}, CASE WHEN {num} < 100 THEN 'Low' WHEN {num} < 500 THEN 'Medium' ELSE 'High' END as value_segment FROM {table_name} LIMIT 100;"
        })

    # 5. CTE
    if categorical_cols and numeric_cols:
        cat = categorical_cols[0]
        num = numeric_cols[0]
        queries.append({
            "title": "Top Customers via CTE",
            "category": "CTE",
            "description": "Common Table Expression for readability and modular queries",
            "sql": f"WITH customer_totals AS (SELECT {cat}, SUM({num}) as total FROM {table_name} GROUP BY {cat}) SELECT * FROM customer_totals ORDER BY total DESC LIMIT 10;"
        })

    # 6. Window Function RANK
    if categorical_cols and numeric_cols:
        cat = categorical_cols[0]
        num = numeric_cols[0]
        queries.append({
            "title": "Ranking with Window Function (RANK)",
            "category": "Window Functions",
            "description": "RANK() OVER (ORDER BY) — top N per business without LIMIT tricks",
            "sql": f"SELECT {cat}, SUM({num}) as total, RANK() OVER (ORDER BY SUM({num}) DESC) as rank FROM {table_name} GROUP BY {cat} ORDER BY rank LIMIT 10;"
        })

    # 7. Window LAG for MoM
    if date_cols and numeric_cols:
        dcol = date_cols[0]
        num = numeric_cols[0]
        queries.append({
            "title": "Month-over-Month Growth (LAG)",
            "category": "Window Functions",
            "description": "LAG() to compare current vs previous period — essential for MoM/YoY analysis",
            "sql": f"WITH monthly AS (SELECT DATE_TRUNC('month', {dcol}) as month, SUM({num}) as revenue FROM {table_name} GROUP BY month) SELECT month, revenue, LAG(revenue) OVER (ORDER BY month) as prev_month, (revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month) *100 as growth_pct FROM monthly ORDER BY month;"
        })

    # 8. Date Trunc analysis
    if date_cols and numeric_cols:
        dcol = date_cols[0]
        num = numeric_cols[0]
        queries.append({
            "title": "Time Series Aggregation (DATE_TRUNC)",
            "category": "Date Analysis",
            "description": "DATE_TRUNC groups by month/quarter/year for trend analysis",
            "sql": f"SELECT DATE_TRUNC('month', {dcol}) as month, SUM({num}) as total FROM {table_name} GROUP BY DATE_TRUNC('month', {dcol}) ORDER BY month;"
        })

    # 9. Multiple JOIN example (self-join concept)
    if categorical_cols:
        cat = categorical_cols[0]
        queries.append({
            "title": "Self-Join Concept — Compare Categories",
            "category": "JOIN",
            "description": "JOIN to compare categories side by side (illustrative — uses CTEs as tables)",
            "sql": f"WITH a AS (SELECT {cat}, AVG({numeric_cols[0]}) as avg_val FROM {table_name} GROUP BY {cat}) SELECT a1.{cat} as cat1, a2.{cat} as cat2, a1.avg_val, a2.avg_val FROM a a1 JOIN a a2 ON a1.avg_val > a2.avg_val LIMIT 20;"
        })

    # 10. Aggregation with DISTINCT
    if numeric_cols and categorical_cols:
        queries.append({
            "title": "COUNT DISTINCT & Statistical",
            "category": "Aggregation",
            "description": "COUNT DISTINCT, STDDEV, percentiles — descriptive stats in SQL",
            "sql": f"SELECT COUNT(DISTINCT {categorical_cols[0]}) as unique_{categorical_cols[0]}, AVG({numeric_cols[0]}) as avg_{numeric_cols[0]}, STDDEV({numeric_cols[0]}) as stddev, MIN({numeric_cols[0]}) as min_val, MAX({numeric_cols[0]}) as max_val FROM {table_name};"
        })

    return queries
