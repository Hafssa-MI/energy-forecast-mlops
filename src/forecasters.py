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


FAMILIES = {c.family: c for c in (SeasonalNaive,)}


def build_forecaster(family, cfg, params):
    if family == "baseline":
        return SeasonalNaive()
    raise ValueError(f"Famille inconnue pour l'instant : {family}")


def load_forecaster(directory):
    fam = json.loads((Path(directory) / "meta.json").read_text())["family"]
    return FAMILIES[fam].load(directory)