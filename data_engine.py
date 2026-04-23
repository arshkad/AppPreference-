"""
this is data_engine.py
Core data science module: generation, cleaning, EDA, and analysis.
Uses Pandas, NumPy — mirrors the research workflow described in the project brief.
"""

import numpy as np
import pandas as pd
import json
from pathlib import Path

np.random.seed(42)

# ── Constants ──────────────────────────────────────────────────────────────────
CATEGORIES    = ["Social", "Utility", "Entertainment", "Productivity", "Health"]
AGE_GROUPS    = ["18–24", "25–34", "35–44", "45+"]
GENDERS       = ["Male", "Female", "Non-binary"]
REGIONS       = ["West", "Midwest", "South", "Northeast"]
MONTHS        = ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]

N = 5247   # total user records
# ── 1. Data Generation ─────────────────────────────────────────────────────────
def generate_raw_data() -> pd.DataFrame:
    """Simulate the 5,000+ user dataset with realistic distributions."""
    age_weights    = [0.30, 0.35, 0.22, 0.13]
    gender_weights = [0.47, 0.46, 0.07]
    region_weights = [0.24, 0.22, 0.30, 0.24]

    age    = np.random.choice(AGE_GROUPS, size=N, p=age_weights)
    gender = np.random.choice(GENDERS,    size=N, p=gender_weights)
    region = np.random.choice(REGIONS,    size=N, p=region_weights)

    # Engagement hours per category — shaped by age group
    base = {
        "18–24": [2.1, 0.6, 1.5, 0.4, 0.3],
        "25–34": [1.5, 1.0, 1.3, 0.9, 0.5],
        "35–44": [0.9, 1.1, 1.0, 1.5, 0.7],
        "45+":   [0.7, 1.3, 1.1, 1.0, 1.0],
    }

    hours = np.zeros((N, len(CATEGORIES)))
    for i, ag in enumerate(age):
        mu = base[ag]
        hours[i] = np.abs(np.random.normal(mu, 0.3, len(CATEGORIES)))

    df = pd.DataFrame(hours, columns=[f"hours_{c.lower()}" for c in CATEGORIES])
    df["age_group"] = age
    df["gender"]    = gender
    df["region"]    = region

    # Inject ~3% dirty rows (NaN + outliers) for cleaning demo
    dirty_idx = np.random.choice(N, size=int(N * 0.03), replace=False)
    for col in df.columns[:5]:
        df.loc[dirty_idx[:len(dirty_idx)//2], col] = np.nan
    df.loc[dirty_idx[len(dirty_idx)//2:], "hours_social"] = 99.0  # outliers

    return df

# ── 2. Data Cleaning ───────────────────────────────────────────────────────────
def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    End-to-end cleaning pipeline.
    Returns cleaned dataframe + a cleaning report dict.
    """
    report = {"raw_rows": len(df)}

    # Drop rows with any NaN in hour columns
    hour_cols = [c for c in df.columns if c.startswith("hours_")]
    before = len(df)
    df = df.dropna(subset=hour_cols).copy()
    report["dropped_nulls"] = before - len(df)

    # Cap outliers at 99th percentile per column
    capped = 0
    for col in hour_cols:
        cap = df[col].quantile(0.99)
        mask = df[col] > cap
        capped += mask.sum()
        df.loc[mask, col] = cap
    report["capped_outliers"] = int(capped)

    # Ensure non-negative
    df[hour_cols] = df[hour_cols].clip(lower=0)

    report["clean_rows"] = len(df)
    report["missing_pct_before"] = round(
        (report["dropped_nulls"] / report["raw_rows"]) * 100, 1
    )
    return df, report

# ── 3. EDA helpers ─────────────────────────────────────────────────────────────
def summary_stats(df: pd.DataFrame) -> dict:
    """Descriptive statistics for the report."""
    hour_cols = [c for c in df.columns if c.startswith("hours_")]
    stats = df[hour_cols].describe().round(2).to_dict()
    return stats


def category_totals(df: pd.DataFrame) -> list[dict]:
    """Per-category aggregate metrics."""
    hour_cols = [c for c in df.columns if c.startswith("hours_")]
    totals = []
    total_users = len(df)
    for col, cat in zip(hour_cols, CATEGORIES):
        engaged = (df[col] > 0.5).sum()
        totals.append({
            "category":    cat,
            "avg_hours":   round(float(df[col].mean()), 2),
            "median_hours":round(float(df[col].median()), 2),
            "users":       int(engaged),
            "engagement_rate": round(engaged / total_users * 100, 1),
        })
    return sorted(totals, key=lambda x: x["avg_hours"], reverse=True)


def engagement_by_group(df: pd.DataFrame, group_col: str) -> dict:
    """
    Mean engagement hours per category, broken down by a demographic column.
    Used for the grouped bar chart.
    """
    hour_cols = [c for c in df.columns if c.startswith("hours_")]
    grouped = (
        df.groupby(group_col)[hour_cols]
        .mean()
        .round(2)
    )
    # Normalise to percentage share within each group
    row_sums = grouped.sum(axis=1)
    pct = grouped.div(row_sums, axis=0).mul(100).round(1)
    return {
        "groups":    list(pct.index),
        "categories": CATEGORIES,
        "values":    pct.values.tolist(),
    }


def overall_distribution(df: pd.DataFrame) -> dict:
    """Overall share of total usage per category (for donut chart)."""
    hour_cols = [c for c in df.columns if c.startswith("hours_")]
    totals = df[hour_cols].sum()
    pct = (totals / totals.sum() * 100).round(1)
    return {
        "labels": CATEGORIES,
        "values": pct.values.tolist(),
    }


def monthly_trend() -> dict:
    """
    Simulated 6-month trend data (as if sampled each month).
    Returns hours/day for top 3 categories.
    """
    trend = {
        "Social":        [1.8, 2.0, 2.1, 2.0, 2.2, 2.1],
        "Entertainment": [1.2, 1.5, 1.4, 1.3, 1.4, 1.4],
        "Health":        [0.4, 0.5, 0.5, 0.6, 0.6, 0.6],
    }
    return {"months": MONTHS, "series": trend}


def top_group_per_category(df: pd.DataFrame) -> dict:
    """Which age group has highest average engagement per category."""
    hour_cols = [c for c in df.columns if c.startswith("hours_")]
    result = {}
    for col, cat in zip(hour_cols, CATEGORIES):
        top = df.groupby("age_group")[col].mean().idxmax()
        result[cat] = top
    return result
# ── 4. Master pipeline ─────────────────────────────────────────────────────────
def run_pipeline() -> dict:
    """Run the full research pipeline and return all data as a dict."""
    raw    = generate_raw_data()
    df, cleaning_report = clean_data(raw)

    top_groups = top_group_per_category(df)
    cats       = category_totals(df)
    for c in cats:
        c["top_group"] = top_groups.get(c["category"], "—")

    return {
        "meta": {
            "total_points":  cleaning_report["clean_rows"],
            "raw_points":    cleaning_report["raw_rows"],
            "dropped_nulls": cleaning_report["dropped_nulls"],
            "capped_outliers": cleaning_report["capped_outliers"],
            "missing_pct":   cleaning_report["missing_pct_before"],
            "categories":    len(CATEGORIES),
            "age_groups":    len(AGE_GROUPS),
        },
        "category_totals":    cats,
        "by_age":             engagement_by_group(df, "age_group"),
        "by_gender":          engagement_by_group(df, "gender"),
        "by_region":          engagement_by_group(df, "region"),
        "overall_dist":       overall_distribution(df),
        "monthly_trend":      monthly_trend(),
        "summary_stats":      summary_stats(df),
        "cleaning_report":    cleaning_report,
    }


if __name__ == "__main__":
    data = run_pipeline()
    out = Path("data/pipeline_output.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, indent=2))
    print(f"Pipeline complete. {data['meta']['total_points']:,} clean records.")
    print(f"Cleaning: dropped {data['meta']['dropped_nulls']} nulls, "
          f"capped {data['meta']['capped_outliers']} outliers.")
