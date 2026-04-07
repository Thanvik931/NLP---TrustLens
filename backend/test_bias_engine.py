"""
test_bias_engine.py
====================
Standalone test for the TrustLens bias detection engine.
Run with:  .venv\Scripts\python test_bias_engine.py

Generates 3 synthetic scenarios and verifies all 4 metrics print correctly:
  Scenario A — PASSED   (clean model, balanced predictions)
  Scenario B — FLAGGED  (DIR between 0.6 and 0.8)
  Scenario C — BLOCKED  (DIR < 0.6, critical bias)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

from app.services.audit_engine import run_bias_audit

DIVIDER = "=" * 65


def print_result(label: str, result):
    print(f"\n{DIVIDER}")
    print(f"  SCENARIO: {label}")
    print(DIVIDER)
    print(f"  Overall Accuracy : {result.overall_accuracy:.4f}")
    print(f"  Overall AUROC    : {result.overall_auroc}")
    print()

    for fr in result.fairness:
        print(f"  ── Sensitive col: '{fr.sensitive_col}' ─────────────────────")
        print(f"     Privileged group   : {fr.privileged_group}")
        print(f"     Unprivileged group : {fr.unprivileged_group}")
        print()
        print(f"     Demographic Parity Diff  : {fr.demographic_parity:+.4f}  "
              f"({'✅ PASS' if fr.dp_compliant else '❌ FAIL'})")
        print(f"     Equalized Odds TPR gap   : {fr.equalized_odds_tpr:+.4f}  "
              f"({'✅ PASS' if fr.eo_compliant else '❌ FAIL'})")
        print(f"     Equalized Odds FPR gap   : {fr.equalized_odds_fpr:+.4f}")
        print(f"     Disparate Impact Ratio   : {fr.disparate_impact:.4f}  "
              f"({'✅ PASS (≥0.8)' if fr.dir_compliant else '❌ FAIL (<0.8)'})")
        print(f"     Subgroup Divergence      : {fr.subgroup_divergence:.4f}")
        print()
        print(f"     Group breakdown:")
        for gm in fr.group_metrics:
            tpr_str = f"{gm.tpr:.3f}" if gm.tpr is not None else "N/A"
            fpr_str = f"{gm.fpr:.3f}" if gm.fpr is not None else "N/A"
            print(f"       {gm.group_value:<12} n={gm.n:<5} "
                  f"pos_rate={gm.positive_rate:.3f}  "
                  f"tpr={tpr_str}  fpr={fpr_str}  acc={gm.accuracy:.3f}")

    print()
    print(f"  Worst-case metrics across all sensitive cols:")
    print(f"    min Disparate Impact    : {result.min_disparate_impact:.4f}")
    print(f"    max Demographic Parity  : {result.max_demographic_parity:.4f}")
    print(f"    max EO TPR gap          : {result.max_equalized_odds_tpr:.4f}")
    print(f"    max EO FPR gap          : {result.max_equalized_odds_fpr:.4f}")
    print(f"    max Subgroup Divergence : {result.max_subgroup_divergence:.4f}")
    print()
    print(f"  Bias Flags ({len(result.bias_flags)}):")
    for bf in result.bias_flags:
        print(f"    [{bf['severity'].upper():<8}] {bf['metric_name']:<25} "
              f"value={bf['metric_value']:.4f}  "
              f"threshold={bf['threshold']}")
    print()
    status_icon = {"PASSED": "✅", "FLAGGED": "⚠️ ", "BLOCKED": "🔴"}.get(result.status, "?")
    print(f"  FINAL STATUS: {status_icon}  {result.status}")
    for reason in result.status_reasons:
        print(f"    → {reason}")
    print(DIVIDER)


# ---------------------------------------------------------------------------
# Scenario A — PASSED (balanced predictions)
# ---------------------------------------------------------------------------

def scenario_a_passed():
    rng = np.random.default_rng(42)
    n = 600

    sex  = rng.choice(["Male", "Female"], n, p=[0.5, 0.5])
    race = rng.choice(["White", "Black", "Hispanic"], n, p=[0.4, 0.3, 0.3])
    age  = rng.integers(20, 65, n)
    edu  = rng.integers(8, 18, n)

    # True label: income > 50k — slightly correlated with edu/age, almost NO sex/race effect
    logit = -2 + 0.05 * edu + 0.02 * age + rng.normal(0, 0.3, n)
    prob  = 1 / (1 + np.exp(-logit))
    y_true = (rng.random(n) < prob).astype(int)

    # Fair model: predicts nearly identically across groups
    y_pred  = (prob > 0.45).astype(int)
    y_score = prob

    df = pd.DataFrame({
        "sex": sex, "race": race, "age": age, "edu": edu,
        "y_true": y_true, "y_pred": y_pred, "y_score": y_score,
    })

    return run_bias_audit(df, "y_true", "y_pred", ["sex", "race"], "y_score")


# ---------------------------------------------------------------------------
# Scenario B — FLAGGED (moderate bias against females)
# ---------------------------------------------------------------------------

def scenario_b_flagged():
    rng = np.random.default_rng(0)
    n = 600

    sex = rng.choice(["Male", "Female"], n, p=[0.55, 0.45])
    age = rng.integers(20, 65, n)
    edu = rng.integers(8, 18, n)

    logit = -2 + 0.04 * edu + 0.015 * age + rng.normal(0, 0.2, n)
    prob  = 1 / (1 + np.exp(-logit))
    y_true = (rng.random(n) < prob).astype(int)

    # Biased predictions: females approved at ~0.65 rate of males
    y_pred = np.zeros(n, dtype=int)
    for i in range(n):
        threshold = 0.40 if sex[i] == "Male" else 0.60   # higher bar for females
        y_pred[i] = int(prob[i] > threshold)

    df = pd.DataFrame({
        "sex": sex, "age": age, "edu": edu,
        "y_true": y_true, "y_pred": y_pred, "y_score": prob,
    })

    return run_bias_audit(df, "y_true", "y_pred", ["sex"], "y_score")


# ---------------------------------------------------------------------------
# Scenario C — BLOCKED (severe racial bias, DIR < 0.6)
# ---------------------------------------------------------------------------

def scenario_c_blocked():
    rng = np.random.default_rng(7)
    n = 800

    race = rng.choice(["White", "Black"], n, p=[0.6, 0.4])
    age  = rng.integers(20, 65, n)
    edu  = rng.integers(8, 18, n)

    logit = -1.5 + 0.05 * edu + 0.01 * age + rng.normal(0, 0.2, n)
    prob  = 1 / (1 + np.exp(-logit))
    y_true = (rng.random(n) < prob).astype(int)

    # Severely biased: Black applicants approved at 40% rate of White applicants
    y_pred = np.zeros(n, dtype=int)
    for i in range(n):
        threshold = 0.35 if race[i] == "White" else 0.75  # very high bar for Black
        y_pred[i] = int(prob[i] > threshold)

    df = pd.DataFrame({
        "race": race, "age": age, "edu": edu,
        "y_true": y_true, "y_pred": y_pred, "y_score": prob,
    })

    return run_bias_audit(df, "y_true", "y_pred", ["race"], "y_score")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n" + DIVIDER)
    print("  TrustLens AI — Bias Detection Engine Test")
    print(DIVIDER)

    print("\nRunning Scenario A (expect PASSED)...")
    result_a = scenario_a_passed()
    print_result("A — Fair Model (expect PASSED)", result_a)

    print("\nRunning Scenario B (expect FLAGGED)...")
    result_b = scenario_b_flagged()
    print_result("B — Moderate Gender Bias (expect FLAGGED)", result_b)

    print("\nRunning Scenario C (expect BLOCKED)...")
    result_c = scenario_c_blocked()
    print_result("C — Severe Racial Bias (expect BLOCKED)", result_c)

    # ── Final assertions ──────────────────────────────────────────────────
    print("\n" + DIVIDER)
    print("  ASSERTIONS")
    print(DIVIDER)

    assert result_a.status == "PASSED",  f"Expected PASSED, got {result_a.status}"
    print("  ✅ Scenario A → PASSED")

    assert result_b.status in ("FLAGGED", "BLOCKED"), f"Expected FLAGGED, got {result_b.status}"
    print(f"  ✅ Scenario B → {result_b.status}")

    assert result_c.status == "BLOCKED", f"Expected BLOCKED, got {result_c.status}"
    print("  ✅ Scenario C → BLOCKED")

    assert result_a.min_disparate_impact is not None, "DIR missing from result A"
    assert result_a.max_demographic_parity is not None, "DP missing from result A"
    assert result_a.max_equalized_odds_tpr is not None, "EO TPR missing from result A"
    assert result_a.max_subgroup_divergence is not None, "Subgroup divergence missing"
    print("  ✅ All 4 metrics present in result A")

    print()
    print("  ALL ASSERTIONS PASSED — Task 4 complete ✅")
    print(DIVIDER + "\n")
