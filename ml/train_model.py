"""
Trains a win-probability classifier on fct_games and saves it to model.joblib.
Run after `dbt run` has refreshed the marts.

Usage: python ml/train_model.py
"""
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from xgboost import XGBClassifier

from features import build_training_set

MODEL_PATH = "model.joblib"


def main():
    X, y = build_training_set()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        eval_metric="logloss",
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    print(f"Accuracy: {accuracy_score(y_test, preds):.3f}")
    print(f"AUC:      {roc_auc_score(y_test, probs):.3f}")

    joblib.dump(model, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
