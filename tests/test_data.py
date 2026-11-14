import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from common import calendar_features, error_metrics  # noqa: E402
from split import split_series  # noqa: E402


def make_series(n_days=400):
    idx = pd.date_range("2018-01-01", periods=n_days * 24, freq="h")
    return pd.Series(50000 + 8000 * np.sin(2 * np.pi * idx.hour / 24), index=idx)


def test_split_is_chronological_and_disjoint():
    s = make_series()
    p = split_series(s, 30, 60, 60)
    assert p["train"].index.max() < p["val"].index.min() < p["test"].index.min() < p["stream"].index.min()
    assert sum(len(v) for v in p.values()) == len(s)


def test_error_metrics():
    m = error_metrics(np.array([100.0, 200.0]), np.array([110.0, 180.0]))
    assert abs(m["mae"] - 15) < 1e-9


def test_calendar_features_shape_and_holiday():
    f = calendar_features(pd.date_range("2019-12-25", periods=24, freq="h"))
    assert f.shape == (24, 5) and f[:, 4].max() == 1.0