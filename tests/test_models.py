"""ML tests: the five pipelines, split, encoding and voting rule.

These run on a small synthetic frame built in the test - they check
the logic, not the real dataset. The real dataset numbers are verified
separately through the live app (see README / verification notes).
"""
import pandas as pd

from ml.preprocessing import (FEATURE_COLUMNS, applicant_to_features,
                              encode_features)
from ml.prediction import final_decision, predict_all
from ml.training import build_models, train_all


def _frame(n=120):
    rows = []
    for i in range(n):
        approved = i % 3 != 0
        rows.append({
            "loan_id": i + 1, "no_of_dependents": i % 3,
            "education": "Graduate" if i % 2 == 0 else "Not Graduate",
            "self_employed": "Yes" if i % 4 == 0 else "No",
            "income_annum": 900000 + i * 100000,
            "loan_amount": 500000 + i * 100000,
            "loan_term": 5 + (i % 10),
            "cibil_score": 750 if approved else 450,
            "residential_assets_value": 1000000 + i * 10000,
            "commercial_assets_value": 500000 + i * 5000,
            "luxury_assets_value": 800000 + i * 8000,
            "bank_asset_value": 600000 + i * 6000,
            "loan_status": "Approved" if approved else "Rejected",
        })
    return pd.DataFrame(rows)


def test_encoding_matches_spec():
    df = encode_features(_frame(6))
    assert set(df["education"].unique()) <= {0, 1}
    assert set(df["self_employed"].unique()) <= {0, 1}
    assert set(df["loan_status"].unique()) <= {0, 1}
    assert df.loc[0, "education"] == 1  # Graduate
    assert df.loc[1, "education"] == 0  # Not Graduate


def test_five_models_and_split(tmp_path):
    models, metrics, split, importances, best, _yt, _yp = train_all(
        _frame(), str(tmp_path / "models"))
    assert set(metrics) == {"Decision Tree", "Random Forest", "Naive Bayes",
                            "KNN", "Logistic Regression"}
    # 120 rows -> 70/30 split = 84 train / 36 test.
    assert split == {"train": 84, "test": 36}
    for name, m in metrics.items():
        for key in ("accuracy", "precision", "recall", "f1"):
            assert 0.0 <= m[key] <= 1.0, (name, key)
        assert len(m["confusion_matrix"]) == 2
    # Feature importances sum to 1 and cover all 11 features.
    assert len(importances) == 11
    assert abs(sum(importances.values()) - 1.0) < 1e-6
    assert best in metrics


def test_voting_rule():
    assert final_decision(5) == "APPROVED"
    assert final_decision(0) == "REJECTED"
    assert final_decision(3) == "FURTHER REVIEW"
    assert final_decision(1) == "FURTHER REVIEW"


def test_predict_all_returns_five_votes(tmp_path):
    models, _m, _s, _i, _b, _yt, _yp = train_all(_frame(), str(tmp_path / "models"))
    applicant = {
        "no_of_dependents": 0, "education": "Graduate", "self_employed": "Salaried",
        "income_annum": 4000000, "loan_amount": 11500000, "loan_term": 8,
        "cibil_score": 434, "residential_assets_value": 4500000,
        "commercial_assets_value": 2800000, "luxury_assets_value": 8400000,
        "bank_asset_value": 5900000,
    }
    result = predict_all(models, applicant)
    assert len(result["votes"]) == 5
    assert result["approval_votes"] + result["rejection_votes"] == 5
    assert result["final_decision"] == final_decision(result["approval_votes"])
    # Applicant row uses the same feature order as training.
    X = applicant_to_features(applicant)
    assert list(X.columns) == FEATURE_COLUMNS
