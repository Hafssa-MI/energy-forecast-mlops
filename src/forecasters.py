"""Modèles de prévision avec la MÊME interface :
   fit(train, val, horizon) / predict(history, horizon) / save(dossier) / load(dossier).
L'API utilise exactement les mêmes classes que l'entraînement."""
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd


class SeasonalNaive:
    """Baseline : la valeur de la même heure, la semaine précédente."""
    family = "baseline"

    def __init__(self, season=168, **_):
        self.season = season

    def fit(self, train, val, horizon):
        return self

    def predict(self, history, horizon):
        return np.resize(history.values[-self.season:], horizon)

    def save(self, d):
        Path(d).mkdir(parents=True, exist_ok=True)
        (Path(d) / "meta.json").write_text(json.dumps({"family": self.family, "season": self.season}))

    @classmethod
    def load(cls, d):
        m = json.loads((Path(d) / "meta.json").read_text())
        return cls(season=m["season"])

class SarimaForecaster:
    """SARIMA(p,d,q)(P,D,Q,24). Choix de l'ordre par AIC. Prévision sans refit :
    les paramètres appris sont appliqués à la fenêtre la plus récente (smooth)."""
    family = "sarima"

    def __init__(self, window_days=42, orders=((1, 0, 1),), seasonal=(1, 1, 1, 24), **_):
        self.window = int(window_days) * 24
        self.orders = [tuple(o) for o in orders]
        self.seasonal = tuple(seasonal)
        self.order = None
        self.params = None

    def _model(self, values, order):
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        return SARIMAX(values, order=order, seasonal_order=self.seasonal, trend="n",
                       enforce_stationarity=False, enforce_invertibility=False)

    def fit(self, train, val, horizon):
        y = train.values[-self.window:]
        best = None
        for order in self.orders:
            res = self._model(y, order).fit(disp=False, maxiter=50)
            print(f"  SARIMA{order}x{self.seasonal} AIC={res.aic:.1f}")
            if best is None or res.aic < best[0]:
                best = (res.aic, order, np.asarray(res.params))
        _, self.order, self.params = best
        print("  ordre retenu :", self.order)
        return self

    def predict(self, history, horizon):
        res = self._model(history.values[-self.window:], self.order).smooth(self.params)
        return np.asarray(res.forecast(horizon))

    def save(self, d):
        Path(d).mkdir(parents=True, exist_ok=True)
        (Path(d) / "meta.json").write_text(json.dumps({
            "family": self.family, "window": self.window, "order": list(self.order),
            "seasonal": list(self.seasonal), "params": self.params.tolist()}))

    @classmethod
    def load(cls, d):
        m = json.loads((Path(d) / "meta.json").read_text())
        o = cls(window_days=m["window"] // 24, orders=[m["order"]], seasonal=m["seasonal"])
        o.order, o.params = tuple(m["order"]), np.array(m["params"])
        return o

FAMILIES = {c.family: c for c in (SeasonalNaive,SarimaForecaster)}


def build_forecaster(family, cfg, params):
    if family == "baseline":
        return SeasonalNaive()
    if family == "sarima":
        return SarimaForecaster(**cfg["sarima"])
    raise ValueError(f"Famille inconnue pour l'instant : {family}")


def load_forecaster(directory):
    fam = json.loads((Path(directory) / "meta.json").read_text())["family"]
    return FAMILIES[fam].load(directory)