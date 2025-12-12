"""Public health indicator calculations for reproducible epidemiology."""

from indicator_recipes.core import (
    direct_age_standardized_rate,
    flag_small_numbers,
    poisson_rate_ci,
    rate_difference,
    rate_per,
    rate_ratio,
    rolling_mean,
)

__all__ = [
    "rate_per",
    "poisson_rate_ci",
    "rolling_mean",
    "direct_age_standardized_rate",
    "rate_ratio",
    "rate_difference",
    "flag_small_numbers",
]

__version__ = "0.1.0"
