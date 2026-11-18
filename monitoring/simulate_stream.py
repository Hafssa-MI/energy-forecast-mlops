
"""Rejoue le flux de production (stream.csv) jour par jour :
prévoit, puis envoie les vraies valeurs."""

import argparse
import time

import pandas as pd
import requests

ap = argparse.ArgumentParser()

ap.add_argument(
    "--api",
    default="http://localhost:8001",
)

ap.add_argument(
    "--stream",
    default="data/processed/stream.csv",
)

ap.add_argument(
    "--delay",
    type=float,
    default=2.0,
    help="Secondes entre deux jours simulés",
)

ap.add_argument(
    "--shock-from",
    type=int,
    default=None,
    help="Jour à partir duquel on perturbe les données",
)

ap.add_argument(
    "--shock",
    type=float,
    default=1.25,
    help="Facteur multiplicatif pour simuler une dérive",
)

a = ap.parse_args()

s = pd.read_csv(
    a.stream,
    index_col=0,
    parse_dates=True,
).iloc[:, 0]

total_days = len(s) // 24

print(f"Début de la simulation : {total_days} jours")

for d in range(total_days):

    day = s.iloc[d * 24:(d + 1) * 24].copy()

    # 1. Demander les prévisions
    requests.get(
        f"{a.api}/forecast/short",
        timeout=120,
    ).raise_for_status()

    requests.get(
        f"{a.api}/forecast/long",
        timeout=120,
    ).raise_for_status()

    # 2. Simuler une dérive éventuelle
    if a.shock_from is not None and d >= a.shock_from:
        day = day * a.shock

    # 3. Envoyer les observations réelles
    body = [
        {
            "timestamp": str(t),
            "value_mw": float(v),
        }
        for t, v in day.items()
    ]

    requests.post(
        f"{a.api}/observations",
        json=body,
        timeout=60,
    ).raise_for_status()

    print(f"Jour {d + 1}/{total_days} envoyé")

    time.sleep(a.delay)

print("Simulation terminée.")
