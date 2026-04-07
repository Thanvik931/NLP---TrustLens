"""
Data profiling service.

Given a CSV path + metadata, returns:
  - Per-column statistics (dtype, missing rate, top values)
  - Cohort size counts per sensitive group
  - Missing value heatmap
  - Correlation matrix
  - Proxy variable warnings (high correlation with sensitive cols)
"""

import os
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from app.schemas.dataset import CohortStat, ColumnProfile, DatasetProfile


# Threshold above which a numeric column is flagged as a proxy variable
PROXY_CORR_THRESHOLD = 0.7

# Maximum unique values for a column to be included in top_values
MAX_TOP_VALUES = 10


def profile_dataset(
    dataset_id: str,
    file_path: str,
    sensitive_cols: Optional[List[str]] = None,
    target_col: Optional[str] = None,
) -> DatasetProfile:
    """
    Load a CSV and compute a full profiling report.

    Returns a DatasetProfile with:
      - column-level stats
      - cohort size counts for every sensitive column
      - missing heatmap
      - correlation matrix (numeric columns only)
      - proxy variable warnings
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    df = pd.read_csv(file_path, low_memory=False)
    sensitive_cols = [c for c in (sensitive_cols or []) if c in df.columns]

    # ── 1. Per-column profiles ─────────────────────────────────────────────
    column_profiles: List[ColumnProfile] = []
    for col in df.columns:
        series = df[col]
        missing_count = int(series.isna().sum())
        missing_pct = round(missing_count / len(df) * 100, 2) if len(df) > 0 else 0.0

        # top values (only for non-float columns to keep payload small)
        if series.dtype == object or series.nunique() <= 50:
            top_raw = series.value_counts().head(MAX_TOP_VALUES)
            top_values = {str(k): int(v) for k, v in top_raw.items()}
        else:
            top_values = {}

        column_profiles.append(
            ColumnProfile(
                column=col,
                dtype=str(series.dtype),
                missing_count=missing_count,
                missing_pct=missing_pct,
                unique_count=int(series.nunique()),
                top_values=top_values,
            )
        )

    # ── 2. Cohort stats per sensitive column ───────────────────────────────
    cohort_stats: List[CohortStat] = []
    for col in sensitive_cols:
        counts = df[col].value_counts(dropna=False)
        total = len(df)
        for val, cnt in counts.items():
            cohort_stats.append(
                CohortStat(
                    column=col,
                    value=str(val),
                    count=int(cnt),
                    pct=round(int(cnt) / total * 100, 2) if total > 0 else 0.0,
                )
            )

    # ── 3. Missing value heatmap ───────────────────────────────────────────
    missing_heatmap: Dict[str, float] = {
        col: round(float(df[col].isna().mean() * 100), 2) for col in df.columns
    }

    # ── 4. Correlation matrix (numeric only) ──────────────────────────────
    numeric_df = df.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        corr = numeric_df.corr().round(4)
        corr = corr.fillna(0)
        correlation_matrix: Dict[str, Dict[str, float]] = {
            col: {c: float(v) for c, v in row.items()}
            for col, row in corr.to_dict().items()
        }
    else:
        correlation_matrix = {}

    # ── 5. Proxy variable warnings ────────────────────────────────────────
    proxy_warnings: List[str] = []
    numeric_sensitive = [c for c in sensitive_cols if c in numeric_df.columns]
    if numeric_sensitive and not numeric_df.empty:
        for sens_col in numeric_sensitive:
            for other_col in numeric_df.columns:
                if other_col == sens_col:
                    continue
                if other_col == target_col:
                    continue
                corr_val = abs(
                    numeric_df[sens_col].corr(numeric_df[other_col])
                )
                if corr_val >= PROXY_CORR_THRESHOLD:
                    proxy_warnings.append(
                        f"'{other_col}' is highly correlated with sensitive column "
                        f"'{sens_col}' (r={corr_val:.3f}) — possible proxy variable"
                    )

    return DatasetProfile(
        dataset_id=dataset_id,
        row_count=len(df),
        feature_count=len(df.columns),
        columns=column_profiles,
        cohort_stats=cohort_stats,
        missing_heatmap=missing_heatmap,
        correlation_matrix=correlation_matrix,
        proxy_warnings=proxy_warnings,
    )
