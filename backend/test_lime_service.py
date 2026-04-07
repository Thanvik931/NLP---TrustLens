"""
test_lime_service.py
====================
Standalone test for the TrustLens LIME explainability service.
Run with:  .venv\\Scripts\\python test_lime_service.py

Trains a RandomForest, then verifies:
  1. Feature contributions dict returned
  2. Fidelity score returned (R^2 of local linear model)
  3. Prediction and prediction_proba present
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from app.services.lime_service import compute_lime_explanation

DIVIDER = "=" * 60


def main():
    print(f"\n{DIVIDER}")
    print("  TrustLens AI - LIME Explainability Test")
    print(DIVIDER)

    # -- Build synthetic data + train model --
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

    # -- Test: LIME for row 0 --
    print("\n  Computing LIME explanation for row 0...")
    row = df.iloc[[0]]

    result = compute_lime_explanation(
        model=model,
        X_train=df,
        row=row,
        feature_names=feature_names,
        class_names=["Low Income", "High Income"],
        num_features=5,
    )

    print(f"  Prediction       : {result['prediction']}")
    print(f"  Prediction proba : {result['prediction_proba']}")
    print(f"  Fidelity score   : {result['fidelity_score']}")
    print(f"  Intercept        : {result['intercept']}")
    print(f"\n  Feature contributions ({len(result['feature_contributions'])}):")
    for feat, weight in sorted(result["feature_contributions"].items(),
                                key=lambda x: abs(x[1]), reverse=True):
        direction = "+" if weight > 0 else ""
        print(f"    {feat:<35} {direction}{weight:.6f}")

    # -- Assertions --
    print(f"\n{DIVIDER}")
    print("  ASSERTIONS")
    print(DIVIDER)

    assert "feature_contributions" in result, "Missing feature_contributions"
    assert len(result["feature_contributions"]) > 0, "Empty feature_contributions"
    print("  [OK] feature_contributions present and non-empty")

    assert "fidelity_score" in result, "Missing fidelity_score"
    assert result["fidelity_score"] is not None, "fidelity_score is None"
    assert 0 <= result["fidelity_score"] <= 1.1, \
        f"fidelity_score {result['fidelity_score']} out of expected range"
    print(f"  [OK] fidelity_score = {result['fidelity_score']}")

    assert "prediction" in result, "Missing prediction"
    assert result["prediction"] in (0, 1), f"Bad prediction: {result['prediction']}"
    print(f"  [OK] prediction = {result['prediction']}")

    assert "prediction_proba" in result, "Missing prediction_proba"
    assert len(result["prediction_proba"]) == 2, "Expected 2-class proba"
    print(f"  [OK] prediction_proba = {result['prediction_proba']}")

    print(f"\n  ALL ASSERTIONS PASSED - Task 6 complete! [OK]")
    print(DIVIDER + "\n")


if __name__ == "__main__":
    main()
