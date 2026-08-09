"""
Generate realistic synthetic datasets for demo.
Clearly labeled synthetic.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

os.makedirs(os.path.dirname(__file__), exist_ok=True)

np.random.seed(42)
random.seed(42)

def gen_ecommerce():
    n = 12500
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = pd.date_range(start_date, end_date, freq='D')

    # Generate data
    order_ids = [f"ORD-{i:06d}" for i in range(1, n+1)]
    customer_ids = [f"CUST-{random.randint(1,2500):05d}" for _ in range(n)]
    order_dates = [random.choice(date_range) + timedelta(hours=random.randint(0,23)) for _ in range(n)]

    products = ['Laptop Pro', 'Phone X', 'Headphones Z', 'Tablet A', 'Watch S', 'Speaker B', 'Mouse M', 'Keyboard K']
    categories = ['Electronics', 'Electronics', 'Accessories', 'Electronics', 'Wearables', 'Accessories', 'Accessories', 'Accessories']
    regions = ['North', 'South', 'East', 'West', 'Central']
    # Intentional inconsistent labels for quality demo
    regions_with_noise = []
    for r in [random.choice(regions) for _ in range(n)]:
        if random.random() < 0.02:
            # Add inconsistent
            if r == 'North':
                regions_with_noise.append(random.choice(['North', 'north', 'NORTH', ' North']))
            elif r == 'South':
                regions_with_noise.append(random.choice(['South', 'south', ' South']))
            else:
                regions_with_noise.append(r)
        else:
            regions_with_noise.append(r)

    product_choices = [random.choice(products) for _ in range(n)]
    category_choices = [categories[products.index(p)] for p in product_choices]

    quantity = np.random.randint(1, 5, n)
    price = np.random.choice([199, 299, 499, 799, 999, 1299, 1499], n) + np.random.randint(-50,50,n)
    price = np.maximum(price, 50)

    discount_pct = np.random.choice([0, 5, 10, 15, 20, 25], n, p=[0.4,0.2,0.15,0.1,0.1,0.05])
    revenue = price * quantity * (1 - discount_pct/100)
    cost = price * 0.6 + np.random.randint(-20,20,n)
    profit = revenue - cost * quantity
    # Intentional outliers
    outlier_idx = np.random.choice(n, 14, replace=False)
    revenue[outlier_idx] = revenue[outlier_idx] * 5

    # Introduce missing
    customer_age = np.random.randint(18, 70, n).astype(float)
    missing_age_idx = np.random.choice(n, int(n*0.072), replace=False)
    customer_age[missing_age_idx] = np.nan

    # Duplicate some rows - 12 duplicates
    df = pd.DataFrame({
        'order_id': order_ids,
        'customer_id': customer_ids,
        'order_date': order_dates,
        'product': product_choices,
        'category': category_choices,
        'region': regions_with_noise,
        'quantity': quantity,
        'price': price,
        'discount_pct': discount_pct,
        'revenue': revenue.round(2),
        'profit': profit.round(2),
        'customer_age': customer_age,
        'payment_method': [random.choice(['Credit Card', 'PayPal', 'UPI', 'Net Banking']) for _ in range(n)],
        'shipping_status': [random.choice(['Delivered', 'Shipped', 'Processing', 'Returned']) for _ in range(n)]
    })

    # Add duplicates
    dup_rows = df.sample(12)
    df = pd.concat([df, dup_rows], ignore_index=True)

    # Blank strings + whitespace for quality demo
    df.loc[np.random.choice(df.index, 30), 'region'] = ' '
    df.loc[np.random.choice(df.index, 15), 'payment_method'] = ''

    df.to_csv(os.path.join(os.path.dirname(__file__), 'ecommerce_sales.csv'), index=False)
    print(f"E-commerce generated: {len(df)} rows")

def gen_marketing():
    n = 3400
    campaigns = [f"CMP-{i:04d}" for i in range(1, 51)]
    channels = ['Google Ads', 'Facebook', 'Instagram', 'LinkedIn', 'Email', 'Organic', 'YouTube']
    start_date = datetime(2023, 1, 1)
    date_range = pd.date_range(start_date, datetime(2024,12,31), freq='D')

    data = []
    for _ in range(n):
        camp = random.choice(campaigns)
        channel = random.choice(channels)
        date = random.choice(date_range)
        impressions = np.random.randint(1000, 100000)
        clicks = int(impressions * np.random.uniform(0.01, 0.08))
        conversions = int(clicks * np.random.uniform(0.02, 0.15))
        spend = np.random.uniform(100, 5000)
        revenue = conversions * np.random.uniform(50, 500)

        ctr = clicks / impressions * 100 if impressions>0 else 0
        cpa = spend / conversions if conversions>0 else 0
        roas = revenue / spend if spend>0 else 0

        data.append([camp, channel, date, impressions, clicks, conversions, spend, revenue, ctr, cpa, roas])

    df = pd.DataFrame(data, columns=['campaign_id','channel','date','impressions','clicks','conversions','spend','revenue','ctr','cpa','roas'])
    # Missing
    df.loc[np.random.choice(df.index, 50), 'spend'] = np.nan
    df.to_csv(os.path.join(os.path.dirname(__file__), 'marketing_campaigns.csv'), index=False)
    print(f"Marketing generated: {len(df)} rows")

def gen_saas():
    n = 5800
    customer_ids = [f"CUST-{i:05d}" for i in range(1, n+1)]
    plans = ['Starter', 'Growth', 'Professional', 'Enterprise']
    statuses = ['Active', 'Churned', 'Trial']
    start_date = datetime(2022,1,1)
    date_range = pd.date_range(start_date, datetime(2024,12,31), freq='D')

    data = []
    for cid in customer_ids:
        plan = random.choice(plans)
        status = random.choices(statuses, weights=[0.7,0.2,0.1])[0]
        signup = random.choice(date_range)
        tenure = (datetime(2024,12,31) - signup).days // 30
        mrr_map = {'Starter':29, 'Growth':99, 'Professional':299, 'Enterprise':999}
        mrr = mrr_map[plan] + np.random.randint(-5,5)
        engagement_score = np.random.randint(1,100) if status!='Churned' else np.random.randint(1,40)
        support_tickets = np.random.randint(0,15)
        last_active = signup + timedelta(days=random.randint(0, (datetime(2024,12,31)-signup).days))

        data.append([cid, plan, status, signup, tenure, mrr, engagement_score, support_tickets, last_active])

    df = pd.DataFrame(data, columns=['customer_id','plan','status','signup_date','tenure_months','mrr','engagement_score','support_tickets','last_active_date'])
    # Missing & duplicates like before
    df.loc[np.random.choice(df.index, 100), 'engagement_score'] = np.nan
    df.to_csv(os.path.join(os.path.dirname(__file__), 'saas_customers.csv'), index=False)
    print(f"SaaS generated: {len(df)} rows")

if __name__ == "__main__":
    gen_ecommerce()
    gen_marketing()
    gen_saas()
    print("All samples generated — synthetic datasets labelled.")
