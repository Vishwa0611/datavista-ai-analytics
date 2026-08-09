"""
Constants for InsightForge — no magic strings scattered across codebase.
"""
from enum import Enum

# File handling
SUPPORTED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.json', '.parquet'}
MAX_FILE_SIZE_MB = 200
PREVIEW_ROWS = 100

# Column type enums
class ColumnType(str, Enum):
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    ID = "id"
    TEXT = "text"
    PII = "pii"
    CONSTANT = "constant"
    UNKNOWN = "unknown"

# Domain types
class Domain(str, Enum):
    ECOMMERCE = "ecommerce"
    MARKETING = "marketing"
    HR = "hr"
    SAAS = "saas"
    FINANCE = "finance"
    OPERATIONS = "operations"
    SPORTS = "sports"
    UNKNOWN = "unknown"

# Cleaning operations
class CleaningOp(str, Enum):
    REMOVE_DUPLICATES = "remove_duplicates"
    FILL_NUM_MEAN = "fill_num_mean"
    FILL_NUM_MEDIAN = "fill_num_median"
    FILL_CAT_MODE = "fill_cat_mode"
    DROP_COL = "drop_col"
    RENAME_COL = "rename_col"
    CONVERT_DTYPE = "convert_dtype"
    PARSE_DATES = "parse_dates"
    TRIM_WHITESPACE = "trim_whitespace"
    STANDARDIZE_CASE = "standardize_case"
    CAP_OUTLIERS = "cap_outliers"
    REMOVE_OUTLIERS = "remove_outliers"
    DROP_ROWS_MISSING = "drop_rows_missing"

# Quality scoring weights
QUALITY_WEIGHTS = {
    "completeness": 0.40,
    "record_uniqueness": 0.20,
    "validity": 0.20,
    "consistency": 0.20
}

# Chart colors — colorblind-safe, muted
CHART_PALETTE = [
    "#6366F1", "#10B981", "#F59E0B", "#8B5CF6",
    "#EC4899", "#06B6D4", "#84CC16", "#F97316"
]

# Regex patterns for PII — careful, Indian context Aadhaar etc
PII_PATTERNS = {
    "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "phone_in": r"(\+91[\-\s]?)?[0]?(91)?[789]\d{9}",
    "phone_us": r"(\+1[\-\s]?)?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{4}",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "aadhaar": r"\b\d{4}\s?\d{4}\s?\d{4}\b"
}

# Domain keyword dictionaries for detection
DOMAIN_KEYWORDS = {
    Domain.ECOMMERCE: [
        "revenue", "sales", "order", "price", "quantity", "product", "customer",
        "profit", "discount", "transaction", "cart", "purchase", "sku", "inventory",
        "payment", "shipping", "aov", "average order"
    ],
    Domain.MARKETING: [
        "spend", "impression", "click", "ctr", "conversion", "cpa", "roas",
        "campaign", "ad", "channel", "cpc", "cpm", "lead", "acquisition",
        "marketing", "budget", "roi"
    ],
    Domain.HR: [
        "employee", "salary", "attrition", "tenure", "department", "performance",
        "hire", "resignation", "engagement", "absenteeism", "job", "role",
        "experience", "appraisal"
    ],
    Domain.SAAS: [
        "mrr", "arr", "churn", "ltv", "subscription", "plan", "customer",
        "retention", "cohort", "activation", "trial", "renewal", "license"
    ],
    Domain.FINANCE: [
        "profit", "loss", "cost", "expense", "budget", "margin", "ebitda",
        "cash", "flow", "balance", "accounting", "invoice"
    ],
    Domain.OPERATIONS: [
        "delivery", "logistics", "warehouse", "inventory", "stock", "supply",
        "lead time", "fulfillment", "on-time", "defect", "operation"
    ],
    Domain.SPORTS: [
        "player", "team", "match", "goal", "assist", "tournament", "stadium",
        "position", "market_value", "rating", "performance", "minutes_played",
        "shots", "passes", "tackles", "nationality", "club", "jersey"
    ]
}

# KPI Definitions — domain → list of KPIs
# Fixed: Revenue vs Sales consistency, added Total Profit, improved naming
DOMAIN_KPI_CONFIG = {
    Domain.ECOMMERCE: [
        {"name": "Total Sales", "aliases": [["total sales", "sales", "revenue", "total_sales", "amount"]], "formula": "SUM(Sales)", "unit": "currency"},
        {"name": "Total Profit", "aliases": [["profit", "total_profit", "net_profit"]], "formula": "SUM(Profit)", "unit": "currency"},
        {"name": "Total Units Sold", "aliases": [["units sold", "units_sold", "quantity", "qty", "units"]], "formula": "SUM(Units Sold)", "unit": "count"},
        {"name": "Average Sales", "aliases": [["average sales", "avg sales", "mean sales", "total sales", "sales"]], "formula": "AVG(Sales)", "unit": "currency"},
        {"name": "Average Unit Price", "aliases": [["unit price", "unit_price", "average unit price", "price"]], "formula": "AVG(Unit Price)", "unit": "currency"},
        {"name": "Total Orders", "aliases": [["order_id", "order", "transaction_id", "order_number"]], "formula": "COUNT_DISTINCT(order_id)", "unit": "count"},
        {"name": "Average Order Value", "aliases": [["sales", "revenue"], ["order_id", "order"]], "formula": "Total Sales / Total Orders", "unit": "currency"},
        {"name": "Total Customers", "aliases": [["customer_id", "customer", "client_id", "user_id"]], "formula": "COUNT_DISTINCT(customer_id)", "unit": "count"},
        {"name": "Profit Margin", "aliases": [["profit", "margin"], ["sales", "revenue"]], "formula": "SUM(Profit) / SUM(Sales) * 100", "unit": "percent"},
        {"name": "Discount Impact", "aliases": [["discount", "discount_pct"]], "formula": "AVG(discount)", "unit": "percent"},
    ],
    Domain.MARKETING: [
        {"name": "Total Spend", "aliases": [["spend", "cost", "budget"]], "formula": "SUM(spend)", "unit": "currency"},
        {"name": "CTR", "aliases": [["clicks", "click"], ["impressions", "impression"]], "formula": "Clicks / Impressions *100", "unit": "percent"},
        {"name": "Conversion Rate", "aliases": [["conversion", "conversions", "converted"], ["clicks", "visits"]], "formula": "Conversions / Clicks *100", "unit": "percent"},
        {"name": "ROAS", "aliases": [["sales", "revenue"], ["spend", "cost"]], "formula": "Sales / Spend", "unit": "ratio"},
        {"name": "CPA", "aliases": [["spend", "cost"], ["conversion", "conversions"]], "formula": "Spend / Conversions", "unit": "currency"},
    ],
    Domain.HR: [
        {"name": "Attrition Rate", "aliases": [["attrition", "left", "resigned", "status"]], "formula": "Count Attrited / Total *100", "unit": "percent"},
        {"name": "Average Salary", "aliases": [["salary", "compensation", "pay"]], "formula": "AVG(salary)", "unit": "currency"},
        {"name": "Average Tenure", "aliases": [["tenure", "years_at_company", "service"]], "formula": "AVG(tenure)", "unit": "years"},
    ],
    Domain.SAAS: [
        {"name": "Churn Rate", "aliases": [["churn", "churned", "retention", "status"]], "formula": "COUNT(Churned) / COUNT(*) *100", "unit": "percent"},
        {"name": "MRR", "aliases": [["mrr", "monthly_recurring_revenue", "revenue"]], "formula": "SUM(MRR)", "unit": "currency"},
        {"name": "Average Tenure", "aliases": [["tenure", "tenure_months", "months"]], "formula": "AVG(tenure)", "unit": "months"},
        {"name": "Active Customers", "aliases": [["status", "active", "subscription"]], "formula": "COUNT(Active)", "unit": "count"},
    ],
    Domain.SPORTS: [
        {"name": "Total Goals", "aliases": [["goals", "total_goals", "goals_scored"]], "formula": "SUM(goals)", "unit": "count"},
        {"name": "Total Assists", "aliases": [["assists", "total_assists"]], "formula": "SUM(assists)", "unit": "count"},
        {"name": "Average Player Rating", "aliases": [["player_rating", "rating", "tournament_rating"]], "formula": "AVG(rating)", "unit": "ratio"},
        {"name": "Average Market Value", "aliases": [["market_value_eur", "market_value", "value"]], "formula": "AVG(market_value)", "unit": "currency"},
        {"name": "Goals per 90", "aliases": [["goals"], ["minutes_played", "minutes", "total_minutes"]], "formula": "(SUM(goals)/SUM(minutes))*90", "unit": "ratio"},
        {"name": "Total Minutes Played", "aliases": [["minutes_played", "minutes", "total_minutes"]], "formula": "SUM(minutes_played)", "unit": "count"},
    ]
}
