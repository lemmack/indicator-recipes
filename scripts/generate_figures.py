#!/usr/bin/env python
"""Generate all figures for the documentation.

This script creates all the plots used in the recipe card documentation.
Run from the project root: python scripts/generate_figures.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add src to path for local development
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from indicator_recipes import (
    direct_age_standardized_rate,
    flag_small_numbers,
    poisson_rate_ci,
    rate_difference,
    rate_per,
    rate_ratio,
    rolling_mean,
)

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "docs" / "assets" / "data"
FIGURES_DIR = PROJECT_ROOT / "docs" / "assets" / "figures"

# Ensure figures directory exists
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Style settings
plt.style.use("seaborn-v0_8-whitegrid")
COLORS = {
    "primary": "#009688",
    "secondary": "#FF9800",
    "accent": "#E91E63",
    "neutral": "#607D8B",
}


def generate_crude_rate_figure():
    """Generate figure for crude rate recipe."""
    df = pd.read_csv(DATA_DIR / "crude_rate_example.csv")

    # Calculate rates and CIs
    rates = []
    lower_cis = []
    upper_cis = []

    for _, row in df.iterrows():
        rate = rate_per(row["cases"], row["population"])
        lower, upper = poisson_rate_ci(row["cases"], row["population"])
        rates.append(rate)
        lower_cis.append(lower)
        upper_cis.append(upper)

    df["rate"] = rates
    df["lower_ci"] = lower_cis
    df["upper_ci"] = upper_cis

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Sort by rate for better visualization
    df_sorted = df.sort_values("rate", ascending=True)

    y_pos = np.arange(len(df_sorted))

    # Plot bars
    bars = ax.barh(y_pos, df_sorted["rate"], color=COLORS["primary"], alpha=0.7)

    # Add error bars for CI
    ax.errorbar(
        df_sorted["rate"],
        y_pos,
        xerr=[
            df_sorted["rate"] - df_sorted["lower_ci"],
            df_sorted["upper_ci"] - df_sorted["rate"],
        ],
        fmt="none",
        color=COLORS["neutral"],
        capsize=4,
        linewidth=2,
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(df_sorted["region"])
    ax.set_xlabel("Rate per 100,000 population")
    ax.set_title("Crude Rates by Region with 95% Poisson Confidence Intervals")

    # Add rate labels
    for i, (rate, upper) in enumerate(zip(df_sorted["rate"], df_sorted["upper_ci"])):
        ax.text(upper + 10, i, f"{rate:.1f}", va="center", fontsize=9)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "crude_rate_comparison.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Generated: crude_rate_comparison.png")


def generate_rolling_average_figure():
    """Generate figure for rolling average recipe."""
    df = pd.read_csv(DATA_DIR / "time_series_example.csv")
    df["date"] = pd.to_datetime(df["date"])

    # Calculate rolling averages
    df["rolling_3"] = rolling_mean(df["cases"], window=3, min_periods=1)
    df["rolling_7"] = rolling_mean(df["cases"], window=7, min_periods=1)

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot raw data
    ax.scatter(
        df["date"],
        df["cases"],
        color=COLORS["neutral"],
        alpha=0.5,
        s=50,
        label="Weekly cases (raw)",
        zorder=3,
    )

    # Plot rolling averages
    ax.plot(
        df["date"],
        df["rolling_3"],
        color=COLORS["primary"],
        linewidth=2,
        label="3-week rolling average",
        zorder=2,
    )
    ax.plot(
        df["date"],
        df["rolling_7"],
        color=COLORS["secondary"],
        linewidth=2,
        label="7-week rolling average",
        zorder=2,
    )

    # Highlight missing data
    missing_dates = df[df["cases"].isna()]["date"]
    for date in missing_dates:
        ax.axvline(date, color=COLORS["accent"], linestyle="--", alpha=0.5, linewidth=1)

    ax.set_xlabel("Date")
    ax.set_ylabel("Weekly Cases")
    ax.set_title("Time Series with Rolling Averages (dashed lines = missing data)")
    ax.legend(loc="upper left")

    plt.xticks(rotation=45)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "rolling_average_comparison.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Generated: rolling_average_comparison.png")


def generate_age_standardized_figure():
    """Generate figure for age-standardized rate recipe."""
    df = pd.read_csv(DATA_DIR / "age_stratified_example.csv")
    std_pop = pd.read_csv(DATA_DIR / "standard_population.csv")

    # Calculate crude and age-standardized rates for each region
    results = []
    for region in df["region"].unique():
        region_data = df[df["region"] == region]

        # Crude rate
        total_cases = region_data["cases"].sum()
        total_pop = region_data["population"].sum()
        crude = rate_per(total_cases, total_pop)

        # Age-standardized rate
        asr = direct_age_standardized_rate(
            region_data["cases"].values,
            region_data["population"].values,
            std_pop["weight"].values,
        )

        results.append({"region": region, "crude_rate": crude, "asr": asr})

    results_df = pd.DataFrame(results)

    fig, ax = plt.subplots(figsize=(8, 6))

    x = np.arange(len(results_df))
    width = 0.35

    bars1 = ax.bar(
        x - width / 2,
        results_df["crude_rate"],
        width,
        label="Crude Rate",
        color=COLORS["neutral"],
        alpha=0.7,
    )
    bars2 = ax.bar(
        x + width / 2,
        results_df["asr"],
        width,
        label="Age-Standardized Rate",
        color=COLORS["primary"],
        alpha=0.7,
    )

    ax.set_ylabel("Rate per 100,000")
    ax.set_title("Crude vs Age-Standardized Rates by Region")
    ax.set_xticks(x)
    ax.set_xticklabels(results_df["region"])
    ax.legend()

    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(
            f"{height:.0f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    for bar in bars2:
        height = bar.get_height()
        ax.annotate(
            f"{height:.0f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "age_standardized_comparison.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Generated: age_standardized_comparison.png")


def generate_rate_ratio_figure():
    """Generate figure for rate ratio/difference recipe."""
    df = pd.read_csv(DATA_DIR / "age_stratified_example.csv")

    # Calculate rates for each region
    region_a = df[df["region"] == "Region A"]
    region_b = df[df["region"] == "Region B"]

    cases_a = region_a["cases"].sum()
    pop_a = region_a["population"].sum()
    cases_b = region_b["cases"].sum()
    pop_b = region_b["population"].sum()

    rate_a = rate_per(cases_a, pop_a)
    rate_b = rate_per(cases_b, pop_b)

    rr = rate_ratio(cases_a, pop_a, cases_b, pop_b)
    rd = rate_difference(cases_a, pop_a, cases_b, pop_b)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Bar chart comparing rates
    ax1 = axes[0]
    regions = ["Region A", "Region B"]
    rates = [rate_a, rate_b]
    bars = ax1.bar(regions, rates, color=[COLORS["primary"], COLORS["secondary"]], alpha=0.7)
    ax1.set_ylabel("Rate per 100,000")
    ax1.set_title("Rate Comparison")

    for bar, rate in zip(bars, rates):
        ax1.annotate(
            f"{rate:.1f}",
            xy=(bar.get_x() + bar.get_width() / 2, rate),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    # Right: Metrics summary
    ax2 = axes[1]
    ax2.axis("off")

    summary_text = f"""
    Rate Ratio (A / B):  {rr:.2f}

    Rate Difference (A - B):  {rd:.1f} per 100,000


    Interpretation:
    • Rate Ratio = {rr:.2f} means Region A's rate is
      {rr:.0%} of Region B's rate

    • Rate Difference = {rd:.1f} means Region A has
      {abs(rd):.1f} {"more" if rd > 0 else "fewer"} cases per 100,000
      compared to Region B
    """

    ax2.text(
        0.1,
        0.5,
        summary_text,
        transform=ax2.transAxes,
        fontsize=12,
        verticalalignment="center",
        fontfamily="monospace",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )
    ax2.set_title("Rate Ratio & Rate Difference")

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "rate_ratio_difference.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Generated: rate_ratio_difference.png")


def generate_age_specific_figure():
    """Generate figure for age-specific rates with small-n warnings."""
    df = pd.read_csv(DATA_DIR / "small_numbers_example.csv")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for idx, region in enumerate(df["region"].unique()):
        ax = axes[idx]
        region_data = df[df["region"] == region].copy()

        # Calculate rates
        region_data["rate"] = rate_per(
            region_data["cases"].values, region_data["population"].values
        )
        region_data["small_n_flag"] = flag_small_numbers(region_data["cases"].values)

        x = np.arange(len(region_data))

        # Color bars based on small-n flag
        colors = [
            COLORS["accent"] if flag else COLORS["primary"]
            for flag in region_data["small_n_flag"]
        ]

        bars = ax.bar(x, region_data["rate"], color=colors, alpha=0.7)

        ax.set_xticks(x)
        ax.set_xticklabels(region_data["age_group"], rotation=45, ha="right")
        ax.set_ylabel("Rate per 100,000")
        ax.set_title(f"Age-Specific Rates: {region}")

        # Add count labels and warning symbols
        for i, (bar, row) in enumerate(zip(bars, region_data.itertuples())):
            height = bar.get_height()
            label = f"n={row.cases}"
            if row.small_n_flag:
                label += " ⚠"
            ax.annotate(
                label,
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
                color=COLORS["accent"] if row.small_n_flag else COLORS["neutral"],
            )

    # Add legend
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor=COLORS["primary"], alpha=0.7, label="Stable estimate (n ≥ 5)"),
        Patch(facecolor=COLORS["accent"], alpha=0.7, label="Unstable estimate (n < 5) ⚠"),
    ]
    axes[1].legend(handles=legend_elements, loc="upper right")

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "age_specific_rates.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Generated: age_specific_rates.png")


def main():
    """Generate all figures."""
    print(f"Generating figures in {FIGURES_DIR}")
    print("-" * 40)

    generate_crude_rate_figure()
    generate_rolling_average_figure()
    generate_age_standardized_figure()
    generate_rate_ratio_figure()
    generate_age_specific_figure()

    print("-" * 40)
    print("All figures generated successfully!")


if __name__ == "__main__":
    main()
