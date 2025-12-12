"""Tests for core indicator functions.

All tests use toy data only - no network calls.
"""

import numpy as np
import pandas as pd
import pytest

from indicator_recipes import (
    direct_age_standardized_rate,
    flag_small_numbers,
    poisson_rate_ci,
    rate_difference,
    rate_per,
    rate_ratio,
    rolling_mean,
)


class TestRatePer:
    """Tests for rate_per function."""

    def test_basic_calculation(self):
        """Test basic rate calculation."""
        result = rate_per(150, 50000, scale=100_000)
        assert result == 300.0

    def test_different_scale(self):
        """Test with different scale."""
        result = rate_per(25, 10000, scale=1000)
        assert result == 2.5

    def test_array_input(self):
        """Test with array inputs."""
        cases = np.array([10, 20, 30])
        pop = np.array([1000, 2000, 3000])
        result = rate_per(cases, pop, scale=1000)
        np.testing.assert_array_equal(result, [10.0, 10.0, 10.0])

    def test_zero_cases(self):
        """Test with zero cases."""
        result = rate_per(0, 10000)
        assert result == 0.0

    def test_zero_population_raises(self):
        """Test that zero population raises error."""
        with pytest.raises(ValueError, match="Population must be positive"):
            rate_per(10, 0)

    def test_negative_population_raises(self):
        """Test that negative population raises error."""
        with pytest.raises(ValueError, match="Population must be positive"):
            rate_per(10, -100)


class TestPoissonRateCI:
    """Tests for poisson_rate_ci function."""

    def test_basic_ci(self):
        """Test basic confidence interval calculation."""
        lower, upper = poisson_rate_ci(150, 50000)
        # Expected values from chi-square method
        assert 250 < lower < 260
        assert 350 < upper < 360

    def test_zero_cases(self):
        """Test CI with zero cases."""
        lower, upper = poisson_rate_ci(0, 10000)
        assert lower == 0.0
        assert upper > 0

    def test_small_count(self):
        """Test CI with small count (n=5)."""
        lower, upper = poisson_rate_ci(5, 10000)
        assert lower > 0
        assert upper > lower
        # CI should be wide for small counts
        assert (upper - lower) > lower

    def test_negative_cases_raises(self):
        """Test that negative cases raises error."""
        with pytest.raises(ValueError, match="Cases must be non-negative"):
            poisson_rate_ci(-1, 10000)

    def test_zero_population_raises(self):
        """Test that zero population raises error."""
        with pytest.raises(ValueError, match="Population must be positive"):
            poisson_rate_ci(10, 0)

    def test_custom_alpha(self):
        """Test with custom alpha (90% CI)."""
        lower_95, upper_95 = poisson_rate_ci(100, 10000, alpha=0.05)
        lower_90, upper_90 = poisson_rate_ci(100, 10000, alpha=0.10)
        # 90% CI should be narrower than 95% CI
        assert (upper_90 - lower_90) < (upper_95 - lower_95)


class TestRollingMean:
    """Tests for rolling_mean function."""

    def test_basic_rolling(self):
        """Test basic rolling mean."""
        s = pd.Series([1, 2, 3, 4, 5])
        result = rolling_mean(s, window=3)
        expected = [np.nan, np.nan, 2.0, 3.0, 4.0]
        pd.testing.assert_series_equal(result, pd.Series(expected))

    def test_min_periods(self):
        """Test with min_periods less than window."""
        s = pd.Series([1, 2, 3, 4, 5])
        result = rolling_mean(s, window=3, min_periods=1)
        expected = [1.0, 1.5, 2.0, 3.0, 4.0]
        pd.testing.assert_series_equal(result, pd.Series(expected))

    def test_centered_window(self):
        """Test centered rolling mean."""
        s = pd.Series([1, 2, 3, 4, 5])
        result = rolling_mean(s, window=3, center=True, min_periods=1)
        # Center shifts the result
        expected = [1.5, 2.0, 3.0, 4.0, 4.5]
        pd.testing.assert_series_equal(result, pd.Series(expected))

    def test_with_missing_values(self):
        """Test handling of NaN values."""
        s = pd.Series([1, np.nan, 3, 4, 5])
        result = rolling_mean(s, window=3, min_periods=2)
        # NaN is skipped in calculation
        assert pd.isna(result.iloc[0])
        assert result.iloc[2] == 2.0  # (1 + 3) / 2
        assert result.iloc[3] == 3.5  # (3 + 4) / 2
        assert result.iloc[4] == 4.0  # (3 + 4 + 5) / 3

    def test_list_input(self):
        """Test with list input instead of Series."""
        data = [1, 2, 3, 4, 5]
        result = rolling_mean(data, window=3)
        assert len(result) == 5
        assert result.iloc[2] == 2.0


class TestDirectAgeStandardizedRate:
    """Tests for direct_age_standardized_rate function."""

    def test_basic_calculation(self):
        """Test basic age-standardized rate calculation."""
        counts = [10, 20, 50]  # Young, middle, old
        pop = [10000, 8000, 5000]
        std_weights = [0.4, 0.35, 0.25]
        result = direct_age_standardized_rate(counts, pop, std_weights)
        # Manual calculation:
        # Age-specific rates: 10/10000=0.001, 20/8000=0.0025, 50/5000=0.01
        # Weighted: 0.001*0.4 + 0.0025*0.35 + 0.01*0.25 = 0.003775
        # Scaled: 0.003775 * 100000 = 377.5
        assert abs(result - 377.5) < 0.1

    def test_weights_normalized(self):
        """Test that weights are normalized if they don't sum to 1."""
        counts = [10, 20]
        pop = [10000, 10000]
        # Weights don't sum to 1
        std_weights = [100, 100]
        result = direct_age_standardized_rate(counts, pop, std_weights)
        # Should be same as with [0.5, 0.5]
        expected = direct_age_standardized_rate(counts, pop, [0.5, 0.5])
        assert result == expected

    def test_mismatched_lengths_raises(self):
        """Test that mismatched array lengths raise error."""
        with pytest.raises(ValueError, match="same length"):
            direct_age_standardized_rate([10, 20], [10000], [0.5, 0.5])

    def test_negative_counts_raises(self):
        """Test that negative counts raise error."""
        with pytest.raises(ValueError, match="Counts cannot be negative"):
            direct_age_standardized_rate([-1, 20], [10000, 10000], [0.5, 0.5])

    def test_zero_population_warning(self):
        """Test warning when age group has zero population but cases."""
        with pytest.warns(UserWarning, match="Excluding"):
            direct_age_standardized_rate([10, 5], [10000, 0], [0.5, 0.5])


class TestRateRatio:
    """Tests for rate_ratio function."""

    def test_equal_rates(self):
        """Test rate ratio when rates are equal."""
        result = rate_ratio(50, 10000, 50, 10000)
        assert result == 1.0

    def test_double_rate(self):
        """Test when group A has double the rate."""
        result = rate_ratio(50, 10000, 25, 10000)
        assert result == 2.0

    def test_half_rate(self):
        """Test when group A has half the rate."""
        result = rate_ratio(25, 10000, 50, 10000)
        assert result == 0.5

    def test_different_populations(self):
        """Test with different population sizes."""
        result = rate_ratio(30, 15000, 40, 10000)
        # Rate A = 30/15000 = 0.002
        # Rate B = 40/10000 = 0.004
        # Ratio = 0.5
        assert result == 0.5

    def test_zero_reference_rate_raises(self):
        """Test that zero reference rate raises error."""
        with pytest.raises(ValueError, match="reference rate is zero"):
            rate_ratio(10, 10000, 0, 10000)

    def test_both_zero_returns_one(self):
        """Test that both zero rates returns 1."""
        result = rate_ratio(0, 10000, 0, 10000)
        assert result == 1.0

    def test_zero_population_raises(self):
        """Test that zero population raises error."""
        with pytest.raises(ValueError, match="Populations must be positive"):
            rate_ratio(10, 0, 10, 10000)


class TestRateDifference:
    """Tests for rate_difference function."""

    def test_positive_difference(self):
        """Test positive rate difference."""
        result = rate_difference(50, 10000, 25, 10000)
        # Rate A = 500/100k, Rate B = 250/100k
        # Difference = 250/100k
        assert result == 250.0

    def test_negative_difference(self):
        """Test negative rate difference."""
        result = rate_difference(25, 10000, 50, 10000)
        assert result == -250.0

    def test_zero_difference(self):
        """Test zero difference when rates are equal."""
        result = rate_difference(50, 10000, 50, 10000)
        assert result == 0.0

    def test_different_scale(self):
        """Test with different scale."""
        result = rate_difference(30, 15000, 40, 10000, scale=1000)
        # Rate A = 30/15000 * 1000 = 2
        # Rate B = 40/10000 * 1000 = 4
        # Difference = -2
        assert result == -2.0

    def test_zero_population_raises(self):
        """Test that zero population raises error."""
        with pytest.raises(ValueError, match="Populations must be positive"):
            rate_difference(10, 10000, 10, 0)


class TestFlagSmallNumbers:
    """Tests for flag_small_numbers function."""

    def test_below_threshold(self):
        """Test flagging below default threshold."""
        assert flag_small_numbers(3) is True
        assert flag_small_numbers(4) is True

    def test_at_threshold(self):
        """Test at threshold (should not flag)."""
        assert flag_small_numbers(5) is False

    def test_above_threshold(self):
        """Test above threshold."""
        assert flag_small_numbers(10) is False

    def test_custom_threshold(self):
        """Test with custom threshold."""
        assert flag_small_numbers(7, threshold=10) is True
        assert flag_small_numbers(10, threshold=10) is False

    def test_array_input(self):
        """Test with array input."""
        result = flag_small_numbers([2, 5, 10, 3])
        expected = np.array([True, False, False, True])
        np.testing.assert_array_equal(result, expected)

    def test_zero_cases(self):
        """Test with zero cases."""
        assert flag_small_numbers(0) is True
