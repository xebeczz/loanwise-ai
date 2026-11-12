"""LoanWise AI - model evaluation + charts.

All metrics are calculated from the actual test split - never hardcoded.
Charts are drawn with Matplotlib and saved as PNG files so the pages
work without any JavaScript chart library.
"""
import os

import matplotlib
matplotlib.use("Agg")  # no display needed on a server
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score)

# Stitch palette, so charts match the UI.
NAVY = "#14243A"
BLUE = "#315EAB"
TEAL = "#24B8A5"
GREY = "#718096"
LIGHT_BG = "#E4EDFC"
MODEL_COLOURS = {
    "Decision Tree": "#315EAB",
    "Random Forest": "#14243A",
    "Naive Bayes": "#24B8A5",
    "KNN": "#7C8BA6",
    "Logistic Regression": "#5B8DEF",
}


def evaluate(pipe, X_test, y_test):
    """Accuracy / precision / recall / F1 + confusion matrix for one model."""
    y_pred = pipe.predict(X_test)
    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "y_pred": [int(v) for v in y_pred],
    }


def _save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def accuracy_chart(metrics, path):
    """Bar chart: accuracy of all five models."""
    names = list(metrics)
    vals = [metrics[n]["accuracy"] * 100 for n in names]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    bars = ax.bar(names, vals, color=[MODEL_COLOURS[n] for n in names], width=0.55)
    ax.set_ylim(0, 105)
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("ML Model Accuracy Comparison", fontweight="bold", color=NAVY)
    ax.spines[["top", "right"]].set_visible(False)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 1.5, f"{v:.2f}%",
                ha="center", fontsize=9, fontweight="bold", color=NAVY)
    plt.xticks(rotation=12, ha="right")
    _save(fig, path)


def metric_chart(metrics, metric, path, title):
    names = list(metrics)
    vals = [metrics[n][metric] * 100 for n in names]
    fig, ax = plt.subplots(figsize=(8, 3.4))
    bars = ax.bar(names, vals, color=[MODEL_COLOURS[n] for n in names], width=0.55)
    ax.set_ylim(0, 105)
    ax.set_ylabel(f"{metric.capitalize()} (%)")
    ax.set_title(title, fontweight="bold", color=NAVY)
    ax.spines[["top", "right"]].set_visible(False)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 1.5, f"{v:.2f}%",
                ha="center", fontsize=9, fontweight="bold", color=NAVY)
    plt.xticks(rotation=12, ha="right")
    _save(fig, path)


def confusion_matrix_chart(cm, best_name, path):
    fig, ax = plt.subplots(figsize=(4.6, 4.0))
    arr = np.array(cm)
    im = ax.imshow(arr, cmap="Blues")
    ax.set_title(f"Confusion Matrix - {best_name}", fontweight="bold", color=NAVY)
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_xticks([0, 1], ["Rejected", "Approved"])
    ax.set_yticks([0, 1], ["Rejected", "Approved"])
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(arr[i, j]), ha="center", va="center",
                    fontsize=14, fontweight="bold",
                    color="white" if arr[i, j] > arr.max() / 2 else NAVY)
    fig.colorbar(im, ax=ax, shrink=0.8)
    _save(fig, path)


def feature_importance_chart(importances, labels, path):
    items = sorted(importances.items(), key=lambda kv: kv[1], reverse=True)
    names = [labels.get(k, k) for k, _ in items]
    vals = [v for _, v in items]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    bars = ax.barh(names[::-1], vals[::-1],
                   color=[TEAL if i == len(vals) - 1 else BLUE for i in range(len(vals))])
    ax.set_xlabel("Importance")
    ax.set_title("Feature Importance (Random Forest)", fontweight="bold", color=NAVY)
    ax.spines[["top", "right"]].set_visible(False)
    for bar, v in zip(bars, vals[::-1]):
        ax.text(v + 0.01, bar.get_y() + bar.get_height() / 2, f"{v:.3f}",
                va="center", fontsize=9, color=NAVY)
    _save(fig, path)


def build_all_charts(metrics, best_name, importances, labels, chart_dir):
    """Generate every chart PNG the Performance page needs. Returns filenames."""
    os.makedirs(chart_dir, exist_ok=True)
    files = {}
    files["accuracy"] = "accuracy.png"
    accuracy_chart(metrics, os.path.join(chart_dir, "accuracy.png"))
    for metric, fname, title in [
        ("precision", "precision.png", "Precision Comparison"),
        ("recall", "recall.png", "Recall Comparison"),
        ("f1", "f1.png", "F1-Score Comparison"),
    ]:
        metric_chart(metrics, metric, os.path.join(chart_dir, fname), title)
        files[metric] = fname
    cm = metrics[best_name]["confusion_matrix"]
    confusion_matrix_chart(cm, best_name, os.path.join(chart_dir, "confusion_matrix.png"))
    files["confusion_matrix"] = "confusion_matrix.png"
    feature_importance_chart(importances, labels, os.path.join(chart_dir, "feature_importance.png"))
    files["feature_importance"] = "feature_importance.png"
    return files
