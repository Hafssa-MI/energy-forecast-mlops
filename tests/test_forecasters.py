import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from common import backtest  # noqa: E402
from forecasters import SeasonalNaive  # noqa: E402


def make_series(n_days=400):
    idx = pd.date_range("2018-01-01", periods=n_days * 24, freq="h")
    return pd.Series(50000 + 8000 * np.sin(2 * np.pi * idx.hour / 24), index=idx)


def test_baseline_is_perfect_on_periodic_series():
    s = make_series()
    res, _, _ = backtest(SeasonalNaive(), s, 60 * 24, 24, 24)
    assert res["mae"] < 1e-6