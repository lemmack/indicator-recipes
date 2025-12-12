# Public Health Indicator Recipe Cards

A small static site with **5 reproducible "indicator recipe cards"** plus a Python package implementing the calculations. Works with public data or committed snapshots only.

## Quick Start

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package with dev dependencies
pip install -e ".[dev,docs]"

# Run tests
pytest

# Generate figures
python scripts/generate_figures.py

# Serve documentation locally
mkdocs serve
```

## Recipe Cards

1. **Crude rate per 100k + Poisson CI** - Basic rate calculation with confidence intervals
2. **Rolling average** - Time series smoothing with missing data handling
3. **Direct age-standardized rate** - Comparative index using standard population
4. **Rate ratio + rate difference** - Comparing rates between groups
5. **Age-specific rate table** - Stratified rates with small-n warnings

## Package Usage

```python
from indicator_recipes import (
    rate_per,
    poisson_rate_ci,
    rolling_mean,
    direct_age_standardized_rate,
    rate_ratio,
    rate_difference,
    flag_small_numbers,
)

# Calculate crude rate per 100,000
rate = rate_per(cases=150, population=50000, scale=100_000)
# Returns: 300.0

# Get confidence interval
lower, upper = poisson_rate_ci(cases=150, population=50000)
# Returns approximate 95% CI bounds
```

## Project Structure

```
indicator-recipes/
├── src/indicator_recipes/    # Python package
├── docs/                     # MkDocs documentation
│   ├── assets/
│   │   ├── data/            # Example CSV datasets
│   │   └── figures/         # Generated plots
│   └── recipes/             # Recipe card pages
├── scripts/                  # Figure generation scripts
├── tests/                    # pytest tests
└── .github/workflows/        # CI/CD
```

## Development

```bash
# Install pre-commit hooks
pre-commit install

# Run linting
ruff check src tests

# Run tests with coverage
pytest --cov=indicator_recipes
```

## License

GPL-3.0
