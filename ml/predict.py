"""
Loads the trained model and scores a single matchup. The Streamlit app
imports `predict_matchup` directly.

TODO: once features.py pulls in recruiting/advanced-stats columns, extend
the `features` dict shape here to match.
"""
import joblib
import pandas as pd

from train_model import MODEL_PATH

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_matchup(spread: float, over_under: float, week: int) -> float:
    """Returns home-team win probability as a float in [0, 1]."""
    model = _get_model()
    X = pd.DataFrame([{"spread": spread, "over_under": over_under, "week": week}])
    return float(model.predict_proba(X)[0, 1])
