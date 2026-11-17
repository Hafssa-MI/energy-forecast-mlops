
"""API de prévision de consommation électrique (FastAPI + métriques Prometheus)."""

import logging
import os
import sys
import time
from collections import deque
from pathlib import Path

import mlflow
import pandas as pd
from fastapi import FastAPI, HTTPException
from mlflow.tracking import MlflowClient
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from pydantic import BaseModel
from starlette.responses import Response

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from forecasters import load_forecaster  # noqa: E402


ENV = os.getenv("ENV", "dev")
ALIAS = os.getenv("MODEL_ALIAS", "dev")
DATA_DIR = Path(os.getenv("DATA_DIR", "data/processed"))
CACHE = Path(os.getenv("MODEL_CACHE", "/tmp/model_cache"))
HORIZONS = {"short": 24, "long": 168}

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("api")

app = FastAPI(
    title="Prévision de consommation électrique",
    version="1.0",
)

# Métriques Prometheus
REQS = Counter(
    "forecast_requests_total",
    "Requêtes de prévision",
    ["kind"],
)

LAT = Histogram(
    "forecast_latency_seconds",
    "Latence des prévisions",
    ["kind"],
)

OBS = Counter(
    "observations_total",
    "Observations réelles reçues",
)

ROLL_MAE = Gauge(
    "forecast_rolling_mae_mw",
    "MAE glissante (MW)",
    ["kind"],
)

LAST_ERR = Gauge(
    "forecast_last_abs_error_mw",
    "Dernière erreur absolue (MW)",
    ["kind"],
)

MODEL_INFO = Gauge(
    "model_info",
    "Modèle actif (valeur 1)",
    ["kind", "version", "family", "env"],
)

# État de l'API
state = {
    "models": {},
    "versions": {},
    "history": None,
    "pred": {k: {} for k in HORIZONS},
    "errs": {k: deque(maxlen=168) for k in HORIZONS},
}


def load_models():
    """Charge les modèles associés à l'alias MLflow sélectionné."""
    client = MlflowClient()

    for kind in HORIZONS:
        name = f"energy-forecaster-{kind}"

        mv = client.get_model_version_by_alias(name, ALIAS)

        path = mlflow.artifacts.download_artifacts(
            artifact_uri=f"models:/{name}@{ALIAS}",
            dst_path=str(CACHE / f"{kind}-v{mv.version}"),
        )

        state["models"][kind] = load_forecaster(path)

        fam = mv.tags.get("family", "?")

        state["versions"][kind] = {
            "model": name,
            "version": mv.version,
            "family": fam,
            "val_mae": mv.tags.get("mae"),
        }

        MODEL_INFO.labels(
            kind, mv.version, fam, ENV
        ).set(1)

        log.info(
            "Modèle %s chargé : v%s (%s)",
            name,
            mv.version,
            fam,
        )


def load_history():
    """Charge et rassemble les historiques train, val et test."""
    parts = [
        pd.read_csv(
            DATA_DIR / f"{n}.csv",
            index_col=0,
            parse_dates=True,
        ).iloc[:, 0]
        for n in ("train", "val", "test")
    ]

    state["history"] = pd.concat(parts).astype(float)


@app.on_event("startup")
def startup():
    """Initialise MLflow, l'historique et les modèles au démarrage."""
    mlflow.set_tracking_uri(
        os.getenv(
            "MLFLOW_TRACKING_URI",
            "http://localhost:5000",
        )
    )

    load_history()
    load_models()


class Observation(BaseModel):
    timestamp: str
    value_mw: float


@app.get("/health")
def health():
    """Vérifie l'état de fonctionnement de l'API."""
    return {
        "status": "ok",
        "env": ENV,
        "alias": ALIAS,
        "models_loaded": list(state["models"]),
    }


@app.get("/model-info")
def model_info():
    """Retourne les informations sur les modèles actifs."""
    return {
        "env": ENV,
        "alias": ALIAS,
        "models": state["versions"],
        "history_end": str(state["history"].index[-1]),
    }


@app.post("/reload")
def reload_models():
    """Recharge les modèles depuis le registre MLflow."""
    load_models()
    return {"reloaded": state["versions"]}


def _forecast(kind, horizon):
    """Génère une prévision et enregistre les prédictions."""
    h = state["history"]

    if horizon < 1 or horizon > HORIZONS[kind]:
        raise HTTPException(
            422,
            f"horizon entre 1 et {HORIZONS[kind]} heures",
        )

    t0 = time.time()

    y = state["models"][kind].predict(
        h,
        HORIZONS[kind],
    )

    idx = h.index[-1] + pd.to_timedelta(
        range(1, HORIZONS[kind] + 1),
        unit="h",
    )

    for ts, v in zip(idx, y):
        state["pred"][kind].setdefault(
            ts,
            float(v),
        )

    REQS.labels(kind).inc()
    LAT.labels(kind).observe(time.time() - t0)

    return {
        "kind": kind,
        "model": state["versions"][kind],
        "forecast": [
            {
                "timestamp": str(t),
                "load_mw": round(float(v), 1),
            }
            for t, v in list(zip(idx, y))[:horizon]
        ],
    }


@app.get("/forecast/short")
def forecast_short(horizon: int = 24):
    """Prévision à court terme, jusqu'à 24 heures."""
    return _forecast("short", horizon)


@app.get("/forecast/long")
def forecast_long(horizon: int = 168):
    """Prévision à long terme, jusqu'à 168 heures."""
    return _forecast("long", horizon)


@app.post("/observations")
def add_observations(obs: list[Observation]):
    """
    Reçoit les consommations réelles :
    met à jour l'historique et mesure l'erreur de prévision.
    """
    for o in obs:
        ts = pd.Timestamp(o.timestamp)

        state["history"].loc[ts] = o.value_mw
        OBS.inc()

        for kind in HORIZONS:
            p = state["pred"][kind].pop(ts, None)

            if p is not None:
                e = abs(p - o.value_mw)

                state["errs"][kind].append(e)

                LAST_ERR.labels(kind).set(e)

                ROLL_MAE.labels(kind).set(
                    sum(state["errs"][kind])
                    / len(state["errs"][kind])
                )

    state["history"] = state["history"].sort_index()

    return {
        "history_end": str(state["history"].index[-1])
    }


@app.get("/metrics")
def metrics():
    """Expose les métriques au format Prometheus."""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
