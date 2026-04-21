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
