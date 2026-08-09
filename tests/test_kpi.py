"""
Tests for KPI calculator.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
from src.kpi.calculator import calculate_kpi

def test_total_revenue():
    df = pd.DataFrame({"revenue":[100,200,300], "order_id":[1,2,3]})
    cfg = {"name":"Total Revenue","aliases":[["revenue","sales"]],"formula":"SUM(revenue)","unit":"currency"}
    res = calculate_kpi(df, cfg)
    assert res.available
    assert res.value == 600

def test_aov():
    df = pd.DataFrame({"revenue":[300,300], "order_id":[1,2]})
    cfg = {"name":"Average Order Value","aliases":[["revenue","sales"],["order_id","order"]],"formula":"Total Revenue / Total Orders","unit":"currency"}
    res = calculate_kpi(df, cfg)
    assert res.available
    assert res.value == 300

def test_missing_cols():
    df = pd.DataFrame({"a":[1,2]})
    cfg = {"name":"Total Revenue","aliases":[["revenue","sales"]],"formula":"SUM(revenue)","unit":"currency"}
    res = calculate_kpi(df, cfg)
    assert not res.available

if __name__ == "__main__":
    test_total_revenue()
    test_aov()
    test_missing_cols()
    print("test_kpi PASS")
