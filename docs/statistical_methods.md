# Statistical Methods — Why Each Choice

## Pearson vs Spearman
- Pearson measures linear correlation, sensitive to outliers, requires interval data
- Spearman measures rank correlation (monotonic), robust to outliers, works with ordinal
- We show both to demonstrate statistical maturity and to explain when to use which
- Interview answer: "I show Pearson for linear and Spearman as robust check — if Pearson high but Spearman low, suggests outlier-driven linear relationship"

## Welch's t-test (not Student's)
- Student's assumes equal variance; Welch's does not — safer default for real data
- We use equal_var=False
- When to use: compare mean of numeric across 2 categories (e.g., profit North vs South)
- Null: means equal, Alt: means differ

## ANOVA
- When >2 groups (e.g., profit across 4 regions)
- Null: all means equal, Alt: at least one differs
- If significant, recommend post-hoc (Tukey) — we mention but not implement to keep scope

## Chi-Square Test of Independence
- Categorical vs categorical (e.g., product category vs region)
- Null: independent, Alt: associated
- Requires contingency table >=2x2, expected frequencies >=5 (we don't enforce strictly but check shape)

## Confidence Intervals
- 95% CI via t-distribution: mean ± t_critical * SEM
- Interpretation: If repeated sampling, 95% of intervals contain true mean — not "95% chance true mean is in interval"
- Shows understanding beyond point estimates

## Effect Size — Cohen's d
- p-value tells significance, not practical importance
- Cohen's d: (mean1-mean2)/pooled_std
- Interpretation: <0.2 negligible, <0.5 small, <0.8 medium, >=0.8 large
- Interview: "I include effect size to avoid p-value hacking and show business relevance"

## Outliers — IQR vs Z-score
- IQR: Q1-1.5IQR, Q3+1.5IQR — robust, no normality assumption — default
- Z-score: mean ±3 std — assumes normality, sensitive to outliers
- We use IQR for MVP, mention Z-score as alternative

## Skewness & Kurtosis
- Skew: >0.5 right skewed, <-0.5 left skewed — guides use of median vs mean
- Kurtosis: heavy tails indicator

## Why Not Machine Learning?
- Fresher Data Analyst role focuses on descriptive, diagnostic, not predictive
- Adding ML without business question looks like tutorial
- We include simple forecasting as advanced optional, with disclaimer, to show awareness without overengineering
