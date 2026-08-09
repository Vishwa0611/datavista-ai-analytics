"""
Quality score calculation — weighted, transparent.
Fixed: Uniqueness renamed to Record Uniqueness for clarity.
"""
from ..utils.constants import QUALITY_WEIGHTS

def calculate_quality_score(
    missing_pct: float,
    dupe_pct: float,
    validity_issues_count: int,
    consistency_issues_count: int,
    total_rows: int
) -> tuple[int, dict]:
    """
    Scoring:
    - Completeness 40%: 100 - missing_pct
    - Record Uniqueness 20%: 100 - min(50, dupe_pct*5) — no duplicate records
    - Validity 20%: penalize validity issues
    - Consistency 20%: penalize consistency issues
    """
    completeness = max(0, 100 - missing_pct)

    uniqueness_penalty = min(50, dupe_pct*5)  # 10% dupes -> 50 penalty, cap at 50
    record_uniqueness = max(0, 100 - uniqueness_penalty)

    # Validity: each issue penalizes but cap
    validity_penalty = min(30, validity_issues_count * 5)
    validity = max(0, 100 - validity_penalty)

    consistency_penalty = min(30, consistency_issues_count * 3)
    consistency = max(0, 100 - consistency_penalty)

    weighted = (
        completeness * QUALITY_WEIGHTS["completeness"] +
        record_uniqueness * QUALITY_WEIGHTS["record_uniqueness"] +
        validity * QUALITY_WEIGHTS["validity"] +
        consistency * QUALITY_WEIGHTS["consistency"]
    )

    score = int(round(weighted))

    breakdown = {
        "completeness": round(completeness,1),
        "record_uniqueness": round(record_uniqueness,1),
        "validity": round(validity,1),
        "consistency": round(consistency,1),
        "weighted_total": score,
        # Keep old key for backward compatibility
        "uniqueness": round(record_uniqueness,1)
    }

    return score, breakdown
