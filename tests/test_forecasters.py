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

import pytest


def test_prophet_save_load_roundtrip(tmp_path):
    pytest.importorskip("prophet")
    from forecasters import ProphetForecaster

    s = make_series(40)
    m = ProphetForecaster(window_days=30).fit(s, None, 24)
    p1 = m.predict(s, 24)
    m.save(tmp_path / "m")
    p2 = ProphetForecaster.load(tmp_path / "m").predict(s, 24)
    assert len(p1) == 24 and np.allclose(p1, p2)

def test_lstm_shapes_and_roundtrip(tmp_path):
    pytest.importorskip("tensorflow")
    from forecasters import LSTMDirect, LSTMRecursive

    s = make_series(30)
    train, val = s.iloc[:-72], s.iloc[-72:]
    kw = dict(lookback=24, units_grid=[4], epochs=1, batch_size=32, patience=1, stride=1)

    d = LSTMDirect(**kw).fit(train, val, 6)
    p = d.predict(s, 6)
    d.save(tmp_path / "d")
    assert len(p) == 6 and np.allclose(p, LSTMDirect.load(tmp_path / "d").predict(s, 6))

    r = LSTMRecursive(**kw).fit(train, val, 6)
    assert len(r.predict(s, 6)) == 6