"""
Main quality auditor — orchestrates checks and builds report.
Fixed: Improved wording for outliers, constant columns, record uniqueness.
"""
from typing import List
import pandas as pd
from ..validation.schema import (
    DataQualityReport, MissingReport, DuplicateReport,
    OutlierReport, ConsistencyReport, Issue, IssueSeverity, IssueLabel
)
from .checks import check_missing, check_duplicates, check_outliers, check_consistency, check_validity
from .scoring import calculate_quality_score

def audit_dataset(df: pd.DataFrame, numeric_cols: List[str], categorical_cols: List[str]) -> DataQualityReport:
    if df.empty:
        return DataQualityReport(
            score=0,
            score_breakdown={},
            missing=MissingReport(0,0,0,{},[]),
            duplicates=DuplicateReport(0,0,{},None),
            outliers=OutlierReport("IQR", {}, 0),
            consistency=ConsistencyReport({}, {}, {}, [], []),
            issues=[Issue(severity=IssueSeverity.CRITICAL.value, label=IssueLabel.DETECTED.value, column=None, description="Empty dataset")],
            is_empty=True
        )

    # Missing
    total_missing, total_cells, missing_pct, per_col_missing, worst_missing = check_missing(df)
    missing_report = MissingReport(
        total_missing_cells=total_missing,
        total_cells=total_cells,
        missing_pct=missing_pct,
        per_column=per_col_missing,
        worst_columns=worst_missing
    )

    # Duplicates
    dupe_rows, dupe_pct, dupe_id_cols, sample_dupes = check_duplicates(df)
    dupe_report = DuplicateReport(
        duplicate_row_count=dupe_rows,
        duplicate_pct=dupe_pct,
        duplicate_id_cols=dupe_id_cols,
        sample_duplicates=sample_dupes
    )

    # Outliers
    outlier_per_col, total_outlier_rows = check_outliers(df, numeric_cols, method="IQR")
    outlier_report = OutlierReport(
        method="IQR",
        per_column=outlier_per_col,
        total_outlier_rows=total_outlier_rows
    )

    # Consistency
    blank_counts, ws_counts, inconsist, constant_cols, high_card_cols = check_consistency(df, categorical_cols)
    consistency_report = ConsistencyReport(
        blank_string_counts=blank_counts,
        whitespace_counts=ws_counts,
        inconsistent_labels=inconsist,
        constant_columns=constant_cols,
        high_cardinality_columns=high_card_cols
    )

    # Validity
    validity_issues = check_validity(df, numeric_cols)

    # Scoring
    validity_count = len(validity_issues)
    consistency_count = len(blank_counts) + len(ws_counts) + len(inconsist) + len(constant_cols)
    score, breakdown = calculate_quality_score(missing_pct, dupe_pct, validity_count, consistency_count, len(df))

    # Build issues list for UI — improved wording
    issues = []

    # Completeness
    if missing_pct == 0:
        issues.append(Issue(severity=IssueSeverity.INFO.value, label=IssueLabel.DETECTED.value, column=None, description=f"✓ {100-missing_pct:.1f}% complete — no missing values"))
    else:
        for col in worst_missing[:5]:
            pct = per_col_missing[col]["pct"]
            if pct > 0:
                sev = IssueSeverity.WARNING.value if pct < 10 else IssueSeverity.CRITICAL.value
                label = IssueLabel.DETECTED.value if pct >5 else IssueLabel.POTENTIAL.value
                issues.append(Issue(severity=sev, label=label, column=col, description=f"{pct}% missing in {col} — {per_col_missing[col]['count']} of {len(df)} records", affected_count=per_col_missing[col]["count"]))

    # Duplicates — improved wording for uniqueness
    if dupe_rows == 0:
        issues.append(Issue(severity=IssueSeverity.INFO.value, label=IssueLabel.DETECTED.value, column=None, description="✓ Record uniqueness: 100% — no duplicate records detected"))
    else:
        issues.append(Issue(severity=IssueSeverity.WARNING.value, label=IssueLabel.DETECTED.value, column=None, description=f"{dupe_rows} duplicate records found ({dupe_pct}%) — review if duplicates are valid", affected_count=dupe_rows))

    # Outliers — improved wording: statistical anomaly, not error
    for col, info in outlier_per_col.items():
        issues.append(Issue(
            severity=IssueSeverity.INFO.value,  # Changed from WARNING to INFO — outliers are not errors
            label=IssueLabel.POTENTIAL.value, 
            column=col, 
            description=f"Statistical anomaly — {info['count']} observations in {col} fall outside IQR boundaries ({info['pct']}%). Not automatically considered data errors — investigate in context.",
            affected_count=info['count']
        ))

    # Consistency
    for col, cnt in blank_counts.items():
        issues.append(Issue(severity=IssueSeverity.WARNING.value, label=IssueLabel.DETECTED.value, column=col, description=f"{cnt} blank strings in {col} — empty strings may indicate missing data", affected_count=cnt))
    for col, cnt in ws_counts.items():
        issues.append(Issue(severity=IssueSeverity.WARNING.value, label=IssueLabel.DETECTED.value, column=col, description=f"{cnt} values with leading/trailing whitespace in {col} — consider trimming", affected_count=cnt))
    for col, detail in inconsist.items():
        examples = detail['examples'][0] if detail['examples'] else ('example','example')
        issues.append(Issue(severity=IssueSeverity.WARNING.value, label=IssueLabel.POTENTIAL.value, column=col, description=f"Inconsistent labels in {col}: e.g., {examples} represents same category with different casing/spacing — consider standardizing", affected_count=detail['total_groups']))

    for col in constant_cols:
        issues.append(Issue(severity=IssueSeverity.INFO.value, label=IssueLabel.DETECTED.value, column=col, description=f"Constant column {col} — contains only one unique value, removed because it adds no analytical value (e.g., Country = United States for all rows)"))

    # Validity
    for col, desc, cnt in validity_issues:
        issues.append(Issue(severity=IssueSeverity.WARNING.value, label=IssueLabel.DETECTED.value, column=col, description=desc, affected_count=cnt))

    if len(issues) == 0:
        issues.append(Issue(severity=IssueSeverity.INFO.value, label=IssueLabel.DETECTED.value, column=None, description="✓ High quality — no major issues detected"))

    return DataQualityReport(
        score=score,
        score_breakdown=breakdown,
        missing=missing_report,
        duplicates=dupe_report,
        outliers=outlier_report,
        consistency=consistency_report,
        issues=issues,
        is_empty=False
    )
