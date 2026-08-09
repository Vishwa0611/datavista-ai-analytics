"""
Main orchestrator — runs full pipeline in order, aggregates results.
Optimized with caching to prevent Streamlit Cloud CPU throttling.
"""

from typing import Dict, Any, Optional
import pandas as pd
import streamlit as st
from ..profiling.profiler import profile_dataset
from ..quality.auditor import audit_dataset
from ..eda.engine import run_eda
from ..kpi.engine import run_kpi_analysis
from ..statistics.engine import run_statistical_analysis
from ..segmentation.engine import run_segmentation
from ..timeseries.engine import run_timeseries_analysis
from ..ai.insight_engine import generate_insights
from ..validation.schema import ModuleResult
from ..utils.logger import logger

def _run_pipeline_uncached(
    df: pd.DataFrame,
    file_metadata: Dict[str, Any],
    app_version: str = "0.1.0",
    cleaning_result: Optional[Any] = None
) -> Dict[str, Any]:
    """Internal heavy pipeline — no caching"""
    logger.info(f"Starting pipeline for {file_metadata.get('file_name')} with {len(df)} rows")

    df_for_analysis = cleaning_result.df_cleaned if cleaning_result else df

    # 1. Profiling
    profile_result = profile_dataset(df_for_analysis, file_metadata.get('file_name', ''))

    # 2. Quality
    quality_result = audit_dataset(df_for_analysis, profile_result.numeric_cols, profile_result.categorical_cols)

    # 3. EDA — sampling for large datasets to save CPU
    # If rows > 20000, use sample for EDA charts (but keep full for KPIs via DuckDB)
    df_for_eda = df_for_analysis
    if len(df_for_analysis) > 20000:
        df_for_eda = df_for_analysis.sample(n=20000, random_state=42)
        logger.info(f"Sampling EDA from {len(df_for_analysis)} to 20000 rows to save CPU")

    eda_result = run_eda(df_for_eda, profile_result.numeric_cols, profile_result.categorical_cols, profile_result.datetime_cols)

    # 4. KPI — uses full DF via DuckDB (fast columnar)
    kpi_result = run_kpi_analysis(df_for_analysis, profile_result.detected_domain, profile_result)

    # 5. Statistics — sampling for large datasets
    df_for_stats = df_for_analysis
    if len(df_for_analysis) > 15000:
        df_for_stats = df_for_analysis.sample(n=15000, random_state=42)

    stats_result = run_statistical_analysis(df_for_stats, profile_result.numeric_cols, profile_result.categorical_cols)

    # 6. Segmentation
    seg_result = run_segmentation(df_for_analysis, profile_result.numeric_cols, profile_result.categorical_cols, profile_result.datetime_cols)

    # 7. Time Series
    ts_result = run_timeseries_analysis(df_for_analysis, profile_result.datetime_cols, profile_result.numeric_cols)

    # Aggregate for insight engine
    pipeline_data_for_insights = {
        "profile": profile_result,
        "quality": quality_result,
        "eda": eda_result.data if isinstance(eda_result, ModuleResult) else eda_result,
        "kpi": kpi_result.data if isinstance(kpi_result, ModuleResult) else kpi_result,
        "statistics": stats_result.data if isinstance(stats_result, ModuleResult) else stats_result,
        "segmentation": seg_result.data if isinstance(seg_result, ModuleResult) else seg_result,
        "timeseries": ts_result.data if isinstance(ts_result, ModuleResult) else ts_result,
        "metadata": file_metadata,
        "app_version": app_version
    }

    # 8. Insights
    insights = generate_insights(pipeline_data_for_insights)

    # Full aggregation
    full_result = {
        "profile": profile_result,
        "quality": quality_result,
        "eda": eda_result.data if isinstance(eda_result, ModuleResult) and eda_result.available else {},
        "eda_raw": eda_result,
        "kpi": kpi_result.data if isinstance(kpi_result, ModuleResult) and kpi_result.available else {},
        "kpi_raw": kpi_result,
        "statistics": stats_result.data if isinstance(stats_result, ModuleResult) and stats_result.available else {},
        "statistics_raw": stats_result,
        "segmentation": seg_result.data if isinstance(seg_result, ModuleResult) else {},
        "segmentation_raw": seg_result,
        "timeseries": ts_result.data if isinstance(ts_result, ModuleResult) else {},
        "timeseries_raw": ts_result,
        "insights": insights,
        "metadata": file_metadata,
        "app_version": app_version,
        "cleaning": cleaning_result,
        "df_original": df,
        "df_cleaned": df_for_analysis
    }

    logger.info(f"Pipeline complete — quality {quality_result.score}, {len(insights)} insights")
    return full_result

@st.cache_data(show_spinner="🔬 Analyzing data... profiling, quality, KPIs, stats (this may take 10-20 sec for large files, cached for 1 hour)", ttl=3600, max_entries=10)
def run_full_pipeline(
    df: pd.DataFrame,
    file_metadata: Dict[str, Any],
    app_version: str = "0.1.0",
    cleaning_result: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Cached pipeline — prevents re-running heavy calculations on every page switch.
    This is the main fix for Streamlit Cloud CPU throttling.
    - First upload of a file: runs full pipeline (10-20 sec for 54k rows)
    - Next page switches: uses cached result instantly (0 sec, no CPU)
    - ttl=3600: cache expires after 1 hour
    - max_entries=10: keeps only 10 recent files in cache to save memory
    
    If cleaning_result provided, uses cleaned DF and bypasses cache for that run
    (cleaning is user-triggered and should re-run)
    """
    # If cleaning result provided, don't use cache — cleaning should always re-run
    if cleaning_result is not None:
        return _run_pipeline_uncached(df, file_metadata, app_version, cleaning_result)
    
    # Otherwise use cached uncached version
    return _run_pipeline_uncached(df, file_metadata, app_version, cleaning_result)
