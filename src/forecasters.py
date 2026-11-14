"""Modèles de prévision avec la MÊME interface :
   fit(train, val, horizon) / predict(history, horizon) / save(dossier) / load(dossier).
L'API utilise exactement les mêmes classes que l'entraînement."""
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from common import calendar_features

logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
logging.getLogger("prophet").setLevel(logging.WARNING)


def _future_index(history, horizon):
    return history.index[-1] + pd.to_timedelta(np.arange(1, horizon + 1), unit="h")


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

class ProphetForecaster:
    """Prophet : tendance + saisonnalités + jours fériés. N'utilise que les dates futures."""
    family = "prophet"

    def __init__(self, window_days=None, country="DE", **_):
        self.window = int(window_days) * 24 if window_days else None
        self.country = country
        self.model = None

    def fit(self, train, val, horizon):
        from prophet import Prophet
        y = train.iloc[-self.window:] if self.window else train
        df = pd.DataFrame({"ds": y.index, "y": y.values})
        m = Prophet(daily_seasonality=True, weekly_seasonality=True,
                    yearly_seasonality=len(y) > 24 * 365 * 1.5)
        m.add_country_holidays(country_name=self.country)
        m.fit(df)
        self.model = m
        return self

    def predict(self, history, horizon):
        future = pd.DataFrame({"ds": _future_index(history, horizon)})
        return self.model.predict(future)["yhat"].values

    def save(self, d):
        from prophet.serialize import model_to_json
        Path(d).mkdir(parents=True, exist_ok=True)
        (Path(d) / "prophet.json").write_text(model_to_json(self.model))
        (Path(d) / "meta.json").write_text(json.dumps({"family": self.family, "country": self.country}))

    @classmethod
    def load(cls, d):
        from prophet.serialize import model_from_json
        o = cls(country=json.loads((Path(d) / "meta.json").read_text())["country"])
        o.model = model_from_json((Path(d) / "prophet.json").read_text())
        return o

class LSTMDirect:
    """LSTM stratégie DIRECTE : une seule passe produit les `horizon` valeurs d'un coup."""
    family = "lstm_direct"

    def __init__(self, lookback=168, units_grid=(32,), epochs=10, batch_size=256, patience=3,
                 stride=1, tz="Europe/Berlin", country="DE", **_):
        self.lookback, self.units_grid = int(lookback), list(units_grid)
        self.epochs, self.batch_size, self.patience = int(epochs), int(batch_size), int(patience)
        self.stride, self.tz, self.country = int(stride), tz, country
        self.mean = self.std = None
        self.horizon = None
        self.model = None

    def _features(self, index, values):
        z = ((np.asarray(values, "float32") - self.mean) / self.std)[:, None]
        return np.hstack([z, calendar_features(index, self.tz, self.country)])

    def _xy(self, series, horizon, start=0):
        F = self._features(series.index, series.values)
        L = self.lookback
        idx = np.arange(max(L - 1, start), len(F) - horizon, self.stride)
        X = np.stack([F[i - L + 1: i + 1] for i in idx]).astype("float32")
        Y = np.stack([F[i + 1: i + 1 + horizon, 0] for i in idx]).astype("float32")
        return X, Y

    def _build(self, units, horizon):
        import tensorflow as tf
        m = tf.keras.Sequential([
            tf.keras.layers.Input((self.lookback, 6)),
            tf.keras.layers.LSTM(units),
            tf.keras.layers.Dropout(0.1),
            tf.keras.layers.Dense(horizon),
        ])
        m.compile(optimizer="adam", loss="mse")
        return m

    def fit(self, train, val, horizon):
        import tensorflow as tf
        tf.keras.utils.set_random_seed(42)
        self.horizon = horizon
        self.mean, self.std = float(train.mean()), float(train.std())
        Xtr, Ytr = self._xy(train, horizon)
        both = pd.concat([train, val])
        Xva, Yva = self._xy(both, horizon, start=len(train) - 1)
        best = None
        for units in self.units_grid:
            m = self._build(units, horizon)
            h = m.fit(Xtr, Ytr, validation_data=(Xva, Yva), epochs=self.epochs,
                      batch_size=self.batch_size, verbose=2,
                      callbacks=[tf.keras.callbacks.EarlyStopping(
                          patience=self.patience, restore_best_weights=True)])
            v = min(h.history["val_loss"])
            print(f"  LSTM units={units} val_loss={v:.4f}")
            if best is None or v < best[0]:
                best = (v, m, units)
        self.val_loss, self.model, self.units = best
        return self

    def predict(self, history, horizon):
        assert horizon == self.horizon, f"Ce modèle prédit {self.horizon} h, pas {horizon} h"
        h = history.iloc[-self.lookback:]
        x = self._features(h.index, h.values)[None]
        y = self.model(x, training=False).numpy()[0]
        return y * self.std + self.mean

    def _meta(self):
        return {"family": self.family, "lookback": self.lookback, "mean": self.mean, "std": self.std,
                "horizon": self.horizon, "tz": self.tz, "country": self.country}

    def save(self, d):
        Path(d).mkdir(parents=True, exist_ok=True)
        self.model.save(Path(d) / "model.keras")
        (Path(d) / "meta.json").write_text(json.dumps(self._meta()))

    @classmethod
    def load(cls, d):
        import tensorflow as tf
        m = json.loads((Path(d) / "meta.json").read_text())
        o = cls(lookback=m["lookback"], tz=m["tz"], country=m["country"])
        o.mean, o.std, o.horizon = m["mean"], m["std"], m["horizon"]
        o.model = tf.keras.models.load_model(Path(d) / "model.keras")
        return o

class LSTMRecursive(LSTMDirect):
    """LSTM stratégie RÉCURSIVE : prédit 1 h, la réinjecte en entrée, et recommence `horizon` fois.
    Les erreurs peuvent donc s'accumuler. Le calendrier futur est connu à l'avance."""
    family = "lstm_recursive"

    def fit(self, train, val, horizon):
        super().fit(train, val, 1)          # modèle à 1 pas
        return self

    def predict(self, history, horizon):
        h = history.iloc[-self.lookback:]
        w = self._features(h.index, h.values)                      # (L, 6)
        cal = calendar_features(_future_index(history, horizon), self.tz, self.country)
        out = []
        for k in range(horizon):
            p = float(self.model(w[None], training=False).numpy()[0, 0])
            out.append(p)
            w = np.vstack([w[1:], np.concatenate([[p], cal[k]]).astype("float32")])
        return np.array(out) * self.std + self.mean

FAMILIES = {c.family: c for c in (SeasonalNaive,SarimaForecaster,ProphetForecaster, LSTMDirect, LSTMRecursive)}


def build_forecaster(family, cfg, params):
    if family == "baseline":
        return SeasonalNaive()
    if family == "sarima":
        return SarimaForecaster(**cfg["sarima"])
    if family == "prophet":
        return ProphetForecaster(country=params["data"]["country_holidays"], **cfg["prophet"])
    if family in ("lstm_direct", "lstm_recursive"):
        d = params["data"]
        return FAMILIES[family](tz=d["local_tz"], country=d["country_holidays"], **cfg["lstm"])
    raise ValueError(f"Famille inconnue : {family}")

def load_forecaster(directory):
    fam = json.loads((Path(directory) / "meta.json").read_text())["family"]
    return FAMILIES[fam].load(directory)