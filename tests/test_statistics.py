"""
Tests for statistics module.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
from src.statistics.correlation import analyze_correlations
from src.statistics.hypothesis import auto_suggest_and_run_tests

def test_correlation():
    df = pd.DataFrame({"a":[1,2,3,4,5], "b":[2,4,6,8,10]})
    res = analyze_correlations(df, ["a","b"])
    assert res["available"]
    assert len(res["results"]) == 1
    assert res["results"][0].pearson_r > 0.9

def test_ttest():
    import numpy as np
    np.random.seed(0)
    df = pd.DataFrame({
        "value": list(np.random.normal(100,10,50)) + list(np.random.normal(120,10,50)),
        "group": ["A"]*50 + ["B"]*50
    })
    tests = auto_suggest_and_run_tests(df, ["value"], ["group"])
    assert len(tests) >= 1
    # Should be significant
    assert tests[0].p_value < 0.05

if __name__ == "__main__":
    test_correlation()
    test_ttest()
    print("test_statistics PASS")
