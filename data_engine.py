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