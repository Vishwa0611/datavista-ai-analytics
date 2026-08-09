"""
Domain detector — scores dataset against domain keyword lists.
Simple, transparent, no ML.
"""
from typing import Dict, Tuple
import pandas as pd
from ..utils.constants import DOMAIN_KEYWORDS, Domain

def detect_domain(columns: list, sample_text: str = "") -> Tuple[str, float, Dict[str, int]]:
    """
    Returns: domain, confidence, keywords_matched dict
    confidence = matched keywords / total keywords in domain? Actually score / max.
    We use scoring: count of columns that contain keyword.
    """
    cols_lower = [c.lower() for c in columns]
    cols_str = " ".join(cols_lower) + " " + sample_text.lower()

    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        matched = 0
        matched_detail = {}
        for kw in keywords:
            if kw in cols_str:
                matched += 1
                matched_detail[kw] = cols_str.count(kw)
        scores[domain.value] = {"total_matched": matched, "details": matched_detail}

    # Find best domain
    best_domain = Domain.UNKNOWN.value
    best_score = 0
    for dom, data in scores.items():
        if data["total_matched"] > best_score:
            best_score = data["total_matched"]
            best_domain = dom

    # Confidence: best matched / (total keywords in best domain) * scaling, plus count
    if best_domain != Domain.UNKNOWN.value:
        total_keywords_in_best = len(DOMAIN_KEYWORDS[Domain(best_domain)])
        confidence = min(0.95, (best_score / max(1, total_keywords_in_best*0.5)))
        # Boost if >3 matches
        if best_score >= 3:
            confidence = min(0.95, confidence + 0.2)
        # If zero matches, unknown
        if best_score == 0:
            best_domain = Domain.UNKNOWN.value
            confidence = 0.0
    else:
        confidence = 0.0

    # Flatten for return
    keywords_matched = scores.get(best_domain, {}).get("details", {}) if best_domain != Domain.UNKNOWN.value else {}

    return best_domain, round(confidence, 2), keywords_matched

def list_all_domain_scores(columns: list) -> Dict[str, int]:
    """Return all domain scores for debugging/UI."""
    cols_str = " ".join([c.lower() for c in columns])
    result = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        matched = sum(1 for kw in keywords if kw in cols_str)
        result[domain.value] = matched
    return result
