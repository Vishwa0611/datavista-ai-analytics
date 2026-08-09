# Data Dictionary — Synthetic Sample Datasets

**All datasets are synthetic, realistic, labeled as synthetic — no real company data, no PII.**

## 1. E-commerce Sales Analytics — `ecommerce_sales.csv` — 12,512 rows

**Domain:** E-commerce
**Purpose:** Demonstrates revenue, profit, AOV, margin, Pareto, RFM, time series, duplicate detection, missing, inconsistent labels

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| order_id | ID | Unique order identifier ORD-000001 | 12 duplicates for quality demo |
| customer_id | Categorical | Customer ID CUST-xxxxx | 2486 unique, for segmentation |
| order_date | DateTime | Order timestamp 2023-01-01 to 2024-12-31 | For time series, MoM/YoY |
| product | Categorical | Product name (Laptop Pro, Phone X, etc.) | 8 products |
| category | Categorical | Electronics, Accessories, Wearables | 3 categories, Pareto |
| region | Categorical | North, South, East, West, Central | Intentional inconsistent: North vs north vs " North" |
| quantity | Numerical | Qty per order 1-4 | |
| price | Numerical | Unit price 50-1550 | |
| discount_pct | Numerical | Discount % 0-25 | For KPI Discount Impact |
| revenue | Numerical | price*qty*(1-discount) | Right skewed, 14 outliers *5 |
| profit | Numerical | revenue - cost*qty | For margin KPI |
| customer_age | Numerical | 18-70, 7.2% missing | Missing demo |
| payment_method | Categorical | Credit Card, PayPal, UPI, Net Banking | 15 blank strings for quality |
| shipping_status | Categorical | Delivered, Shipped, Processing, Returned | |

**Intentional quality issues for demo:**
- 12 duplicate rows (0.1%)
- 7.2% missing customer_age
- 3 inconsistent region labels
- 14 outliers in revenue
- 30 blank/whitespace region, 15 blank payment_method

## 2. Marketing Campaign Performance — `marketing_campaigns.csv` — 3400 rows

**Domain:** Marketing
**Purpose:** CTR, CPA, ROAS, funnel, ROI, channel comparison

| Column | Type | Description |
|--------|------|-------------|
| campaign_id | Categorical | CMP-0001 to CMP-0050 | 
| channel | Categorical | Google Ads, Facebook, Instagram, LinkedIn, Email, Organic, YouTube |
| date | DateTime | 2023-01-01 to 2024-12-31 |
| impressions | Numerical | 1000-100000 |
| clicks | Numerical | impressions * 1-8% |
| conversions | Numerical | clicks * 2-15% |
| spend | Numerical | 100-5000, 50 missing |
| revenue | Numerical | conversions * 50-500 |
| ctr | Numerical | clicks/impressions*100 |
| cpa | Numerical | spend/conversions |
| roas | Numerical | revenue/spend |

## 3. SaaS Customer Retention — `saas_customers.csv` — 5800 rows

**Domain:** SaaS
**Purpose:** Churn, MRR, tenure, engagement, cohort-like

| Column | Type | Description |
|--------|------|-------------|
| customer_id | ID | CUST-00001 etc |
| plan | Categorical | Starter, Growth, Professional, Enterprise |
| status | Categorical | Active (70%), Churned (20%), Trial (10%) |
| signup_date | DateTime | 2022-01-01 to 2024-12-31 |
| tenure_months | Numerical | Months since signup |
| mrr | Numerical | Monthly recurring revenue per plan |
| engagement_score | Numerical | 1-100, lower if churned, 100 missing |
| support_tickets | Numerical | 0-15 |
| last_active_date | DateTime | Last activity |

**Use Cases:**
- E-commerce: best for portfolio demo — covers most modules
- Marketing: best for ROAS, CTR, funnel analysis
- SaaS: best for churn, tenure, engagement
