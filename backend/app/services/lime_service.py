"""
TrustLens AI — LIME Local Explainability Service

Provides per-row local explanations using lime.lime_tabular.
Returns feature contributions + fidelity score (R² of the local linear model).

Called on-demand when a user selects a specific row to explain.
"""

from __future__ import annotations

import warnings
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


def compute_lime_explanation(
    model: Any,
    X_train: pd.DataFrame,
    row: pd.DataFrame,
    feature_names: Optional[List[str]] = None,
    class_names: Optional[List[str]] = None,
    num_features: int = 10,
) -> Dict[str, Any]:
    """
    Compute a LIME local explanation for a single row.

    Args:
        model:         Trained classifier with predict_proba
        X_train:       Training data (used to fit LIME's local sampler)
        row:           Single-row DataFrame to explain
        feature_names: Column names
        class_names:   E.g. ["Rejected", "Approved"]
        num_features:  Number of top features to return

    Returns:
        {
            "feature_contributions": {feature_name: contribution},
            "fidelity_score": float,     # R² of LIME's local linear model
            "prediction": int,
            "prediction_proba": [p_class_0, p_class_1],
            "intercept": float,
        }
    """
    from lime.lime_tabular import LimeTabularExplainer

    if feature_names is None:
        feature_names = list(X_train.columns) if isinstance(X_train, pd.DataFrame) else \
            [f"feature_{i}" for i in range(X_train.shape[1])]

    if class_names is None:
        class_names = ["Class_0", "Class_1"]

    # Convert to numpy for LIME
    X_train_np = X_train.values if isinstance(X_train, pd.DataFrame) else X_train
    row_np = row.values[0] if isinstance(row, pd.DataFrame) else row

    # Detect categorical columns (object dtype)
    categorical_features = []
    if isinstance(X_train, pd.DataFrame):
        for idx, col in enumerate(X_train.columns):
            if X_train[col].dtype == object:
                categorical_features.append(idx)

    # Create explainer
    explainer = LimeTabularExplainer(
        training_data=X_train_np.astype(float),
        feature_names=feature_names,
        class_names=class_names,
        mode="classification",
        discretize_continuous=True,
        random_state=42,
    )

    # Explain the single instance
    predict_fn = model.predict_proba if hasattr(model, "predict_proba") else model.predict
    explanation = explainer.explain_instance(
        data_row=row_np.astype(float),
        predict_fn=predict_fn,
        num_features=min(num_features, len(feature_names)),
        labels=(1,),  # explain positive class
    )

    # Extract contributions
    # explanation.as_list(label=1) returns [(feature_desc, weight), ...]
    raw_contributions = explanation.as_list(label=1)
    feature_contributions = {
        desc: round(float(weight), 6)
        for desc, weight in raw_contributions
    }

    # Fidelity score = R² of the local linear model
    fidelity_score = round(float(explanation.score), 6) if hasattr(explanation, 'score') else None

    # Prediction
    prediction = int(model.predict(row)[0]) if isinstance(row, pd.DataFrame) else \
        int(model.predict(row.reshape(1, -1))[0])

    # Prediction probabilities
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(row)[0] if isinstance(row, pd.DataFrame) else \
            model.predict_proba(row.reshape(1, -1))[0]
        prediction_proba = [round(float(p), 6) for p in proba]
    else:
        prediction_proba = None

    # Intercept
    intercept = round(float(explanation.intercept[1]), 6) \
        if hasattr(explanation, 'intercept') and 1 in explanation.intercept else None

    return {
        "feature_contributions": feature_contributions,
        "fidelity_score": fidelity_score,
        "prediction": prediction,
        "prediction_proba": prediction_proba,
        "intercept": intercept,
    }
