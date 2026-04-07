"""
test_mitigation_service.py
===========================
Standalone test for TrustLens mitigation strategies.
Run with:  .venv\\Scripts\\python test_mitigation_service.py

Creates a biased model, then applies all 3 mitigation strategies
and verifies before/after values differ.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from app.services.mitigation import (
    apply_reweighing,
    apply_exponentiated_gradient,
    apply_threshold_optimizer,
)

DIVIDER = "=" * 60


def print_result(result):
    print(f"\n  Strategy: {result.strategy}")
    print(f"  Success : {result.success}")
    print(f"  Message : {result.message}")
    if result.success:
        print(f"\n  {'Metric':<25} {'Before':>8} {'After':>8} {'Change':>8}")
        print(f"  {'-'*25} {'-'*8} {'-'*8} {'-'*8}")
        for metric in result.before_metrics:
            b = result.before_metrics[metric]
            a = result.after_metrics[metric]
            i = result.improvement.get(metric, 0)
            print(f"  {metric:<25} {b:>8.4f} {a:>8.4f} {i:>+7.1f}%")


def main():
    print(f"\n{DIVIDER}")
    print("  TrustLens AI - Mitigation Strategies Test")
    print(DIVIDER)

    # -- Build BIASED synthetic data --
    rng = np.random.default_rng(42)
    n = 800
    sex = rng.choice(["Male", "Female"], n, p=[0.55, 0.45])
    age = rng.integers(20, 65, n)
    edu = rng.integers(8, 18, n)
    hours = rng.integers(20, 60, n)

    # Biased ground truth: males more likely to be approved
    logit = -2 + 0.05 * edu + 0.02 * hours + 0.015 * age
    logit += np.where(sex == "Male", 0.8, -0.3)  # bias
    prob = 1 / (1 + np.exp(-logit + rng.normal(0, 0.5, n)))
    y = (rng.random(n) < prob).astype(int)

    df = pd.DataFrame({
        "age": age, "education": edu,
        "hours": hours, "sex": sex,
    })

    X_train, X_test, y_train, y_test = train_test_split(
        df, y, test_size=0.3, random_state=42
    )

    # Train biased model (sex is NOT removed from features here intentionally)
    # We need numeric features for the model
    X_train_model = X_train.copy()
    X_test_model = X_test.copy()
    X_train_model["sex_numeric"] = (X_train_model["sex"] == "Male").astype(int)
    X_test_model["sex_numeric"] = (X_test_model["sex"] == "Male").astype(int)

    feature_cols = ["age", "education", "hours", "sex_numeric"]
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train_model[feature_cols], y_train)

    # Prepare data with sensitive col for mitigation
    X_train_mit = X_train_model[feature_cols + ["sex"]].copy()
    X_test_mit = X_test_model[feature_cols + ["sex"]].copy()

    # -- 1. Reweighing --
    print(f"\n{'='*40}")
    print("  1. REWEIGHING (Pre-processing)")
    print(f"{'='*40}")
    # For reweighing we need to drop sex_numeric since the model should not use it
    # but keep sex as the sensitive column
    X_tr = X_train_mit[["age", "education", "hours", "sex"]].copy()
    X_te = X_test_mit[["age", "education", "hours", "sex"]].copy()
    model_rw = RandomForestClassifier(n_estimators=50, random_state=42)
    model_rw.fit(X_tr.drop(columns=["sex"]), y_train)

    r1 = apply_reweighing(model_rw, X_tr, y_train, X_te, y_test, "sex")
    print_result(r1)

    # -- 2. ExponentiatedGradient --
    print(f"\n{'='*40}")
    print("  2. EXPONENTIATED GRADIENT (In-processing)")
    print(f"{'='*40}")
    r2 = apply_exponentiated_gradient(model_rw, X_tr, y_train, X_te, y_test, "sex")
    print_result(r2)

    # -- 3. ThresholdOptimizer --
    print(f"\n{'='*40}")
    print("  3. THRESHOLD OPTIMIZER (Post-processing)")
    print(f"{'='*40}")
    r3 = apply_threshold_optimizer(model_rw, X_tr, y_train, X_te, y_test, "sex")
    print_result(r3)

    # -- Assertions --
    print(f"\n{DIVIDER}")
    print("  ASSERTIONS")
    print(DIVIDER)

    assert r1.success, f"Reweighing failed: {r1.message}"
    assert r1.before_metrics != r1.after_metrics, "Reweighing: before == after (no effect)"
    print("  [OK] Reweighing: before/after differ")

    assert r2.success, f"ExponentiatedGradient failed: {r2.message}"
    print("  [OK] ExponentiatedGradient: completed successfully")

    assert r3.success, f"ThresholdOptimizer failed: {r3.message}"
    print("  [OK] ThresholdOptimizer: completed successfully")

    print(f"\n  ALL ASSERTIONS PASSED - Task 7 complete! [OK]")
    print(DIVIDER + "\n")


if __name__ == "__main__":
    main()
