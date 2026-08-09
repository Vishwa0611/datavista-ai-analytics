"""
RFM analysis — Recency, Frequency, Monetary.
"""
import pandas as pd
from typing import Dict, Any, List, Optional

def find_rfm_columns(columns: List[str]) -> Dict[str, Optional[str]]:
    """
    Heuristic to find likely R,F,M columns from column names.
    """
    cols_lower = {c.lower(): c for c in columns}
    recency = None
    frequency = None
    monetary = None

    for low, orig in cols_lower.items():
        if any(k in low for k in ['date', 'last_purchase', 'recency', 'order_date', 'last_order']):
            if recency is None:
                recency = orig
        if any(k in low for k in ['frequency', 'order_count', 'orders', 'purchase_count']):
            frequency = orig
        if any(k in low for k in ['monetary', 'revenue', 'sales', 'amount', 'total_spent', 'spent']):
            monetary = orig

    # Also check if customer_id exists
    customer_col = None
    for low, orig in cols_lower.items():
        if 'customer' in low and ('id' in low or low=='customer'):
            customer_col = orig
            break
    if not customer_col:
        for low, orig in cols_lower.items():
            if 'customer_id' in low or low=='customer':
                customer_col = orig
                break

    return {"recency": recency, "frequency": frequency, "monetary": monetary, "customer": customer_col}

def calculate_rfm(df: pd.DataFrame, customer_col: str, date_col: str, monetary_col: str) -> Dict[str, Any]:
    """
    Calculate RFM if we have customer, date, monetary.
    Simplified: Recency = days since last purchase, Frequency = count, Monetary = sum
    """
    try:
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce', dayfirst=True)
        df_copy = df_copy.dropna(subset=[customer_col, date_col, monetary_col])
        df_copy[monetary_col] = pd.to_numeric(df_copy[monetary_col], errors='coerce')
        df_copy = df_copy.dropna(subset=[monetary_col])

        if len(df_copy) == 0:
            return {"available": False, "reason": "No valid rows after cleaning"}

        # Reference date = max date
        max_date = df_copy[date_col].max()

        rfm = df_copy.groupby(customer_col).agg(
            Recency=(date_col, lambda x: (max_date - x.max()).days),
            Frequency=(date_col, 'count'),
            Monetary=(monetary_col, 'sum')
        ).reset_index()

        # Score 1-5 via quantiles
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5,4,3,2,1], duplicates='drop')
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5], duplicates='drop')
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1,2,3,4,5], duplicates='drop')

        # Convert to int for sorting
        rfm['R_Score'] = rfm['R_Score'].astype(int)
        rfm['F_Score'] = rfm['F_Score'].astype(int)
        rfm['M_Score'] = rfm['M_Score'].astype(int)

        # Segment logic
        def segment(row):
            if row['R_Score']>=4 and row['F_Score']>=4 and row['M_Score']>=4:
                return "Champions"
            elif row['R_Score']>=3 and row['F_Score']>=3 and row['M_Score']>=3:
                return "Loyal"
            elif row['R_Score']>=4 and row['F_Score']<=2:
                return "New Customers"
            elif row['R_Score']<=2 and row['F_Score']>=3:
                return "At Risk"
            elif row['R_Score']<=2 and row['F_Score']<=2:
                return "Lost"
            else:
                return "Potential"

        rfm['Segment'] = rfm.apply(segment, axis=1)

        segment_counts = rfm['Segment'].value_counts().to_dict()

        return {
            "available": True,
            "rfm_table": rfm,
            "segment_counts": segment_counts,
            "summary": f"RFM calculated for {len(rfm)} customers — {segment_counts}"
        }

    except Exception as e:
        return {"available": False, "reason": f"RFM failed: {e}"}
