"""LoanWise AI - model training.

Trains the five models from the spec, each as a scikit-learn Pipeline
(StandardScaler fitted on the TRAINING data only + classifier), on the
same 70/30 stratified split (random_state=42) for every model.
Called ONLY when the user clicks "Process Dataset & Train Models".
"""
import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from ml.preprocessing import FEATURE_COLUMNS, TARGET_COLUMN, encode_features


def build_models():
    """The five models, exactly as specified. Returns {name: pipeline}."""
    return {
        "Decision Tree": Pipeline([
            ("scaler", StandardScaler()),
            ("model", DecisionTreeClassifier(random_state=42)),
        ]),
        "Random Forest": Pipeline([
            ("scaler", StandardScaler()),
            ("model", RandomForestClassifier(n_estimators=100, random_state=42)),
        ]),
        "Naive Bayes": Pipeline([
            ("scaler", StandardScaler()),
            ("model", GaussianNB()),
        ]),
        "KNN": Pipeline([
            ("scaler", StandardScaler()),
            ("model", KNeighborsClassifier(n_neighbors=5)),
        ]),
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000, random_state=42)),
        ]),
    }


def train_all(df, model_dir):
    """Train all five models on an encoded dataframe.

    Returns (models, metrics, split_info, feature_importances, y_test, y_pred_best).
    metrics: {model_name: {accuracy, precision, recall, f1, confusion_matrix}}
    split_info: {"train": n, "test": n}
    feature_importances: {feature: importance} from the Random Forest
        (tree-based, so it has real importances - never hand-edited).
    """
    from ml.evaluation import evaluate

    encoded = encode_features(df)
    X = encoded[FEATURE_COLUMNS]
    y = encoded[TARGET_COLUMN]
    # 70% train / 30% test, stratified, random_state=42 (spec section 5H).
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )
    models = build_models()
    metrics = {}
    for name, pipe in models.items():
        pipe.fit(X_train, y_train)
        metrics[name] = evaluate(pipe, X_test, y_test)

    # Feature importance comes from the trained Random Forest itself.
    rf = models["Random Forest"].named_steps["model"]
    importances = {
        col: float(val) for col, val in zip(FEATURE_COLUMNS, rf.feature_importances_)
    }
    # Best model: highest accuracy, F1 as tie-breaker.
    best_name = max(metrics, key=lambda n: (metrics[n]["accuracy"], metrics[n]["f1"]))

    os.makedirs(model_dir, exist_ok=True)
    for name, pipe in models.items():
        safe = name.lower().replace(" ", "_")
        joblib.dump(pipe, os.path.join(model_dir, f"{safe}.joblib"))
    # Save the feature order with the models so prediction can never drift.
    joblib.dump(FEATURE_COLUMNS, os.path.join(model_dir, "feature_columns.joblib"))

    split_info = {"train": int(len(X_train)), "test": int(len(X_test))}
    return models, metrics, split_info, importances, best_name, y_test, metrics[best_name]["y_pred"]


def load_models(model_dir):
    """Load the five saved pipelines. Returns {name: pipeline} or None."""
    names = ["Decision Tree", "Random Forest", "Naive Bayes", "KNN", "Logistic Regression"]
    models = {}
    for name in names:
        path = os.path.join(model_dir, name.lower().replace(" ", "_") + ".joblib")
        if not os.path.exists(path):
            return None
        models[name] = joblib.load(path)
    return models
