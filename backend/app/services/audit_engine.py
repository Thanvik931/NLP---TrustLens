"""
TrustLens AI — Core Bias Detection Engine

Computes 4 fairness metrics:
  1. Demographic Parity Difference   (DP)
  2. Equalized Odds TPR gap          (EO_TPR)
  3. Equalized Odds FPR gap          (EO_FPR)
  4. Disparate Impact Ratio          (DIR)
  5. Subgroup Divergence             (max accuracy gap across subgroups)

Status logic:
  BLOCKED  — DIR < 0.6 OR any critical uncorrected bias OR safety rule fails
  FLAGGED  — DIR < 0.8 OR EO_diff > 0.1 OR any high bias flag
  PASSED   — everything within thresholds

All metrics computed with numpy/pandas — no heavy framework dependencies.
Uses sklearn only for AUROC / accuracy.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------------
# Thresholds (match governance rules in seed data)
# ---------------------------------------------------------------------------

DIR_BLOCKED_THRESHOLD = 0.6      # DIR below this → BLOCKED
DIR_FLAGGED_THRESHOLD = 0.8      # DIR below this → FLAGGED
EO_DIFF_FLAGGED_THRESHOLD = 0.1  # |EO gap| above this → FLAGGED
MIN_GROUP_SIZE = 30              # groups smaller than this are unreliable


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class GroupMetrics:
    """Metrics for a single demographic group value."""
    group_value: str
    n: int
    positive_rate: float         # P(Y_hat=1 | group)
    tpr: Optional[float]         # True Positive Rate (recall)  — None if no positives
    fpr: Optional[float]         # False Positive Rate           — None if no negatives
    accuracy: float


@dataclass
class FairnessResult:
    """
    Full fairness audit result for ONE sensitive attribute.
    e.g. sensitive_col="sex", privileged_group="Male"
    """
    sensitive_col: str
    privileged_group: str         # group with highest positive rate
    unprivileged_group: str       # group with lowest positive rate

    # Core metrics
    demographic_parity: float     # rate_privileged - rate_unprivileged
    equalized_odds_tpr: float     # TPR_privileged  - TPR_unprivileged
    equalized_odds_fpr: float     # FPR_privileged  - FPR_unprivileged
    disparate_impact: float       # rate_unprivileged / rate_privileged  (≥0.8 = compliant)
    subgroup_divergence: float    # max accuracy gap across ALL groups

    # Per-group breakdown
    group_metrics: List[GroupMetrics] = field(default_factory=list)

    # Derived
    dir_compliant: bool = False    # DIR >= 0.8
    eo_compliant: bool = False     # |EO gap| <= 0.1
    dp_compliant: bool = False     # |DP| <= 0.1


@dataclass
class AuditEngineResult:
    """Top-level result returned by run_bias_audit()."""
    # Overall model performance
    overall_accuracy: float
    overall_auroc: Optional[float]

    # Per-attribute fairness results
    fairness: List[FairnessResult]

    # Worst-case values across all sensitive attributes
    min_disparate_impact: float
    max_demographic_parity: float
    max_equalized_odds_tpr: float
    max_equalized_odds_fpr: float
    max_subgroup_divergence: float

    # Final audit status
    status: str                   # PASSED | FLAGGED | BLOCKED
    status_reasons: List[str]     # human-readable reasons for the status

    # Bias flags to persist in DB
    bias_flags: List[Dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core fairness computation
# ---------------------------------------------------------------------------

def _safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Division that returns `default` instead of ZeroDivisionError."""
    return numerator / denominator if denominator != 0 else default


def _compute_group_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    mask: np.ndarray,
    group_value: str,
) -> GroupMetrics:
    """Compute metrics for a single group subset."""
    n = int(mask.sum())
    if n == 0:
        return GroupMetrics(group_value, 0, 0.0, None, None, 0.0)

    yt = y_true[mask]
    yp = y_pred[mask]

    positive_rate = float(yp.mean())
    accuracy = float((yt == yp).mean())

    # TPR — only meaningful if there are actual positives
    actual_pos = yt == 1
    tpr = float(yp[actual_pos].mean()) if actual_pos.sum() > 0 else None

    # FPR — only meaningful if there are actual negatives
    actual_neg = yt == 0
    fpr = float(yp[actual_neg].mean()) if actual_neg.sum() > 0 else None

    return GroupMetrics(
        group_value=group_value,
        n=n,
        positive_rate=positive_rate,
        tpr=tpr,
        fpr=fpr,
        accuracy=accuracy,
    )


def _fairness_for_attribute(
    df: pd.DataFrame,
    y_true_col: str,
    y_pred_col: str,
    sensitive_col: str,
) -> FairnessResult:
    """
    Compute all fairness metrics for one sensitive attribute column.
    Identifies privileged = group with HIGHEST positive rate.
    """
    y_true = df[y_true_col].values.astype(int)
    y_pred = df[y_pred_col].values.astype(int)
    groups = df[sensitive_col].astype(str)

    group_values = groups.unique()
    group_met: List[GroupMetrics] = []

    for val in group_values:
        mask = (groups == val).values
        gm = _compute_group_metrics(y_true, y_pred, mask, val)
        group_met.append(gm)

    # Warn if any group < MIN_GROUP_SIZE
    small = [g for g in group_met if g.n < MIN_GROUP_SIZE]
    if small:
        small_names = [f"{g.group_value} (n={g.n})" for g in small]
        print(f"  ⚠️  Small groups in '{sensitive_col}': {small_names} — metrics may be unreliable")

    # Identify privileged / unprivileged by positive_rate
    sorted_groups = sorted(group_met, key=lambda g: g.positive_rate, reverse=True)
    priv  = sorted_groups[0]
    unpriv = sorted_groups[-1]

    # Demographic Parity Difference
    dp = priv.positive_rate - unpriv.positive_rate

    # Disparate Impact Ratio  [0..∞, 1=perfect, ≥0.8 okay]
    dir_val = _safe_divide(unpriv.positive_rate, priv.positive_rate, default=0.0)

    # Equalized Odds gaps — use 0 when group has no positives/negatives
    tpr_priv  = priv.tpr  if priv.tpr  is not None else 0.0
    tpr_unpriv = unpriv.tpr if unpriv.tpr is not None else 0.0
    fpr_priv  = priv.fpr  if priv.fpr  is not None else 0.0
    fpr_unpriv = unpriv.fpr if unpriv.fpr is not None else 0.0

    eo_tpr = tpr_priv - tpr_unpriv
    eo_fpr = fpr_priv - fpr_unpriv

    # Subgroup divergence: max accuracy gap across ALL groups
    accuracies = [g.accuracy for g in group_met]
    subgroup_div = max(accuracies) - min(accuracies) if len(accuracies) > 1 else 0.0

    return FairnessResult(
        sensitive_col=sensitive_col,
        privileged_group=priv.group_value,
        unprivileged_group=unpriv.group_value,
        demographic_parity=round(dp, 4),
        equalized_odds_tpr=round(eo_tpr, 4),
        equalized_odds_fpr=round(eo_fpr, 4),
        disparate_impact=round(dir_val, 4),
        subgroup_divergence=round(subgroup_div, 4),
        group_metrics=group_met,
        dir_compliant=dir_val >= DIR_FLAGGED_THRESHOLD,
        eo_compliant=abs(eo_tpr) <= EO_DIFF_FLAGGED_THRESHOLD,
        dp_compliant=abs(dp) <= 0.1,
    )


# ---------------------------------------------------------------------------
# Status logic
# ---------------------------------------------------------------------------

def _determine_status(
    min_dir: float,
    max_eo_tpr: float,
    bias_flags: List[Dict],
) -> tuple[str, List[str]]:
    """
    Return (status, [reasons]).
    BLOCKED > FLAGGED > PASSED — most severe wins.
    """
    reasons: List[str] = []
    status = "PASSED"

    # FLAGGED conditions
    if min_dir < DIR_FLAGGED_THRESHOLD:
        status = "FLAGGED"
        reasons.append(
            f"Disparate Impact {min_dir:.3f} below threshold {DIR_FLAGGED_THRESHOLD} "
            f"(80/20 rule violation)"
        )

    if abs(max_eo_tpr) > EO_DIFF_FLAGGED_THRESHOLD:
        status = "FLAGGED"
        reasons.append(
            f"Equalized Odds TPR gap {abs(max_eo_tpr):.3f} exceeds threshold "
            f"{EO_DIFF_FLAGGED_THRESHOLD}"
        )

    critical_flags = [f for f in bias_flags if f.get("severity") == "critical"]
    high_flags     = [f for f in bias_flags if f.get("severity") == "high"]

    if high_flags and status == "PASSED":
        status = "FLAGGED"
        reasons.append(f"{len(high_flags)} high-severity bias flag(s) detected")

    # BLOCKED conditions (override FLAGGED)
    if min_dir < DIR_BLOCKED_THRESHOLD:
        status = "BLOCKED"
        reasons.append(
            f"Disparate Impact {min_dir:.3f} critically below {DIR_BLOCKED_THRESHOLD} "
            f"— model BLOCKED from deployment"
        )

    if critical_flags:
        status = "BLOCKED"
        reasons.append(
            f"{len(critical_flags)} critical bias flag(s) — model BLOCKED"
        )

    if not reasons:
        reasons.append("All fairness metrics within acceptable thresholds")

    return status, reasons


# ---------------------------------------------------------------------------
# Bias flag builder
# ---------------------------------------------------------------------------

def _build_bias_flags(fairness_results: List[FairnessResult]) -> List[Dict]:
    """
    Convert fairness results into BiasFlag dicts ready for DB insertion.
    """
    flags: List[Dict] = []

    for fr in fairness_results:
        # DIR flag
        if fr.disparate_impact < DIR_FLAGGED_THRESHOLD:
            severity = "critical" if fr.disparate_impact < DIR_BLOCKED_THRESHOLD else "high"
            flags.append({
                "bias_type": "demographic",
                "affected_group": fr.unprivileged_group,
                "severity": severity,
                "metric_name": "disparate_impact",
                "metric_value": fr.disparate_impact,
                "threshold": DIR_FLAGGED_THRESHOLD,
                "description": (
                    f"Disparate Impact {fr.disparate_impact:.3f} for group "
                    f"'{fr.unprivileged_group}' vs '{fr.privileged_group}' "
                    f"in column '{fr.sensitive_col}'"
                ),
                "mitigation_applied": False,
            })

        # EO TPR flag
        if abs(fr.equalized_odds_tpr) > EO_DIFF_FLAGGED_THRESHOLD:
            severity = "high" if abs(fr.equalized_odds_tpr) > 0.15 else "medium"
            flags.append({
                "bias_type": "demographic",
                "affected_group": fr.unprivileged_group,
                "severity": severity,
                "metric_name": "equalized_odds_tpr",
                "metric_value": fr.equalized_odds_tpr,
                "threshold": EO_DIFF_FLAGGED_THRESHOLD,
                "description": (
                    f"TPR gap {fr.equalized_odds_tpr:.3f} between "
                    f"'{fr.privileged_group}' and '{fr.unprivileged_group}' "
                    f"in '{fr.sensitive_col}'"
                ),
                "mitigation_applied": False,
            })

        # DP flag
        if abs(fr.demographic_parity) > 0.1:
            severity = "medium" if abs(fr.demographic_parity) < 0.2 else "high"
            flags.append({
                "bias_type": "demographic",
                "affected_group": fr.unprivileged_group,
                "severity": severity,
                "metric_name": "demographic_parity",
                "metric_value": fr.demographic_parity,
                "threshold": 0.1,
                "description": (
                    f"Demographic Parity difference {fr.demographic_parity:.3f} "
                    f"in column '{fr.sensitive_col}'"
                ),
                "mitigation_applied": False,
            })

    return flags


# ---------------------------------------------------------------------------
# AUROC helper (sklearn optional)
# ---------------------------------------------------------------------------

def _compute_auroc(y_true: np.ndarray, y_score: np.ndarray) -> Optional[float]:
    try:
        from sklearn.metrics import roc_auc_score
        if len(np.unique(y_true)) < 2:
            return None
        return float(roc_auc_score(y_true, y_score))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_bias_audit(
    df: pd.DataFrame,
    y_true_col: str,
    y_pred_col: str,
    sensitive_cols: List[str],
    y_score_col: Optional[str] = None,   # probability scores for AUROC
) -> AuditEngineResult:
    """
    Run the full bias audit on a DataFrame that already contains:
      - Ground-truth labels in `y_true_col`
      - Model predictions (0/1) in `y_pred_col`
      - Optional prediction probabilities in `y_score_col`
      - Sensitive attribute columns listed in `sensitive_cols`

    Returns an AuditEngineResult with metrics, status, and bias flags.
    """
    if y_true_col not in df.columns:
        raise ValueError(f"Target column '{y_true_col}' not found in DataFrame")
    if y_pred_col not in df.columns:
        raise ValueError(f"Prediction column '{y_pred_col}' not found in DataFrame")

    y_true = df[y_true_col].values.astype(int)
    y_pred = df[y_pred_col].values.astype(int)

    # Overall accuracy
    overall_accuracy = float((y_true == y_pred).mean())

    # AUROC (only if score column provided)
    overall_auroc = None
    if y_score_col and y_score_col in df.columns:
        y_score = df[y_score_col].values.astype(float)
        overall_auroc = _compute_auroc(y_true, y_score)

    # Fairness per sensitive attribute
    fairness_results: List[FairnessResult] = []
    for col in sensitive_cols:
        if col not in df.columns:
            print(f"  ⚠️  Sensitive column '{col}' not in DataFrame — skipping")
            continue
        fr = _fairness_for_attribute(df, y_true_col, y_pred_col, col)
        fairness_results.append(fr)

    if not fairness_results:
        return AuditEngineResult(
            overall_accuracy=overall_accuracy,
            overall_auroc=overall_auroc,
            fairness=[],
            min_disparate_impact=1.0,
            max_demographic_parity=0.0,
            max_equalized_odds_tpr=0.0,
            max_equalized_odds_fpr=0.0,
            max_subgroup_divergence=0.0,
            status="PASSED",
            status_reasons=["No sensitive columns analysed"],
        )

    # Aggregate worst-case values
    min_dir    = min(fr.disparate_impact for fr in fairness_results)
    max_dp     = max(abs(fr.demographic_parity) for fr in fairness_results)
    max_eo_tpr = max(abs(fr.equalized_odds_tpr) for fr in fairness_results)
    max_eo_fpr = max(abs(fr.equalized_odds_fpr) for fr in fairness_results)
    max_subdiv = max(fr.subgroup_divergence for fr in fairness_results)

    # Build bias flags
    bias_flags = _build_bias_flags(fairness_results)

    # Determine final status
    status, reasons = _determine_status(min_dir, max_eo_tpr, bias_flags)

    return AuditEngineResult(
        overall_accuracy=round(overall_accuracy, 4),
        overall_auroc=round(overall_auroc, 4) if overall_auroc else None,
        fairness=fairness_results,
        min_disparate_impact=round(min_dir, 4),
        max_demographic_parity=round(max_dp, 4),
        max_equalized_odds_tpr=round(max_eo_tpr, 4),
        max_equalized_odds_fpr=round(max_eo_fpr, 4),
        max_subgroup_divergence=round(max_subdiv, 4),
        status=status,
        status_reasons=reasons,
        bias_flags=bias_flags,
    )
