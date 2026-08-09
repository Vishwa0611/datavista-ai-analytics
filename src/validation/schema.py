"""
Typed dataclasses for all module outputs — makes code professional and testable.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

class IssueSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class IssueLabel(str, Enum):
    DETECTED = "Detected"
    POTENTIAL = "Potential"
    REQUIRES_REVIEW = "Requires review"

@dataclass
class ColumnProfile:
    name: str
    inferred_type: str  # from ColumnType enum value
    original_dtype: str
    unique_count: int
    unique_ratio: float
    missing_count: int
    missing_pct: float
    sample_values: List[Any] = field(default_factory=list)
    is_constant: bool = False
    is_high_cardinality: bool = False
    is_id: bool = False
    is_potential_pii: bool = False
    pii_types: List[str] = field(default_factory=list)
    mean: Optional[float] = None
    median: Optional[float] = None
    min_val: Optional[Any] = None
    max_val: Optional[Any] = None

@dataclass
class ProfileResult:
    columns: List[ColumnProfile]
    row_count: int
    column_count: int
    memory_usage_mb: float
    detected_domain: str
    domain_confidence: float
    domain_keywords_matched: Dict[str, int]
    numeric_cols: List[str] = field(default_factory=list)
    categorical_cols: List[str] = field(default_factory=list)
    datetime_cols: List[str] = field(default_factory=list)
    id_cols: List[str] = field(default_factory=list)
    pii_cols: List[str] = field(default_factory=list)

@dataclass
class MissingReport:
    total_missing_cells: int
    total_cells: int
    missing_pct: float
    per_column: Dict[str, Dict[str, Any]]  # col -> {count, pct}
    worst_columns: List[str]

@dataclass
class DuplicateReport:
    duplicate_row_count: int
    duplicate_pct: float
    duplicate_id_cols: Dict[str, int]  # col -> dupe count
    sample_duplicates: Optional[Any] = None  # df head

@dataclass
class OutlierReport:
    method: str
    per_column: Dict[str, Dict[str, Any]]  # col -> {count, pct, lower, upper}
    total_outlier_rows: int

@dataclass
class ConsistencyReport:
    blank_string_counts: Dict[str, int]
    whitespace_counts: Dict[str, int]
    inconsistent_labels: Dict[str, Dict[str, Any]]  # col -> {examples}
    constant_columns: List[str]
    high_cardinality_columns: List[str]

@dataclass
class Issue:
    severity: str
    label: str
    column: Optional[str]
    description: str
    affected_count: Optional[int] = None

@dataclass
class DataQualityReport:
    score: int  # 0-100
    score_breakdown: Dict[str, float]
    missing: MissingReport
    duplicates: DuplicateReport
    outliers: OutlierReport
    consistency: ConsistencyReport
    issues: List[Issue]
    is_empty: bool = False

@dataclass
class TransformationRecord:
    step: int
    column: str
    action: str
    before: Optional[str]
    after: Optional[str]
    rows_affected: int
    details: Optional[str] = None

@dataclass
class CleaningResult:
    df_cleaned: Any  # pd.DataFrame
    log: List[TransformationRecord]
    rows_before: int
    rows_after: int
    score_before: Optional[int] = None
    score_after: Optional[int] = None

@dataclass
class IngestionResult:
    df: Any
    preview: Any
    metadata: Dict[str, Any]

@dataclass
class KPIResult:
    name: str
    formula: str
    value: Any
    unit: str
    interpretation: str
    evidence_columns: List[str]
    calculation_details: str
    available: bool = True
    reason_if_unavailable: Optional[str] = None

@dataclass
class HypothesisResult:
    test_name: str
    description: str
    null_hypothesis: str
    alt_hypothesis: str
    test_statistic: float
    p_value: float
    alpha: float
    decision: str  # Reject/ Fail to reject
    interpretation: str
    effect_size: Optional[float] = None
    effect_interpretation: Optional[str] = None

@dataclass
class CorrelationResult:
    col1: str
    col2: str
    pearson_r: float
    pearson_p: float
    spearman_r: float
    spearman_p: float
    interpretation: str
    is_significant: bool

@dataclass
class Insight:
    finding: str
    evidence: Dict[str, Any]
    business_meaning: str
    recommendation: str
    severity: str  # info, warning, critical
    confidence: str  # high, medium, low
    type: str  # CalculatedInsight or AIInterpretation
    source: str  # which module generated

@dataclass
class ModuleResult:
    available: bool
    reason: Optional[str] = None
    data: Optional[Any] = None
