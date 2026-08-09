"""
Tests for quality auditor.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
from src.quality.auditor import audit_dataset
from src.profiling.classifier import classify_columns

def test_missing_detection():
    df = pd.DataFrame({"a":[1,None,3], "b":["x",None,"z"]})
    profiles = classify_columns(df)
    numeric = [p.name for p in profiles if p.inferred_type=="numerical"]
    cat = [p.name for p in profiles if p.inferred_type=="categorical"]
    report = audit_dataset(df, numeric, cat)
    assert report.missing.total_missing_cells == 2
    assert report.score < 100

def test_duplicate_detection():
    df = pd.DataFrame({"a":[1,1,2], "b":[2,2,3]})
    profiles = classify_columns(df)
    num = [p.name for p in profiles if p.inferred_type=="numerical"]
    cat = [p.name for p in profiles if p.inferred_type=="categorical"]
    report = audit_dataset(df, num, cat)
    assert report.duplicates.duplicate_row_count == 1

def test_quality_score_perfect():
    df = pd.DataFrame({"a":[1,2,3], "b":[4,5,6]})
    profiles = classify_columns(df)
    num = [p.name for p in profiles if p.inferred_type=="numerical"]
    cat = [p.name for p in profiles if p.inferred_type=="categorical"]
    report = audit_dataset(df, num, cat)
    assert report.score >= 90

if __name__ == "__main__":
    test_missing_detection()
    test_duplicate_detection()
    test_quality_score_perfect()
    print("test_quality PASS")
