"""
Main profiler orchestrator — combines classifier + domain detection.
"""
from typing import Dict
import pandas as pd
from ..validation.schema import ProfileResult
from .classifier import classify_columns
from .domain_detector import detect_domain, list_all_domain_scores
from ..utils.helpers import human_readable_size

def profile_dataset(df: pd.DataFrame, file_name: str = "") -> ProfileResult:
    """
    Full profiling pipeline.
    """
    row_count = len(df)
    col_count = len(df.columns)
    mem_bytes = df.memory_usage(deep=True).sum()
    mem_mb = round(mem_bytes / (1024*1024), 2)

    column_profiles = classify_columns(df)

    # Domain detection
    detected_domain, confidence, keywords_matched = detect_domain(list(df.columns))
    all_scores = list_all_domain_scores(list(df.columns))

    # Categorize cols by inferred type
    numeric_cols = [p.name for p in column_profiles if p.inferred_type == "numerical"]
    categorical_cols = [p.name for p in column_profiles if p.inferred_type == "categorical"]
    datetime_cols = [p.name for p in column_profiles if p.inferred_type == "datetime"]
    id_cols = [p.name for p in column_profiles if p.is_id or p.inferred_type == "id"]
    pii_cols = [p.name for p in column_profiles if p.is_potential_pii]

    return ProfileResult(
        columns=column_profiles,
        row_count=row_count,
        column_count=col_count,
        memory_usage_mb=mem_mb,
        detected_domain=detected_domain,
        domain_confidence=confidence,
        domain_keywords_matched=keywords_matched,
        numeric_cols=numeric_cols,
        categorical_cols=categorical_cols,
        datetime_cols=datetime_cols,
        id_cols=id_cols,
        pii_cols=pii_cols
    )
