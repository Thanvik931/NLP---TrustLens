"""
Pydantic schemas for Dataset endpoints.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class DatasetOut(BaseModel):
    id: str
    name: str
    domain: str
    description: Optional[str]
    file_path: Optional[str]
    row_count: Optional[int]
    feature_count: Optional[int]
    sensitive_cols: Optional[List[str]]
    target_col: Optional[str]
    created_at: str

    model_config = {"from_attributes": True}


class CohortStat(BaseModel):
    column: str
    value: str
    count: int
    pct: float


class ColumnProfile(BaseModel):
    column: str
    dtype: str
    missing_count: int
    missing_pct: float
    unique_count: int
    top_values: Dict[str, int]         # {value: count} top 10


class DatasetProfile(BaseModel):
    dataset_id: str
    row_count: int
    feature_count: int
    columns: List[ColumnProfile]
    cohort_stats: List[CohortStat]     # per sensitive column group counts
    missing_heatmap: Dict[str, float]  # {column: missing_pct}
    correlation_matrix: Dict[str, Dict[str, float]]   # full corr matrix
    proxy_warnings: List[str]          # columns highly correlated with sensitive cols
