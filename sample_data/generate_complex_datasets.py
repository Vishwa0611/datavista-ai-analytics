"""
Generate 20 mid-large complex datasets of all types — not only business
Each dataset: 5000-15000 rows, 15-25 columns, with intentional complexities
To test robustness: missing values, duplicates, outliers, inconsistent labels, mixed date formats
"""
import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

OUTPUT_DIR = os.path.dirname(__file__) + "/complex"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def add_complexities(df, missing_pct=0.03, dup_pct=0.01, outlier_pct=0.01):
    """Add realistic complexities"""
    df = df.copy()
    n = len(df)
    
    # Add missing values randomly (3%)
    for col in df.columns:
        if random.random() < 0.3:  # 30% of columns get missing
            idx = np.random.choice(df.index, int(n*missing_pct), replace=False)
            df.loc[idx, col] = np.nan
    
    # Add duplicates (1%)
    if dup_pct > 0:
        dup_rows = df.sample(int(n*dup_pct))
        df = pd.concat([df, dup_rows], ignore_index=True)
    
    # Add inconsistent labels for categorical columns
    for col in df.select_dtypes(include='object').columns:
        if df[col].nunique() < 20 and random.random() < 0.5:
            # Pick a value and create inconsistent versions
            unique_vals = df[col].dropna().unique()
            if len(unique_vals) > 0:
                val = random.choice(unique_vals)
                inconsistent_versions = [val.lower(), val.upper(), f" {val} ", f"{val} "]
                for _ in range(int(n*0.01)):
                    idx = random.choice(df.index)
                    if df.loc[idx, col] == val:
                        df.loc[idx, col] = random.choice(inconsistent_versions)
    
    # Add outliers for numeric columns
    for col in df.select_dtypes(include=[np.number]).columns:
        if random.random() < 0.4:
            idx = np.random.choice(df.index, int(n*outlier_pct), replace=False)
            # Multiply by 5-10 for outliers
            df.loc[idx, col] = df.loc[idx, col] * random.choice([5, 10, -1])
    
    return df

def gen_ecommerce_large():
    n=12000
    df = pd.DataFrame({
        'order_id': [f"ORD-{i:06d}" for i in range(n)],
        'customer_id': [f"CUST-{random.randint(1,3000):05d}" for _ in range(n)],
        'order_date': [datetime(2022,1,1) + timedelta(days=random.randint(0,1000)) for _ in range(n)],
        'product': [random.choice(['Laptop','Phone','Tablet','Watch','Headphones','Speaker','Mouse','Keyboard']) for _ in range(n)],
        'category': [random.choice(['Electronics','Accessories','Wearables']) for _ in range(n)],
        'region': [random.choice(['North','South','East','West','Central']) for _ in range(n)],
        'quantity': np.random.randint(1,10,n),
        'unit_price': np.random.randint(100,2000,n),
        'discount': np.random.choice([0,0.05,0.1,0.15,0.2], n, p=[0.5,0.2,0.15,0.1,0.05]),
        'sales': np.random.randint(100,5000,n)*np.random.randint(1,5,n),
        'profit': np.random.randint(-100,1000,n),
        'payment_method': [random.choice(['Credit Card','PayPal','UPI','Net Banking']) for _ in range(n)],
        'shipping_days': np.random.randint(1,15,n),
        'customer_segment': [random.choice(['Regular','Premium','VIP']) for _ in range(n)],
        'sales_rep': [random.choice(['Aman','Priya','John','Sarah']) for _ in range(n)],
    })
    df['total_sales'] = df['quantity'] * df['unit_price'] * (1-df['discount'])
    return add_complexities(df)

def gen_healthcare():
    n=8000
    df = pd.DataFrame({
        'patient_id': [f"PAT-{i:06d}" for i in range(n)],
        'admission_date': [datetime(2020,1,1) + timedelta(days=random.randint(0,1500)) for _ in range(n)],
        'discharge_date': [datetime(2020,1,5) + timedelta(days=random.randint(0,1500)) for _ in range(n)],
        'age': np.random.randint(1,90,n),
        'gender': [random.choice(['Male','Female','Other']) for _ in range(n)],
        'blood_type': [random.choice(['A+','A-','B+','B-','O+','O-','AB+','AB-']) for _ in range(n)],
        'disease': [random.choice(['Diabetes','Hypertension','Asthma','COVID','Flu','Cancer']) for _ in range(n)],
        'hospital': [random.choice(['City Hospital','General Hospital','Apollo','Fortis']) for _ in range(n)],
        'doctor': [random.choice(['Dr. Smith','Dr. Johnson','Dr. Williams','Dr. Brown']) for _ in range(n)],
        'treatment_cost': np.random.randint(1000,100000,n),
        'insurance_covered': np.random.randint(0,80000,n),
        'length_of_stay': np.random.randint(1,30,n),
        'lab_tests': np.random.randint(1,15,n),
        'medications': np.random.randint(1,10,n),
        'recovery_score': np.random.uniform(0,100,n),
        'readmitted': [random.choice([0,1]) for _ in range(n)],
    })
    return add_complexities(df)

def gen_education():
    n=10000
    df = pd.DataFrame({
        'student_id': [f"STU-{i:06d}" for i in range(n)],
        'enrollment_date': [datetime(2019,1,1) + timedelta(days=random.randint(0,1500)) for _ in range(n)],
        'name': [f"Student_{i}" for i in range(n)],
        'age': np.random.randint(18,30,n),
        'gender': [random.choice(['Male','Female','Non-binary']) for _ in range(n)],
        'department': [random.choice(['CS','EE','ME','Civil','MBA']) for _ in range(n)],
        'course': [random.choice(['B.Tech','M.Tech','MBA','PhD']) for _ in range(n)],
        'semester': np.random.randint(1,9,n),
        'gpa': np.round(np.random.uniform(2.0,10.0,n),2),
        'attendance_pct': np.random.uniform(40,100,n),
        'assignments_submitted': np.random.randint(0,20,n),
        'hours_studied_weekly': np.random.randint(0,50,n),
        'scholarship': [random.choice([0,5000,10000,20000]) for _ in range(n)],
        'placement_status': [random.choice(['Placed','Not Placed','Internship']) for _ in range(n)],
        'salary_offered': [random.choice([0,300000,500000,800000,1200000]) for _ in range(n)],
    })
    return add_complexities(df)

def gen_finance_stock():
    n=15000
    dates = pd.date_range('2020-01-01', periods=n, freq='D')
    df = pd.DataFrame({
        'date': np.random.choice(dates, n),
        'stock_symbol': [random.choice(['AAPL','GOOGL','MSFT','TSLA','AMZN','META','NFLX','NVDA']) for _ in range(n)],
        'open': np.random.uniform(100,500,n),
        'high': np.random.uniform(100,550,n),
        'low': np.random.uniform(90,490,n),
        'close': np.random.uniform(100,500,n),
        'volume': np.random.randint(1000000,100000000,n),
        'market_cap': np.random.uniform(1e9,2e12,n),
        'pe_ratio': np.random.uniform(10,50,n),
        'dividend_yield': np.random.uniform(0,5,n),
        'sector': [random.choice(['Tech','Finance','Healthcare','Energy']) for _ in range(n)],
        'analyst_rating': [random.choice(['Buy','Sell','Hold']) for _ in range(n)],
        'price_change_pct': np.random.uniform(-10,10,n),
    })
    return add_complexities(df)

def gen_real_estate():
    n=7000
    df = pd.DataFrame({
        'property_id': [f"PROP-{i:06d}" for i in range(n)],
        'sale_date': [datetime(2018,1,1) + timedelta(days=random.randint(0,2000)) for _ in range(n)],
        'city': [random.choice(['Mumbai','Delhi','Bangalore','Chennai','Kolkata','Pune']) for _ in range(n)],
        'area_sqft': np.random.randint(500,5000,n),
        'bedrooms': np.random.randint(1,6,n),
        'bathrooms': np.random.randint(1,5,n),
        'age_years': np.random.randint(0,50,n),
        'price': np.random.randint(2000000,20000000,n),
        'price_per_sqft': np.random.randint(3000,20000,n),
        'furnishing': [random.choice(['Furnished','Semi-Furnished','Unfurnished']) for _ in range(n)],
        'property_type': [random.choice(['Apartment','Villa','Plot','Office']) for _ in range(n)],
        'seller_type': [random.choice(['Owner','Agent','Builder']) for _ in range(n)],
        'near_metro': [random.choice([0,1]) for _ in range(n)],
        'parking': [random.choice([0,1,2]) for _ in range(n)],
    })
    return add_complexities(df)

def gen_hr_attrition():
    n=9000
    df = pd.DataFrame({
        'employee_id': [f"EMP-{i:06d}" for i in range(n)],
        'join_date': [datetime(2015,1,1) + timedelta(days=random.randint(0,2500)) for _ in range(n)],
        'department': [random.choice(['Sales','HR','IT','Finance','Marketing','Operations']) for _ in range(n)],
        'role': [random.choice(['Junior','Mid','Senior','Lead','Manager']) for _ in range(n)],
        'age': np.random.randint(22,60,n),
        'gender': [random.choice(['Male','Female']) for _ in range(n)],
        'salary': np.random.randint(300000,2000000,n),
        'tenure_months': np.random.randint(1,120,n),
        'performance_score': np.random.uniform(1,5,n),
        'satisfaction_score': np.random.uniform(1,5,n),
        'overtime_hours': np.random.randint(0,50,n),
        'trainings_attended': np.random.randint(0,10,n),
        'attrition': [random.choice([0,1]) for _ in range(n)],
        'last_promotion_months_ago': np.random.randint(0,48,n),
    })
    return add_complexities(df)

def gen_manufacturing():
    n=11000
    df = pd.DataFrame({
        'batch_id': [f"BATCH-{i:06d}" for i in range(n)],
        'production_date': [datetime(2021,1,1) + timedelta(days=random.randint(0,1000)) for _ in range(n)],
        'product_line': [random.choice(['A','B','C','D']) for _ in range(n)],
        'machine_id': [f"MACH-{random.randint(1,20):03d}" for _ in range(n)],
        'operator': [f"OP-{random.randint(1,50):03d}" for _ in range(n)],
        'shift': [random.choice(['Morning','Evening','Night']) for _ in range(n)],
        'units_produced': np.random.randint(100,1000,n),
        'defective_units': np.random.randint(0,50,n),
        'defect_rate': np.random.uniform(0,0.1,n),
        'material_cost': np.random.randint(1000,10000,n),
        'labor_hours': np.random.uniform(1,12,n),
        'temperature': np.random.uniform(20,80,n),
        'pressure': np.random.uniform(1,10,n),
        'quality_score': np.random.uniform(60,100,n),
        'passed_qc': [random.choice([0,1]) for _ in range(n)],
    })
    return add_complexities(df)

def gen_logistics():
    n=10000
    df = pd.DataFrame({
        'shipment_id': [f"SHIP-{i:06d}" for i in range(n)],
        'order_date': [datetime(2022,1,1) + timedelta(days=random.randint(0,900)) for _ in range(n)],
        'delivery_date': [datetime(2022,1,5) + timedelta(days=random.randint(0,900)) for _ in range(n)],
        'origin_city': [random.choice(['Mumbai','Delhi','Bangalore','Chennai']) for _ in range(n)],
        'destination_city': [random.choice(['Mumbai','Delhi','Bangalore','Chennai','Kolkata','Pune']) for _ in range(n)],
        'carrier': [random.choice(['FedEx','DHL','BlueDart','DTDC']) for _ in range(n)],
        'weight_kg': np.random.uniform(0.5,100,n),
        'distance_km': np.random.randint(50,3000,n),
        'shipping_cost': np.random.randint(50,5000,n),
        'delivery_days': np.random.randint(1,15,n),
        'on_time': [random.choice([0,1]) for _ in range(n)],
        'package_type': [random.choice(['Box','Envelope','Pallet']) for _ in range(n)],
        'customer_rating': np.random.randint(1,6,n),
    })
    return add_complexities(df)

def gen_social_media():
    n=15000
    df = pd.DataFrame({
        'post_id': [f"POST-{i:08d}" for i in range(n)],
        'post_date': [datetime(2023,1,1) + timedelta(days=random.randint(0,600), hours=random.randint(0,23)) for _ in range(n)],
        'platform': [random.choice(['Instagram','Facebook','Twitter','LinkedIn','TikTok']) for _ in range(n)],
        'author_id': [f"USER-{random.randint(1,2000):05d}" for _ in range(n)],
        'content_type': [random.choice(['Image','Video','Text','Reel','Story']) for _ in range(n)],
        'likes': np.random.randint(0,100000,n),
        'comments': np.random.randint(0,5000,n),
        'shares': np.random.randint(0,10000,n),
        'reach': np.random.randint(100,1000000,n),
        'impressions': np.random.randint(100,2000000,n),
        'engagement_rate': np.random.uniform(0,15,n),
        'followers_at_post': np.random.randint(100,1000000,n),
        'hashtag_count': np.random.randint(0,30,n),
        'is_sponsored': [random.choice([0,1]) for _ in range(n)],
        'sentiment': [random.choice(['Positive','Negative','Neutral']) for _ in range(n)],
    })
    return add_complexities(df)

def gen_iot_sensor():
    n=20000
    df = pd.DataFrame({
        'sensor_id': [f"SENSOR-{random.randint(1,100):04d}" for _ in range(n)],
        'timestamp': [datetime(2024,1,1) + timedelta(minutes=random.randint(0,525600)) for _ in range(n)],
        'location': [random.choice(['Factory A','Factory B','Warehouse','Office','Lab']) for _ in range(n)],
        'temperature_c': np.random.uniform(-10,80,n),
        'humidity_pct': np.random.uniform(20,100,n),
        'pressure_hpa': np.random.uniform(900,1100,n),
        'vibration': np.random.uniform(0,10,n),
        'battery_level': np.random.uniform(0,100,n),
        'signal_strength': np.random.randint(-100,-30,n),
        'error_code': [random.choice([0,0,0,0,1,2,3]) for _ in range(n)],
        'operational_status': [random.choice(['Normal','Warning','Critical']) for _ in range(n)],
    })
    return add_complexities(df)

def gen_weather():
    n=12000
    df = pd.DataFrame({
        'station_id': [f"STN-{random.randint(1,50):03d}" for _ in range(n)],
        'date': [datetime(2010,1,1) + timedelta(days=random.randint(0,5000)) for _ in range(n)],
        'city': [random.choice(['Delhi','Mumbai','Chennai','Kolkata','Bangalore','Hyderabad']) for _ in range(n)],
        'max_temp': np.random.uniform(15,50,n),
        'min_temp': np.random.uniform(5,30,n),
        'humidity': np.random.uniform(20,100,n),
        'rainfall_mm': np.random.uniform(0,200,n),
        'wind_speed': np.random.uniform(0,50,n),
        'pressure': np.random.uniform(980,1030,n),
        'uv_index': np.random.randint(0,12,n),
        'visibility_km': np.random.uniform(1,20,n),
        'weather_condition': [random.choice(['Sunny','Cloudy','Rainy','Stormy','Foggy']) for _ in range(n)],
    })
    return add_complexities(df)

def gen_flight_delays():
    n=13000
    df = pd.DataFrame({
        'flight_id': [f"FL-{i:06d}" for i in range(n)],
        'flight_date': [datetime(2022,1,1) + timedelta(days=random.randint(0,800)) for _ in range(n)],
        'airline': [random.choice(['IndiGo','Air India','SpiceJet','Vistara','GoAir']) for _ in range(n)],
        'origin': [random.choice(['DEL','BOM','BLR','MAA','CCU','HYD']) for _ in range(n)],
        'destination': [random.choice(['DEL','BOM','BLR','MAA','CCU','HYD']) for _ in range(n)],
        'scheduled_departure': [f"{random.randint(0,23):02d}:{random.randint(0,59):02d}" for _ in range(n)],
        'actual_departure': [f"{random.randint(0,23):02d}:{random.randint(0,59):02d}" for _ in range(n)],
        'delay_minutes': np.random.randint(-20,300,n),
        'distance_km': np.random.randint(200,3000,n),
        'aircraft_type': [random.choice(['A320','B737','A321','B787']) for _ in range(n)],
        'passengers': np.random.randint(50,300,n),
        'is_delayed': [random.choice([0,1]) for _ in range(n)],
        'delay_reason': [random.choice(['Weather','Technical','ATC','Crew','None']) for _ in range(n)],
        'ticket_price': np.random.randint(2000,20000,n),
    })
    return add_complexities(df)

def gen_energy():
    n=10000
    df = pd.DataFrame({
        'meter_id': [f"METER-{random.randint(1,500):04d}" for _ in range(n)],
        'reading_date': [datetime(2023,1,1) + timedelta(days=random.randint(0,500)) for _ in range(n)],
        'household_id': [f"HH-{random.randint(1,2000):05d}" for _ in range(n)],
        'city': [random.choice(['Delhi','Mumbai','Bangalore','Chennai']) for _ in range(n)],
        'energy_kwh': np.random.uniform(5,100,n),
        'peak_usage': np.random.uniform(0,50,n),
        'offpeak_usage': np.random.uniform(0,50,n),
        'cost_inr': np.random.uniform(50,1000,n),
        'temperature': np.random.uniform(15,45,n),
        'household_size': np.random.randint(1,8,n),
        'has_solar': [random.choice([0,1]) for _ in range(n)],
        'appliance_count': np.random.randint(5,30,n),
    })
    return add_complexities(df)

def gen_agriculture():
    n=8000
    df = pd.DataFrame({
        'farm_id': [f"FARM-{i:06d}" for i in range(n)],
        'season': [random.choice(['Kharif','Rabi','Summer']) for _ in range(n)],
        'crop': [random.choice(['Rice','Wheat','Maize','Cotton','Sugarcane','Pulses']) for _ in range(n)],
        'state': [random.choice(['Punjab','Haryana','MP','UP','Maharashtra','Karnataka']) for _ in range(n)],
        'area_hectares': np.random.uniform(0.5,50,n),
        'rainfall_mm': np.random.uniform(0,1500,n),
        'fertilizer_kg': np.random.uniform(0,500,n),
        'pesticide_kg': np.random.uniform(0,50,n),
        'irrigation_hours': np.random.uniform(0,200,n),
        'labor_days': np.random.randint(10,200,n),
        'yield_tons': np.random.uniform(0.5,20,n),
        'market_price_per_ton': np.random.randint(10000,50000,n),
        'profit_inr': np.random.uniform(-10000,100000,n),
    })
    return add_complexities(df)

def gen_inventory():
    n=9000
    df = pd.DataFrame({
        'sku': [f"SKU-{random.randint(1,2000):05d}" for _ in range(n)],
        'product_name': [f"Product_{random.randint(1,500)}" for _ in range(n)],
        'category': [random.choice(['Electronics','Apparel','Grocery','Home','Books']) for _ in range(n)],
        'warehouse': [random.choice(['WH-Mumbai','WH-Delhi','WH-Bangalore','WH-Chennai']) for _ in range(n)],
        'stock_date': [datetime(2023,1,1) + timedelta(days=random.randint(0,400)) for _ in range(n)],
        'stock_qty': np.random.randint(0,1000,n),
        'reorder_point': np.random.randint(10,100,n),
        'incoming_qty': np.random.randint(0,500,n),
        'outgoing_qty': np.random.randint(0,500,n),
        'unit_cost': np.random.randint(10,5000,n),
        'stock_value': np.random.randint(0,500000,n),
        'days_since_last_stock': np.random.randint(0,90,n),
        'is_low_stock': [random.choice([0,1]) for _ in range(n)],
        'supplier': [f"Supplier_{random.randint(1,100)}" for _ in range(n)],
    })
    return add_complexities(df)

def gen_support_tickets():
    n=11000
    df = pd.DataFrame({
        'ticket_id': [f"TKT-{i:07d}" for i in range(n)],
        'created_date': [datetime(2023,1,1) + timedelta(days=random.randint(0,500), hours=random.randint(0,23)) for _ in range(n)],
        'customer_id': [f"CUST-{random.randint(1,3000):05d}" for _ in range(n)],
        'priority': [random.choice(['Low','Medium','High','Critical']) for _ in range(n)],
        'category': [random.choice(['Billing','Technical','Account','Feature Request','Bug']) for _ in range(n)],
        'channel': [random.choice(['Email','Chat','Phone','Social']) for _ in range(n)],
        'agent_id': [f"AGENT-{random.randint(1,100):03d}" for _ in range(n)],
        'response_time_hours': np.random.uniform(0,48,n),
        'resolution_time_hours': np.random.uniform(1,168,n),
        'customer_satisfaction': np.random.randint(1,6,n),
        'is_escalated': [random.choice([0,1]) for _ in range(n)],
        'is_resolved': [random.choice([0,1]) for _ in range(n)],
        'reopen_count': np.random.randint(0,5,n),
    })
    return add_complexities(df)

def gen_finance_trading():
    n=14000
    df = pd.DataFrame({
        'trade_id': [f"TRADE-{i:08d}" for i in range(n)],
        'trade_date': [datetime(2020,1,1) + timedelta(days=random.randint(0,1500)) for _ in range(n)],
        'trader_id': [f"TRADER-{random.randint(1,200):04d}" for _ in range(n)],
        'asset': [random.choice(['Stock','Bond','Crypto','Forex','Commodity']) for _ in range(n)],
        'symbol': [random.choice(['BTC','ETH','AAPL','GOOGL','GOLD','OIL']) for _ in range(n)],
        'trade_type': [random.choice(['Buy','Sell']) for _ in range(n)],
        'quantity': np.random.uniform(0.1,1000,n),
        'price': np.random.uniform(10,50000,n),
        'total_value': np.random.uniform(100,1000000,n),
        'fees': np.random.uniform(0,1000,n),
        'profit_loss': np.random.uniform(-10000,50000,n),
        'leverage': [random.choice([1,2,5,10,20]) for _ in range(n)],
        'risk_score': np.random.uniform(1,10,n),
    })
    return add_complexities(df)

def gen_crypto():
    n=12000
    df = pd.DataFrame({
        'transaction_id': [f"TX-{i:08d}" for i in range(n)],
        'timestamp': [datetime(2021,1,1) + timedelta(hours=random.randint(0,30000)) for _ in range(n)],
        'user_id': [f"USER-{random.randint(1,5000):05d}" for _ in range(n)],
        'crypto': [random.choice(['BTC','ETH','SOL','ADA','DOT','MATIC']) for _ in range(n)],
        'transaction_type': [random.choice(['Buy','Sell','Transfer','Stake','Swap']) for _ in range(n)],
        'amount_crypto': np.random.uniform(0.001,10,n),
        'amount_usd': np.random.uniform(10,100000,n),
        'fee_usd': np.random.uniform(0.1,100,n),
        'wallet_balance': np.random.uniform(0,500000,n),
        'gas_price_gwei': np.random.uniform(5,200,n),
        'is_successful': [random.choice([0,1,1,1]) for _ in range(n)],
        'network': [random.choice(['Ethereum','BSC','Polygon','Solana']) for _ in range(n)],
    })
    return add_complexities(df)

def gen_healthcare_vitals():
    n=10000
    df = pd.DataFrame({
        'record_id': [f"REC-{i:07d}" for i in range(n)],
        'patient_id': [f"PAT-{random.randint(1,2000):05d}" for _ in range(n)],
        'timestamp': [datetime(2023,1,1) + timedelta(hours=random.randint(0,10000)) for _ in range(n)],
        'heart_rate': np.random.randint(50,150,n),
        'blood_pressure_sys': np.random.randint(90,180,n),
        'blood_pressure_dia': np.random.randint(60,120,n),
        'temperature_f': np.random.uniform(95,104,n),
        'oxygen_saturation': np.random.uniform(85,100,n),
        'respiratory_rate': np.random.randint(10,40,n),
        'glucose_level': np.random.randint(70,300,n),
        'device_id': [f"DEV-{random.randint(1,50):03d}" for _ in range(n)],
        'alert': [random.choice([0,0,0,1]) for _ in range(n)],
    })
    return add_complexities(df)

def gen_ecommerce_returns():
    n=8000
    df = pd.DataFrame({
        'return_id': [f"RET-{i:06d}" for i in range(n)],
        'order_id': [f"ORD-{random.randint(1,10000):06d}" for _ in range(n)],
        'return_date': [datetime(2022,6,1) + timedelta(days=random.randint(0,700)) for _ in range(n)],
        'customer_id': [f"CUST-{random.randint(1,2000):05d}" for _ in range(n)],
        'product_id': [f"PROD-{random.randint(1,500):04d}" for _ in range(n)],
        'category': [random.choice(['Electronics','Clothing','Home','Beauty']) for _ in range(n)],
        'return_reason': [random.choice(['Defective','Wrong Item','Not as Described','Changed Mind','Size Issue']) for _ in range(n)],
        'refund_amount': np.random.uniform(10,2000,n),
        'return_shipping_cost': np.random.uniform(0,100,n),
        'days_to_return': np.random.randint(0,30,n),
        'is_fraudulent': [random.choice([0,0,0,1]) for _ in range(n)],
        'customer_rating_after_return': np.random.randint(1,6,n),
    })
    return add_complexities(df)

# Generate all
generators = [
    ("01_ecommerce_large", gen_ecommerce_large, "Large E-commerce with returns"),
    ("02_healthcare_admissions", gen_healthcare, "Healthcare admissions with costs"),
    ("03_education_performance", gen_education, "Student performance and placements"),
    ("04_finance_stock", gen_finance_stock, "Stock prices with indicators"),
    ("05_real_estate", gen_real_estate, "Real estate prices and features"),
    ("06_hr_attrition", gen_hr_attrition, "HR attrition and satisfaction"),
    ("07_manufacturing_qc", gen_manufacturing, "Manufacturing quality control"),
    ("08_logistics_shipping", gen_logistics, "Logistics shipping and delivery"),
    ("09_social_media_engagement", gen_social_media, "Social media engagement metrics"),
    ("10_iot_sensor", gen_iot_sensor, "IoT sensor data with anomalies"),
    ("11_weather_climate", gen_weather, "Weather climate data"),
    ("12_flight_delays", gen_flight_delays, "Flight delays and reasons"),
    ("13_energy_consumption", gen_energy, "Energy consumption smart meters"),
    ("14_agriculture_yield", gen_agriculture, "Agriculture yield and profit"),
    ("15_inventory_management", gen_inventory, "Retail inventory and stock"),
    ("16_support_tickets", gen_support_tickets, "Customer support tickets"),
    ("17_finance_trading", gen_finance_trading, "Finance trading P&L"),
    ("18_crypto_transactions", gen_crypto, "Crypto transactions and fees"),
    ("19_healthcare_vitals", gen_healthcare_vitals, "Healthcare vitals monitoring"),
    ("20_ecommerce_returns", gen_ecommerce_returns, "E-commerce returns and fraud"),
]

print(f"Generating 20 complex datasets in {OUTPUT_DIR}...")
for name, func, desc in generators:
    df = func()
    path = os.path.join(OUTPUT_DIR, f"{name}.csv")
    df.to_csv(path, index=False)
    print(f"  ✓ {name}: {len(df)} rows, {len(df.columns)} cols, {df.memory_usage(deep=True).sum()/1024/1024:.1f}MB - {desc}")

print(f"\nAll 20 datasets generated in {OUTPUT_DIR}")
print(f"Total size: {sum(os.path.getsize(os.path.join(OUTPUT_DIR, f)) for f in os.listdir(OUTPUT_DIR))/1024/1024:.1f} MB")
