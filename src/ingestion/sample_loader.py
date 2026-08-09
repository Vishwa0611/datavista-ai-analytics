"""
Sample dataset manager for demo mode.
"""
from pathlib import Path
from typing import List, Dict

SAMPLE_DATASETS = {
    "ecommerce_sales": {
        "title": "E-commerce Sales Analytics",
        "description": "12K orders, revenue, profit, customers, products, regions, 24 months — ideal for KPI, Pareto, RFM",
        "rows": 12500,
        "domain": "ecommerce",
        "file": "ecommerce_sales.csv"
    },
    "marketing_campaigns": {
        "title": "Marketing Campaign Performance",
        "description": "Campaign spend, impressions, clicks, conversions, CTR, CPA, ROAS by channel — funnel & ROI",
        "rows": 3400,
        "domain": "marketing",
        "file": "marketing_campaigns.csv"
    },
    "saas_customers": {
        "title": "SaaS Customer Retention",
        "description": "Subscription plans, MRR, churn, tenure, engagement — churn analysis & cohort",
        "rows": 5800,
        "domain": "saas",
        "file": "saas_customers.csv"
    }
}

def get_sample_list() -> List[Dict]:
    return [{"id": k, **v} for k, v in SAMPLE_DATASETS.items()]

def get_sample_path(name: str) -> Path:
    base = Path(__file__).parent.parent.parent / "sample_data"
    return base / SAMPLE_DATASETS[name]["file"]
