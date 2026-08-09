"""
Tests for SQL engine.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
from src.sql.engine import get_engine

def test_register_and_query():
    df = pd.DataFrame({"a":[1,2,3], "b":[4,5,6]})
    engine = get_engine()
    engine.register_table("test_table", df)
    res = engine.execute("SELECT SUM(a) as sum_a FROM test_table")
    assert res['success']
    assert res['df']['sum_a'][0] == 6

def test_showcase_gen():
    from src.sql.query_generator import generate_showcase_queries
    df = pd.DataFrame({"cat":["A","B","A"], "val":[10,20,30], "date":pd.date_range("2023-01-01", periods=3)})
    queries = generate_showcase_queries(df, "test", ["val"], ["cat"], ["date"])
    assert len(queries) >= 5

if __name__ == "__main__":
    test_register_and_query()
    test_showcase_gen()
    print("test_sql PASS")
