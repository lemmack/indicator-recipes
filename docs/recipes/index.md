# Recipe Cards Overview

This collection provides standardized methods for 5 common public health indicators. Each recipe follows the same template:

1. **What it's for** - The purpose and appropriate use cases
2. **When appropriate** - Situations where this method applies
3. **Data needed** - Required fields and units
4. **Definition/formula** - Plain language + mathematical notation
5. **Implementation notes** - Edge cases and gotchas
6. **Worked example** - Real calculation with sample data
7. **Common mistakes** - Pitfalls to avoid
8. **Copy-paste code** - Ready-to-use Python snippet
9. **References** - Further reading

## The 5 Recipes

### [1. Crude Rate per 100,000 + Poisson CI](crude-rate.md)

The foundation of epidemiological analysis. Calculate disease rates and quantify uncertainty using Poisson-based confidence intervals.

**Use when:** Reporting basic incidence or prevalence in a single population.

---

### [2. Rolling Average](rolling-average.md)

Smooth noisy time series data while handling missing values appropriately. Essential for trend visualization and outbreak detection.

**Use when:** You have time series data and need to see underlying trends through noise.

---

### [3. Direct Age-Standardized Rate](age-standardized-rate.md)

Compare populations with different age structures using a weighted average of age-specific rates. The result is a **comparative index**, not an actual rate.

**Use when:** Comparing disease burden across populations with different demographics.

---

### [4. Rate Ratio & Rate Difference](rate-ratio-difference.md)

Quantify the relative and absolute difference in rates between two groups. Essential for health equity analysis and policy evaluation.

**Use when:** Comparing outcomes between exposed/unexposed, treatment/control, or any two populations.

---

### [5. Age-Specific Rate Table + Small-n Warnings](age-specific-rates.md)

Present rates stratified by age group with automatic flagging of unstable estimates based on small counts.

**Use when:** You need detailed age breakdowns but want to warn users about unreliable estimates.

---

## Important Concepts

### Comparability vs. Absolute Meaning

!!! warning "Know What You're Measuring"
    - **Crude rates** reflect actual burden in a population
    - **Age-standardized rates** are comparative indices for ranking - they don't represent actual burden anywhere
    - **Rate ratios** tell you relative risk but not absolute impact
    - **Rate differences** tell you absolute excess/deficit in terms the rate scale

Always match the indicator to your question:

| Question | Use |
|----------|-----|
| "How many cases per 100k in Region A?" | Crude rate |
| "Which region has higher age-adjusted burden?" | Age-standardized rate |
| "How much higher is the rate in group A vs B?" | Rate ratio |
| "How many excess cases per 100k in group A?" | Rate difference |

### Statistical Stability

Small numbers lead to unstable estimates. A rate based on 3 cases could easily be 5x higher or lower by random chance alone. Our recipes include:

- **Poisson confidence intervals** that widen appropriately for small counts
- **Small-n flags** to warn users about unreliable estimates

This is different from formal suppression policies (which also consider privacy). These recipes focus on statistical reliability warnings only.
