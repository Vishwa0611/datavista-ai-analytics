"""
Tests for cleaning engine.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
from src.cleaning.engine import apply_cleaning_operations
from src.utils.constants import CleaningOp

def test_remove_duplicates():
    df = pd.DataFrame({"a":[1,1,2], "b":[2,2,3]})
    ops = [{"op": CleaningOp.REMOVE_DUPLICATES, "column": "all"}]
    res = apply_cleaning_operations(df, ops)
    assert res.rows_after == 2
    assert len(res.log) == 1

def test_fill_missing():
    df = pd.DataFrame({"a":[1,None,3]})
    ops = [{"op": CleaningOp.FILL_NUM_MEDIAN, "column": "a"}]
    res = apply_cleaning_operations(df, ops)
    assert res.df_cleaned['a'].isna().sum() == 0

def test_trim_whitespace():
    df = pd.DataFrame({"a":["  hello ","world "]})
    ops = [{"op": CleaningOp.TRIM_WHITESPACE, "column": "a"}]
    res = apply_cleaning_operations(df, ops)
    assert res.df_cleaned['a'].iloc[0] == "hello"

if __name__ == "__main__":
    test_remove_duplicates()
    test_fill_missing()
    test_trim_whitespace()
    print("test_cleaning PASS")
