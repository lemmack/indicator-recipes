"""Core indicator calculation functions.

This module provides functions for calculating common public health indicators
including rates, confidence intervals, rolling averages, and age-standardized rates.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from scipy import stats

if TYPE_CHECKING:
    from collections.abc import Sequence

    import pandas as pd


def rate_per(
    cases: int | float | np.ndarray,
    population: int | float | np.ndarray,
    scale: int = 100_000,
) -> float | np.ndarray:
    """Calculate crude rate per population unit.

    Args:
        cases: Number of events/cases (numerator).
        population: Population at risk (denominator).
        scale: Multiplier for the rate (default 100,000 for "per 100k").

    Returns:
        Rate per scale population units.

    Raises:
        ValueError: If population is zero or negative, or scale is not positive.

    Examples:
        >>> rate_per(150, 50000)
        300.0
        >>> rate_per(25, 10000, scale=1000)
        2.5
    """
    if scale <= 0:
        raise ValueError(f"Scale must be positive, got {scale}")

    cases = np.asarray(cases)
    population = np.asarray(population)

    if np.any(population <= 0):
        raise ValueError("Population must be positive")

    rate = (cases / population) * scale

    # Check for overflow/underflow
    if np.any(~np.isfinite(rate)):
        import warnings

        warnings.warn(
            "Result contains non-finite values (inf or nan), likely due to extreme inputs",
            RuntimeWarning,
            stacklevel=2,
        )

    return float(rate) if rate.ndim == 0 else rate


def poisson_rate_ci(
    cases: int | float,
    population: int | float,
    scale: int = 100_000,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Calculate confidence interval for a rate assuming Poisson-distributed counts.

    Uses the exact method based on the chi-square distribution for the Poisson
    parameter. This is appropriate when events are rare and independent.

    Args:
        cases: Number of observed events (must be non-negative integer).
        population: Population at risk.
        scale: Multiplier for the rate (default 100,000).
        alpha: Significance level (default 0.05 for 95% CI). Must be in (0, 1).

    Returns:
        Tuple of (lower_bound, upper_bound) for the confidence interval.

    Raises:
        ValueError: If cases is negative, population is non-positive,
            scale is not positive, or alpha is not in (0, 1).

    Notes:
        For cases = 0, the lower bound is 0 and upper bound uses the one-sided
        interval. This method is exact and performs well even for small counts.

    References:
        Ulm K. A simple method to calculate the confidence interval of a
        standardized mortality ratio. Am J Epidemiol. 1990;131(2):373-375.

    Examples:
        >>> lower, upper = poisson_rate_ci(150, 50000)
        >>> round(lower, 1), round(upper, 1)
        (253.4, 352.0)
    """
    if cases < 0:
        raise ValueError(f"Cases must be non-negative, got {cases}")
    if population <= 0:
        raise ValueError(f"Population must be positive, got {population}")
    if scale <= 0:
        raise ValueError(f"Scale must be positive, got {scale}")
    if not (0 < alpha < 1):
        raise ValueError(f"Alpha must be between 0 and 1 (exclusive), got {alpha}")

    cases = int(round(cases))

    # Exact Poisson CI using chi-square distribution
    # Lower bound: chi2(alpha/2, 2*cases) / 2
    # Upper bound: chi2(1-alpha/2, 2*(cases+1)) / 2
    if cases == 0:
        lower_count = 0.0
    else:
        lower_count = stats.chi2.ppf(alpha / 2, 2 * cases) / 2

    upper_count = stats.chi2.ppf(1 - alpha / 2, 2 * (cases + 1)) / 2

    lower_rate = (lower_count / population) * scale
    upper_rate = (upper_count / population) * scale

    return (lower_rate, upper_rate)


def rolling_mean(
    series: pd.Series | Sequence[float],
    window: int,
    center: bool = False,
    min_periods: int | None = None,
) -> pd.Series:
    """Calculate rolling mean with configurable handling of missing data.

    Args:
        series: Time series data (can contain NaN values).
        window: Size of the moving window. Must be positive.
        center: If True, set the labels at the center of the window.
        min_periods: Minimum number of observations required to compute a value.
            If None, defaults to window size (requires full window). Must be positive.

    Returns:
        Series with rolling mean values.

    Raises:
        ValueError: If window is not positive, or min_periods is not positive.

    Notes:
        - NaN values in input are ignored in the calculation.
        - If min_periods is less than window, partial windows at edges will
          produce values (useful for avoiding data loss at series boundaries).
        - Setting center=True shifts results to align with the middle of the
          window, which is often preferred for visualization but introduces
          a look-ahead that's inappropriate for real-time applications.

    Examples:
        >>> import pandas as pd
        >>> s = pd.Series([1, 2, 3, 4, 5])
        >>> rolling_mean(s, window=3).tolist()
        [nan, nan, 2.0, 3.0, 4.0]
        >>> rolling_mean(s, window=3, min_periods=1).tolist()
        [1.0, 1.5, 2.0, 3.0, 4.0]
    """
    import pandas as pd

    if window <= 0:
        raise ValueError(f"Window must be positive, got {window}")

    if min_periods is not None and min_periods <= 0:
        raise ValueError(f"min_periods must be positive, got {min_periods}")

    if not isinstance(series, pd.Series):
        series = pd.Series(series)

    if min_periods is None:
        min_periods = window

    return series.rolling(window=window, center=center, min_periods=min_periods).mean()


def direct_age_standardized_rate(
    counts_by_age: Sequence[int | float] | np.ndarray,
    pop_by_age: Sequence[int | float] | np.ndarray,
    std_weights: Sequence[float] | np.ndarray,
    scale: int = 100_000,
) -> float:
    """Calculate directly age-standardized rate.

    This produces a weighted average of age-specific rates, where weights come
    from a standard population. The result is a COMPARATIVE INDEX, not an
    estimate of actual disease burden.

    Args:
        counts_by_age: Event counts for each age group.
        pop_by_age: Population for each age group.
        std_weights: Standard population weights for each age group.
            These should sum to 1 (proportions) or will be normalized.
        scale: Multiplier for the rate (default 100,000).

    Returns:
        Age-standardized rate per scale population.

    Raises:
        ValueError: If input arrays have mismatched lengths or invalid values.

    Important:
        Age-standardized rates are COMPARATIVE INDICES designed for comparing
        populations with different age structures. They do NOT represent the
        actual rate in any real population. The magnitude depends entirely on
        the choice of standard population.

    Notes:
        - All input arrays must have the same length (one element per age group).
        - Age groups must be defined consistently across all inputs.
        - Zero population in an age group will cause that group to be excluded
          (with a warning if counts > 0 for that group).

    Examples:
        >>> counts = [10, 20, 50]  # Young, middle, old
        >>> pop = [10000, 8000, 5000]
        >>> std_weights = [0.4, 0.35, 0.25]  # Standard population proportions
        >>> round(direct_age_standardized_rate(counts, pop, std_weights), 1)
        377.5
    """
    if scale <= 0:
        raise ValueError(f"Scale must be positive, got {scale}")

    counts_arr: np.ndarray = np.asarray(counts_by_age, dtype=float)
    pop_arr: np.ndarray = np.asarray(pop_by_age, dtype=float)
    weights_arr: np.ndarray = np.asarray(std_weights, dtype=float)

    # Validate inputs
    if not (len(counts_arr) == len(pop_arr) == len(weights_arr)):
        raise ValueError("All input arrays must have the same length")

    if np.any(counts_arr < 0):
        raise ValueError("Counts cannot be negative")

    if np.any(pop_arr < 0):
        raise ValueError("Population cannot be negative")

    if np.any(weights_arr < 0):
        raise ValueError("Standard weights cannot be negative")

    # Normalize weights to sum to 1
    weight_sum = np.sum(weights_arr)
    if weight_sum <= 0:
        raise ValueError("Standard weights must sum to a positive value")
    weights_arr = weights_arr / weight_sum

    # Handle zero population (exclude those age groups)
    valid_mask = pop_arr > 0

    if not np.all(valid_mask):
        # Check if we're losing cases
        lost_cases = np.sum(counts_arr[~valid_mask])
        if lost_cases > 0:
            import warnings

            warnings.warn(
                f"Excluding {lost_cases} cases in age groups with zero population",
                UserWarning,
                stacklevel=2,
            )
        # Re-normalize weights for valid groups only
        weights_arr = weights_arr[valid_mask]
        weights_arr = weights_arr / np.sum(weights_arr)
        counts_arr = counts_arr[valid_mask]
        pop_arr = pop_arr[valid_mask]

    # Calculate age-specific rates
    age_specific_rates = counts_arr / pop_arr

    # Weight and sum
    standardized_rate = np.sum(age_specific_rates * weights_arr) * scale

    return float(standardized_rate)


def rate_ratio(
    cases_a: int | float,
    pop_a: int | float,
    cases_b: int | float,
    pop_b: int | float,
) -> float:
    """Calculate rate ratio (relative risk) comparing two groups.

    Rate ratio = (Rate in group A) / (Rate in group B)

    Args:
        cases_a: Number of cases in group A (numerator group).
        pop_a: Population of group A.
        cases_b: Number of cases in group B (reference/denominator group).
        pop_b: Population of group B.

    Returns:
        Rate ratio (group A rate / group B rate).

    Raises:
        ValueError: If populations are non-positive or reference rate is zero.

    Notes:
        - RR = 1 indicates no difference between groups.
        - RR > 1 indicates higher rate in group A.
        - RR < 1 indicates lower rate in group A.
        - The choice of reference group matters for interpretation.

    Examples:
        >>> rate_ratio(50, 10000, 25, 10000)
        2.0
        >>> rate_ratio(30, 15000, 40, 10000)
        0.5
    """
    if pop_a <= 0 or pop_b <= 0:
        raise ValueError("Populations must be positive")

    rate_a = cases_a / pop_a
    rate_b = cases_b / pop_b

    if rate_b == 0:
        if rate_a == 0:
            return 1.0  # 0/0 case: no difference
        raise ValueError("Cannot compute rate ratio when reference rate is zero")

    return rate_a / rate_b


def rate_difference(
    cases_a: int | float,
    pop_a: int | float,
    cases_b: int | float,
    pop_b: int | float,
    scale: int = 100_000,
) -> float:
    """Calculate rate difference (absolute risk difference) between two groups.

    Rate difference = (Rate in group A) - (Rate in group B)

    Args:
        cases_a: Number of cases in group A.
        pop_a: Population of group A.
        cases_b: Number of cases in group B (reference group).
        pop_b: Population of group B.
        scale: Multiplier for the rates (default 100,000).

    Returns:
        Rate difference per scale population (group A - group B).

    Raises:
        ValueError: If populations are non-positive or scale is not positive.

    Notes:
        - Positive value indicates excess cases in group A.
        - Negative value indicates fewer cases in group A.
        - Unlike rate ratio, rate difference is on an absolute scale and
          can be used to estimate excess burden.

    Examples:
        >>> rate_difference(50, 10000, 25, 10000)
        250.0
        >>> rate_difference(30, 15000, 40, 10000, scale=1000)
        -2.0
    """
    if scale <= 0:
        raise ValueError(f"Scale must be positive, got {scale}")
    if pop_a <= 0 or pop_b <= 0:
        raise ValueError("Populations must be positive")

    rate_a = (cases_a / pop_a) * scale
    rate_b = (cases_b / pop_b) * scale

    return rate_a - rate_b


def flag_small_numbers(
    cases: int | float | np.ndarray | Sequence[int | float],
    threshold: int = 5,
) -> bool | np.ndarray:
    """Flag estimates based on small case counts as potentially unstable.

    Small counts produce unreliable rate estimates with wide confidence intervals.
    This function provides a simple flag for identifying such estimates.

    Args:
        cases: Number of cases (scalar or array).
        threshold: Counts below this value are flagged (default 5).

    Returns:
        Boolean or array of booleans. True indicates the estimate should be
        treated with caution due to small numbers.

    Notes:
        This is a WARNING flag, not a formal suppression rule. Different
        jurisdictions have different policies for suppression based on
        statistical reliability and/or privacy concerns.

        Common thresholds in practice:
        - n < 5: Very unstable, often suppressed
        - n < 10: Unstable, interpret with caution
        - n < 20: May have wide confidence intervals

    Examples:
        >>> flag_small_numbers(3)
        True
        >>> flag_small_numbers(10)
        False
        >>> flag_small_numbers([2, 5, 10, 3])
        array([ True, False, False,  True])
    """
    cases = np.asarray(cases)
    result = cases < threshold

    return bool(result) if result.ndim == 0 else result
