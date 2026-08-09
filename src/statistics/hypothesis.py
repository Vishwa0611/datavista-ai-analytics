"""
Hypothesis testing — t-tests, chi-square, ANOVA with safe guards.
"""
import pandas as pd
import numpy as np
from scipy import stats
from typing import List, Dict, Any
from ..validation.schema import HypothesisResult

def cohens_d(group1, group2):
    """Cohen's d effect size."""
    try:
        n1, n2 = len(group1), len(group2)
        s1, s2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        pooled = np.sqrt(((n1-1)*s1 + (n2-1)*s2) / (n1+n2-2))
        if pooled == 0:
            return 0.0
        return (np.mean(group1) - np.mean(group2)) / pooled
    except:
        return None

def interpret_effect_size(d):
    if d is None:
        return None
    ad = abs(d)
    if ad < 0.2:
        return "negligible effect"
    elif ad <0.5:
        return "small effect"
    elif ad <0.8:
        return "medium effect"
    else:
        return "large effect"

def auto_suggest_and_run_tests(df: pd.DataFrame, numeric_cols: List[str], categorical_cols: List[str]) -> List[HypothesisResult]:
    results = []
    # Filter out non-meaningful numeric columns like postal code
    meaningful_numeric = [c for c in numeric_cols if not any(x in c.lower() for x in ['postal', 'zip', 'pin', 'code', 'latitude', 'longitude'])]
    if meaningful_numeric:
        numeric_cols = meaningful_numeric

    # 1. Two-sample t-test: compare numeric metric across 2 categories of a categorical col (top 2 categories)
    if numeric_cols and categorical_cols:
        for num_col in numeric_cols[:2]:  # limit
            for cat_col in categorical_cols[:2]:
                try:
                    if df[cat_col].nunique() <2 or df[cat_col].nunique()>10:
                        continue
                    cats = df[cat_col].dropna().unique()[:2]
                    if len(cats) <2:
                        continue
                    g1 = pd.to_numeric(df[df[cat_col]==cats[0]][num_col], errors='coerce').dropna()
                    g2 = pd.to_numeric(df[df[cat_col]==cats[1]][num_col], errors='coerce').dropna()
                    if len(g1) <10 or len(g2) <10:
                        continue
                    # Check variance equality? Use Welch's t-test (equal_var=False) safe default
                    t_stat, p_val = stats.ttest_ind(g1, g2, equal_var=False, nan_policy='omit')
                    d = cohens_d(g1, g2)
                    effect_interp = interpret_effect_size(d)

                    decision = "Reject H0" if p_val <0.05 else "Fail to reject H0"
                    interp = f"Comparison of {num_col} between {cats[0]} vs {cats[1]}. Mean {cats[0]}={g1.mean():.2f}, Mean {cats[1]}={g2.mean():.2f}. p={p_val:.4f}. {decision} at α=0.05. {'Statistically significant difference.' if p_val<0.05 else 'No significant difference detected.'} Does NOT prove causation."

                    results.append(HypothesisResult(
                        test_name=f"Two-sample t-test (Welch): {num_col} by {cat_col}",
                        description=f"Does {num_col} differ between top 2 {cat_col} groups?",
                        null_hypothesis=f"No difference in mean {num_col} between {cats[0]} and {cats[1]}",
                        alt_hypothesis=f"Difference exists in mean {num_col}",
                        test_statistic=float(t_stat),
                        p_value=float(p_val),
                        alpha=0.05,
                        decision=decision,
                        interpretation=interp,
                        effect_size=float(d) if d is not None else None,
                        effect_interpretation=effect_interp
                    ))
                except Exception as e:
                    continue

    # 2. ANOVA: numeric across >2 categories
    if numeric_cols and categorical_cols:
        for num_col in numeric_cols[:1]:
            for cat_col in categorical_cols[:1]:
                try:
                    unique_cats = df[cat_col].dropna().unique()
                    if len(unique_cats) <3 or len(unique_cats)>6:
                        continue
                    groups = []
                    for cat in unique_cats[:5]:
                        g = pd.to_numeric(df[df[cat_col]==cat][num_col], errors='coerce').dropna()
                        if len(g) >=10:
                            groups.append(g)
                    if len(groups) <3:
                        continue
                    f_stat, p_val = stats.f_oneway(*groups)
                    decision = "Reject H0" if p_val <0.05 else "Fail to reject H0"
                    interp = f"ANOVA for {num_col} across {cat_col} groups ({len(groups)} groups). p={p_val:.4f}. {decision}. {'At least one group differs significantly.' if p_val<0.05 else 'No significant difference across groups.'} Follow with post-hoc if significant."

                    results.append(HypothesisResult(
                        test_name=f"ANOVA: {num_col} by {cat_col}",
                        description=f"Does {num_col} differ across {cat_col} groups?",
                        null_hypothesis=f"Means equal across all {cat_col} groups",
                        alt_hypothesis="At least one group mean differs",
                        test_statistic=float(f_stat),
                        p_value=float(p_val),
                        alpha=0.05,
                        decision=decision,
                        interpretation=interp
                    ))
                except:
                    continue

    # 3. Chi-square: categorical vs categorical
    if len(categorical_cols) >=2:
        try:
            cat1 = categorical_cols[0]
            cat2 = categorical_cols[1]
            if df[cat1].nunique() <=10 and df[cat2].nunique() <=10 and df[cat1].nunique()>1 and df[cat2].nunique()>1:
                contingency = pd.crosstab(df[cat1], df[cat2])
                if contingency.shape[0] >=2 and contingency.shape[1]>=2:
                    chi2, p, dof, expected = stats.chi2_contingency(contingency)
                    # Check expected frequencies - chi-square unreliable if any expected <5 or n <20
                    min_expected = expected.min() if hasattr(expected, 'min') else 0
                    total_n = contingency.values.sum()
                    is_unreliable = min_expected < 5 or total_n < 20
                    
                    decision = "Reject H0" if p <0.05 else "Fail to reject H0"
                    
                    if is_unreliable:
                        interp = f"Chi-square test for association between {cat1} and {cat2}. χ²={chi2:.2f}, p={p:.4f}, min expected={min_expected:.2f}, n={total_n}. {decision}. ⚠️ WARNING: Test assumptions severely violated (expected frequencies <5, n={total_n} very small). Result should NOT be treated as reliable evidence of association. Larger dataset or exact/Monte-Carlo test recommended. Does NOT imply causation."
                    else:
                        interp = f"Chi-square test for association between {cat1} and {cat2}. χ²={chi2:.2f}, p={p:.4f}, min expected={min_expected:.2f}. {decision}. {'Significant association' if p<0.05 else 'No significant association'} — does NOT imply causation."
                    results.append(HypothesisResult(
                        test_name=f"Chi-square: {cat1} vs {cat2}",
                        description=f"Association between {cat1} and {cat2}",
                        null_hypothesis=f"{cat1} and {cat2} are independent",
                        alt_hypothesis=f"{cat1} and {cat2} are associated",
                        test_statistic=float(chi2),
                        p_value=float(p),
                        alpha=0.05,
                        decision=decision,
                        interpretation=interp
                    ))
        except:
            pass

    return results
