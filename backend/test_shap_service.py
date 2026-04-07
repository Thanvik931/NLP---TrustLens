"""
test_shap_service.py
====================
Standalone test for the TrustLens SHAP explainability service.
Run with:  .venv\Scripts\python test_shap_service.py

Trains a RandomForest on synthetic data, then verifies:
  1. Global SHAP: feature_scores dict with all columns present
  2. Local SHAP:  per-feature scores + base_value + prediction for 1 row
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from app.services.explainability import compute_global_shap, compute_local_shap

DIVIDER = "=" * 60


def main():
    print(f"\n{DIVIDER}")
    print("  TrustLens AI — SHAP Explainability Test")
    print(DIVIDER)

    # ── Build synthetic data + train model ─────────────────────────────────
    rng = np.random.default_rng(42)
    n = 300
    df = pd.DataFrame({
        "age":           rng.integers(18, 70, n),
        "education_num": rng.integers(1, 16, n),
        "hours_per_week": rng.integers(20, 60, n),
        "capital_gain":  rng.integers(0, 10000, n),
        "sex_Male":      rng.choice([0, 1], n),
    })
    y = ((df["education_num"] > 10) & (df["hours_per_week"] > 35)).astype(int)

    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(df, y)

    feature_names = list(df.columns)

    # ── Test 1: Global SHAP ────────────────────────────────────────────────
    print("\n  1. Computing Global SHAP...")
    global_result = compute_global_shap(model, df, feature_names)

    print(f"     Method: {global_result['method']}")
    print(f"     Features ranked by importance:")
    for rank, name in enumerate(global_result["feature_names"], 1):
        score = global_result["feature_scores"][name]
        bar = "█" * int(score * 100)
        print(f"       {rank}. {name:<20} {score:.6f}  {bar}")

    assert "feature_scores" in global_result, "Missing feature_scores"
    assert len(global_result["feature_scores"]) == len(feature_names), \
        f"Expected {len(feature_names)} features, got {len(global_result['feature_scores'])}"
    assert global_result["method"] == "TreeExplainer", \
        f"Expected TreeExplainer for RandomForest, got {global_result['method']}"
    print("     ✅ Global SHAP passed — all columns present")

    # ── Test 2: Local SHAP (row 0) ────────────────────────────────────────
    print("\n  2. Computing Local SHAP (row 0)...")
    local_result = compute_local_shap(model, df, row_index=0, feature_names=feature_names)

    print(f"     Method     : {local_result['method']}")
    print(f"     Base value  : {local_result['base_value']:.6f}")
    print(f"     Prediction  : {local_result['prediction']}")
    print(f"     Feature contributions:")
    for name, val in sorted(local_result["feature_scores"].items(),
                            key=lambda x: abs(x[1]), reverse=True):
        direction = "+" if val > 0 else ""
        print(f"       {name:<20} {direction}{val:.6f}")

    assert "feature_scores" in local_result, "Missing feature_scores"
    assert len(local_result["feature_scores"]) == len(feature_names), \
        f"Expected {len(feature_names)} features"
    assert "base_value" in local_result, "Missing base_value"
    assert "prediction" in local_result, "Missing prediction"
    assert local_result["prediction"] in (0, 1), \
        f"Unexpected prediction: {local_result['prediction']}"
    print("     ✅ Local SHAP passed — all fields present")

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n{DIVIDER}")
    print("  ALL ASSERTIONS PASSED — Task 5 complete ✅")
    print(DIVIDER + "\n")


if __name__ == "__main__":
    main()
