# Public Health Indicator Recipe Cards

Welcome to **Indicator Recipe Cards** - a collection of reproducible methods for calculating common public health indicators.

## What is this?

This site provides **5 recipe cards** for essential epidemiological calculations, along with a Python package implementing each method. Every recipe includes:

- Clear explanation of what the indicator measures
- When it's appropriate (and inappropriate) to use
- Mathematical formulas in plain language
- Working code examples with real data
- Common pitfalls to avoid

## Quick Start

### Install the package

```bash
pip install indicator-recipes
```

### Calculate a crude rate

```python
from indicator_recipes import rate_per, poisson_rate_ci

# 150 cases in a population of 50,000
rate = rate_per(150, 50000)  # Returns 300.0 per 100,000

# Get 95% confidence interval
lower, upper = poisson_rate_ci(150, 50000)
print(f"Rate: {rate:.1f} (95% CI: {lower:.1f}-{upper:.1f})")
```

## The Recipe Cards

| Recipe | What it does |
|--------|--------------|
| [Crude Rate](recipes/crude-rate.md) | Basic rate per population + Poisson CI |
| [Rolling Average](recipes/rolling-average.md) | Smooth time series with missing data handling |
| [Age-Standardized Rate](recipes/age-standardized-rate.md) | Compare populations with different age structures |
| [Rate Ratio & Difference](recipes/rate-ratio-difference.md) | Compare rates between groups |
| [Age-Specific Rates](recipes/age-specific-rates.md) | Stratified rates with small-n warnings |

## Key Principles

!!! warning "Comparability vs. Absolute Meaning"
    Many indicators (especially age-standardized rates) are **comparative indices** designed for ranking or comparing populations. They do NOT represent actual disease burden in any real population. Always consider what question you're trying to answer.

!!! tip "Reproducibility"
    All examples use committed data snapshots. No network calls, no credentials, no restricted datasets. You can reproduce every calculation.

## Who is this for?

- **Epidemiologists** wanting standardized, tested implementations
- **Data analysts** working with health data for the first time
- **Students** learning public health methods
- **Anyone** needing clear documentation of indicator calculations

## Source Code

The Python package and documentation source are available on [GitHub](https://github.com/your-org/indicator-recipes).

```bash
# Clone and install for development
git clone https://github.com/your-org/indicator-recipes.git
cd indicator-recipes
pip install -e ".[dev,docs]"
pytest  # Run tests
mkdocs serve  # Preview docs
```
