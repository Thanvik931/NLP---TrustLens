"""
TrustLens AI - Mitigation Strategies Service

Provides three mitigation approaches:
  1. Pre-processing:  Reweighing (sample weight adjustment)
  2. In-processing:   ExponentiatedGradient with DemographicParity (Fairlearn)
  3. Post-processing: ThresholdOptimizer (Fairlearn)

Each returns before/after fairness metric comparison.
"""

from __future__ import annotations

import warnings
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.base import clone

warnings.filterwarnings("ignore")


@dataclass
class MitigationResult:
    """Result of applying a single mitigation strategy."""
    strategy: str                          # reweighing | exponentiated_gradient | threshold_optimizer
    before_metrics: Dict[str, float]       # {metric_name: value}
    after_metrics: Dict[str, float]
    improvement: Dict[str, float]          # {metric_name: pct_change}
    success: bool
    message: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_basic_fairness(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive: np.ndarray,
) -> Dict[str, float]:
    """Quick fairness metrics for before/after comparison."""
    groups = np.unique(sensitive)
    if len(groups) < 2:
        return {"demographic_parity": 0, "disparate_impact": 1, "accuracy": float((y_true == y_pred).mean())}

    rates = {}
    tprs = {}
    for g in groups:
        mask = sensitive == g
        rates[g] = float(y_pred[mask].mean()) if mask.sum() > 0 else 0.0
        pos = y_true[mask] == 1
        tprs[g] = float(y_pred[mask][pos].mean()) if pos.sum() > 0 else 0.0

    sorted_rates = sorted(rates.values())
    dp = sorted_rates[-1] - sorted_rates[0]
    dir_val = sorted_rates[0] / sorted_rates[-1] if sorted_rates[-1] > 0 else 0.0

    sorted_tprs = sorted(tprs.values())
    eo_tpr = sorted_tprs[-1] - sorted_tprs[0]

    return {
        "demographic_parity": round(dp, 4),
        "disparate_impact": round(dir_val, 4),
        "equalized_odds_tpr": round(eo_tpr, 4),
        "accuracy": round(float((y_true == y_pred).mean()), 4),
    }


def _pct_change(before: float, after: float) -> float:
    """Compute percentage improvement (lower DP/EO = better, higher DIR = better)."""
    if before == 0:
        return 0.0
    return round(((after - before) / abs(before)) * 100, 2)


# ---------------------------------------------------------------------------
# 1. Reweighing (Pre-processing)
# ---------------------------------------------------------------------------

def apply_reweighing(
    model: Any,
    X_train: pd.DataFrame,
    y_train: np.ndarray,
    X_test: pd.DataFrame,
    y_test: np.ndarray,
    sensitive_col: str,
) -> MitigationResult:
    """
    Reweighing: Compute sample weights to equalize positive outcome rates
    across groups, then retrain the model.
    """
    try:
        sensitive_train = X_train[sensitive_col].values
        sensitive_test = X_test[sensitive_col].values

        # Before metrics
        y_pred_before = model.predict(X_test.drop(columns=[sensitive_col], errors='ignore'))
        before = _compute_basic_fairness(y_test, y_pred_before, sensitive_test)

        # Compute reweighing sample weights
        groups = np.unique(sensitive_train)
        n = len(y_train)
        weights = np.ones(n)

        for g in groups:
            g_mask = sensitive_train == g
            for label in [0, 1]:
                l_mask = y_train == label
                gl_mask = g_mask & l_mask

                expected = g_mask.sum() * l_mask.sum() / n
                observed = gl_mask.sum()

                if observed > 0:
                    weights[gl_mask] = expected / observed

        # Retrain with weights
        new_model = clone(model)
        X_train_features = X_train.drop(columns=[sensitive_col], errors='ignore')
        X_test_features = X_test.drop(columns=[sensitive_col], errors='ignore')
        new_model.fit(X_train_features, y_train, sample_weight=weights)

        # After metrics
        y_pred_after = new_model.predict(X_test_features)
        after = _compute_basic_fairness(y_test, y_pred_after, sensitive_test)

        improvement = {
            "demographic_parity": _pct_change(before["demographic_parity"], after["demographic_parity"]),
            "disparate_impact": _pct_change(before["disparate_impact"], after["disparate_impact"]),
            "equalized_odds_tpr": _pct_change(before["equalized_odds_tpr"], after["equalized_odds_tpr"]),
            "accuracy": _pct_change(before["accuracy"], after["accuracy"]),
        }

        return MitigationResult(
            strategy="reweighing",
            before_metrics=before,
            after_metrics=after,
            improvement=improvement,
            success=True,
            message="Reweighing applied successfully",
        )

    except Exception as exc:
        return MitigationResult(
            strategy="reweighing",
            before_metrics={},
            after_metrics={},
            improvement={},
            success=False,
            message=f"Reweighing failed: {str(exc)}",
        )


# ---------------------------------------------------------------------------
# 2. ExponentiatedGradient (In-processing)
# ---------------------------------------------------------------------------

def apply_exponentiated_gradient(
    model: Any,
    X_train: pd.DataFrame,
    y_train: np.ndarray,
    X_test: pd.DataFrame,
    y_test: np.ndarray,
    sensitive_col: str,
) -> MitigationResult:
    """
    Fairlearn ExponentiatedGradient with DemographicParity constraint.
    Trains a new fair classifier.
    """
    try:
        from fairlearn.reductions import ExponentiatedGradient, DemographicParity

        sensitive_train = X_train[sensitive_col].values
        sensitive_test = X_test[sensitive_col].values
        X_train_feat = X_train.drop(columns=[sensitive_col], errors='ignore')
        X_test_feat = X_test.drop(columns=[sensitive_col], errors='ignore')

        # Before
        y_pred_before = model.predict(X_test_feat)
        before = _compute_basic_fairness(y_test, y_pred_before, sensitive_test)

        # Fair model
        fair_model = ExponentiatedGradient(
            estimator=clone(model),
            constraints=DemographicParity(),
            max_iter=50,
        )
        fair_model.fit(X_train_feat, y_train, sensitive_features=sensitive_train)

        # After
        y_pred_after = fair_model.predict(X_test_feat)
        after = _compute_basic_fairness(y_test, y_pred_after, sensitive_test)

        improvement = {
            "demographic_parity": _pct_change(before["demographic_parity"], after["demographic_parity"]),
            "disparate_impact": _pct_change(before["disparate_impact"], after["disparate_impact"]),
            "equalized_odds_tpr": _pct_change(before["equalized_odds_tpr"], after["equalized_odds_tpr"]),
            "accuracy": _pct_change(before["accuracy"], after["accuracy"]),
        }

        return MitigationResult(
            strategy="exponentiated_gradient",
            before_metrics=before,
            after_metrics=after,
            improvement=improvement,
            success=True,
            message="ExponentiatedGradient with DemographicParity applied",
        )

    except Exception as exc:
        return MitigationResult(
            strategy="exponentiated_gradient",
            before_metrics={},
            after_metrics={},
            improvement={},
            success=False,
            message=f"ExponentiatedGradient failed: {str(exc)}",
        )


# ---------------------------------------------------------------------------
# 3. ThresholdOptimizer (Post-processing)
# ---------------------------------------------------------------------------

def apply_threshold_optimizer(
    model: Any,
    X_train: pd.DataFrame,
    y_train: np.ndarray,
    X_test: pd.DataFrame,
    y_test: np.ndarray,
    sensitive_col: str,
) -> MitigationResult:
    """
    Fairlearn ThresholdOptimizer: adjusts classification thresholds
    per group to satisfy DemographicParity.
    """
    try:
        from fairlearn.postprocessing import ThresholdOptimizer

        sensitive_train = X_train[sensitive_col].values
        sensitive_test = X_test[sensitive_col].values
        X_train_feat = X_train.drop(columns=[sensitive_col], errors='ignore')
        X_test_feat = X_test.drop(columns=[sensitive_col], errors='ignore')

        # Before
        y_pred_before = model.predict(X_test_feat)
        before = _compute_basic_fairness(y_test, y_pred_before, sensitive_test)

        # Fit threshold optimizer
        postprocess_model = ThresholdOptimizer(
            estimator=model,
            constraints="demographic_parity",
            prefit=True,
        )
        postprocess_model.fit(X_train_feat, y_train, sensitive_features=sensitive_train)

        # After
        y_pred_after = postprocess_model.predict(X_test_feat, sensitive_features=sensitive_test)
        after = _compute_basic_fairness(y_test, y_pred_after, sensitive_test)

        improvement = {
            "demographic_parity": _pct_change(before["demographic_parity"], after["demographic_parity"]),
            "disparate_impact": _pct_change(before["disparate_impact"], after["disparate_impact"]),
            "equalized_odds_tpr": _pct_change(before["equalized_odds_tpr"], after["equalized_odds_tpr"]),
            "accuracy": _pct_change(before["accuracy"], after["accuracy"]),
        }

        return MitigationResult(
            strategy="threshold_optimizer",
            before_metrics=before,
            after_metrics=after,
            improvement=improvement,
            success=True,
            message="ThresholdOptimizer with DemographicParity applied",
        )

    except Exception as exc:
        return MitigationResult(
            strategy="threshold_optimizer",
            before_metrics={},
            after_metrics={},
            improvement={},
            success=False,
            message=f"ThresholdOptimizer failed: {str(exc)}",
        )
