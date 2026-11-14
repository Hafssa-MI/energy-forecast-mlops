"""Fonctions communes à toutes les étapes du projet."""
import os
import subprocess
from pathlib import Path

import holidays
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"


def load_params(path=None):
    with open(path or ROOT / "params.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def env_cfg(params):
    """Configuration de l'environnement actif (dev, staging ou prod)."""
    return params["envs"][params["active_env"]]


def read_series(path):
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    return df.iloc[:, 0].astype(float)


def load_splits(cfg):
    """Retourne train, val, test. Le flux 'prod' (stream.csv) n'est jamais lu ici."""
    train = read_series(PROC / "train.csv")
    val = read_series(PROC / "val.csv")
    test = read_series(PROC / "test.csv")
    if cfg.get("max_train_days"):
        train = train.iloc[-int(cfg["max_train_days"]) * 24:]
    return train, val, test


def calendar_features(index, tz="Europe/Berlin", country="DE"):
    """5 variables calendaires : heure et jour de semaine (sin/cos) + jour férié.
    L'index est en UTC (sans fuseau) ; l'heure locale est utilisée pour le calendrier."""
    loc = pd.DatetimeIndex(index).tz_localize("UTC").tz_convert(tz)
    hour, dow = loc.hour.values, loc.dayofweek.values
    hol = holidays.country_holidays(country, years=range(int(loc.year.min()), int(loc.year.max()) + 1))
    is_hol = np.array([d in hol for d in loc.date], dtype=float)
    return np.column_stack([
        np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24),
        np.sin(2 * np.pi * dow / 7), np.cos(2 * np.pi * dow / 7), is_hol,
    ]).astype("float32")


def error_metrics(y_true, y_pred):
    err = np.asarray(y_pred, float) - np.asarray(y_true, float)
    return {
        "mae": float(np.mean(np.abs(err))),
        "rmse": float(np.sqrt(np.mean(err ** 2))),
        "mape": float(np.mean(np.abs(err) / np.abs(y_true)) * 100),
    }


def backtest(fc, full, test_len, horizon, stride, max_origins=None):
    """Évaluation 'rolling origin' : une prévision tous les `stride` heures sur la période de test.
    Chaque prévision n'utilise que le passé de son origine (aucune fuite du futur)."""
    n = len(full)
    origins = list(range(n - test_len - 1, n - horizon, stride))
    if max_origins:
        origins = origins[: int(max_origins)]
    preds, trues = [], []
    for o in origins:
        preds.append(np.asarray(fc.predict(full.iloc[: o + 1], horizon), dtype=float))
        trues.append(full.values[o + 1: o + 1 + horizon])
    P, T = np.vstack(preds), np.vstack(trues)
    res = error_metrics(T, P)
    res["mae_by_step"] = np.mean(np.abs(P - T), axis=0).tolist()
    res["n_origins"] = len(origins)
    return res, P, T


def setup_mlflow(experiment):
    import mlflow
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    mlflow.set_experiment(experiment)


def git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"
