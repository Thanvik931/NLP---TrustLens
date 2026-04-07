"""
TrustLens AI — SHAP Explainability Service

Provides:
  - Global feature importance (TreeExplainer for sklearn/XGBoost)
  - Local waterfall data for a single prediction
  - KernelExplainer fallback for custom models (max 100 row sample)

PERFORMANCE RULES:
  - TreeExplainer for sklearn / XGBoost / LightGBM: O(n) — fast
  - KernelExplainer: O(n_features^2) per sample — VERY slow, max 100 rows
  - Always run inside Celery task, NEVER block the HTTP request

Returns dicts ready to store in ExplainabilityResult.feature_scores JSON column.
"""

from __future__ import annotations

import warnings
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import shap

warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_tree_model(model: Any) -> bool:
    """Check if model supports TreeExplainer (sklearn trees, XGBoost, LightGBM)."""
    tree_types = []
    try:
        from sklearn.ensemble import (
            RandomForestClassifier,
            GradientBoostingClassifier,
            AdaBoostClassifier,
            ExtraTreesClassifier,
        )
        from sklearn.tree import DecisionTreeClassifier
        tree_types.extend([
            RandomForestClassifier,
            GradientBoostingClassifier,
            AdaBoostClassifier,
            ExtraTreesClassifier,
            DecisionTreeClassifier,
        ])
    except ImportError:
        pass

    try:
        import xgboost as xgb
        tree_types.append(xgb.XGBClassifier)
    except ImportError:
        pass

    try:
        import lightgbm as lgb
        tree_types.append(lgb.LGBMClassifier)
    except ImportError:
        pass

    return isinstance(model, tuple(tree_types)) if tree_types else False


def _get_feature_names(X: pd.DataFrame) -> List[str]:
    """Extract feature names from DataFrame or generate defaults."""
    if isinstance(X, pd.DataFrame):
        return list(X.columns)
    return [f"feature_{i}" for i in range(X.shape[1])]


def _extract_positive_class_shap(shap_values: Any) -> np.ndarray:
    """
    Normalize SHAP output to a 2D array (n_samples, n_features) for
    the positive class.

    SHAP versions return different shapes:
      Old: list of [array(n, f), array(n, f)]  — one per class
      New: array(n, f, 2)  — 3D with classes as last dim
      Single-output: array(n, f) — already correct
    """
    if isinstance(shap_values, list):
        return np.array(shap_values[1])  # positive class

    arr = np.array(shap_values)
    if arr.ndim == 3:
        return arr[:, :, 1]  # last dim = classes, take positive
    return arr  # already 2D


# ---------------------------------------------------------------------------
# Global Explanation
# ---------------------------------------------------------------------------

def compute_global_shap(
    model: Any,
    X: pd.DataFrame,
    feature_names: Optional[List[str]] = None,
    max_samples: int = 500,
) -> Dict[str, Any]:
    """
    Compute global SHAP feature importance.

    Returns:
        {
            "feature_scores": {feature_name: mean_abs_shap_value},
            "feature_names": [sorted by importance, descending],
            "shap_values_sample": [[row0_shap...], [row1_shap...], ...],  # for beeswarm
            "method": "TreeExplainer" | "KernelExplainer"
        }
    """
    if feature_names is None:
        feature_names = _get_feature_names(X)

    # Sample for performance
    if len(X) > max_samples:
        X_sample = X.sample(max_samples, random_state=42)
    else:
        X_sample = X.copy()

    if _is_tree_model(model):
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_sample)
        method = "TreeExplainer"
    else:
        # KernelExplainer fallback — use small background sample
        bg_size = min(50, len(X_sample))
        background = shap.sample(X_sample, bg_size)
        predict_fn = model.predict_proba if hasattr(model, "predict_proba") else model.predict
        explainer = shap.KernelExplainer(predict_fn, background)
        kernel_samples = min(100, len(X_sample))
        X_kernel = X_sample.iloc[:kernel_samples]
        shap_values = explainer.shap_values(X_kernel)
        X_sample = X_kernel
        method = "KernelExplainer"

    # Normalize to 2D (n_samples, n_features) for positive class
    shap_values = _extract_positive_class_shap(shap_values)

    # Compute mean absolute SHAP per feature → global importance
    mean_abs = np.abs(shap_values).mean(axis=0)
    feature_scores = {
        name: round(float(np.float64(val)), 6)
        for name, val in zip(feature_names, mean_abs)
    }

    # Sort by importance descending
    sorted_names = sorted(feature_scores, key=feature_scores.get, reverse=True)

    return {
        "feature_scores": feature_scores,
        "feature_names": sorted_names,
        "shap_values_sample": shap_values.tolist() if hasattr(shap_values, 'tolist') else shap_values,
        "method": method,
    }


# ---------------------------------------------------------------------------
# Local Explanation (single prediction)
# ---------------------------------------------------------------------------

def compute_local_shap(
    model: Any,
    X: pd.DataFrame,
    row_index: int,
    feature_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Compute SHAP explanation for a single prediction (row_index).

    Returns:
        {
            "feature_scores": {feature_name: shap_value},
            "base_value": float,
            "prediction": int,
            "row_index": int,
            "method": "TreeExplainer" | "KernelExplainer"
        }
    """
    if feature_names is None:
        feature_names = _get_feature_names(X)

    if row_index < 0 or row_index >= len(X):
        raise ValueError(f"row_index {row_index} out of range [0, {len(X)})")

    row = X.iloc[[row_index]]

    if _is_tree_model(model):
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(row)
        base_value = explainer.expected_value
        method = "TreeExplainer"
    else:
        bg_size = min(50, len(X))
        background = shap.sample(X, bg_size)
        predict_fn = model.predict_proba if hasattr(model, "predict_proba") else model.predict
        explainer = shap.KernelExplainer(predict_fn, background)
        shap_values = explainer.shap_values(row)
        base_value = explainer.expected_value
        method = "KernelExplainer"

    # Normalize to 2D (n_samples, n_features) for positive class
    shap_values = _extract_positive_class_shap(shap_values)
    if isinstance(base_value, (list, np.ndarray)):
        base_value = float(base_value[1]) if len(base_value) > 1 else float(base_value[0])

    shap_row = shap_values[0]
    feature_scores = {
        name: round(float(np.float64(val)), 6)
        for name, val in zip(feature_names, shap_row)
    }

    prediction = int(model.predict(row)[0])

    return {
        "feature_scores": feature_scores,
        "base_value": round(float(base_value), 6),
        "prediction": prediction,
        "row_index": row_index,
        "method": method,
    }
