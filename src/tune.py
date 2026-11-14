"""Tuning : essaie une grille de réglages et classe selon la MAE de VALIDATION (jamais le test).
Usage : python src/tune.py --family sarima --kind short [--max-origins 10]"""
import argparse
import itertools
import json
import time

import pandas as pd

from common import ROOT, backtest, env_cfg, git_commit, load_params, load_splits, setup_mlflow
from forecasters import build_forecaster

CFG_KEY = {"sarima": "sarima", "prophet": "prophet", "lstm_direct": "lstm", "lstm_recursive": "lstm"}


def expand_grid(grid):
    """{'a': [1, 2], 'b': [3]} -> [{'a': 1, 'b': 3}, {'a': 2, 'b': 3}]"""
    keys = list(grid)
    return [dict(zip(keys, combo)) for combo in itertools.product(*(grid[k] for k in keys))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True, choices=list(CFG_KEY))
    ap.add_argument("--kind", required=True, choices=["short", "long"])
    ap.add_argument("--max-origins", type=int, default=None,
                    help="limite le nombre de prévisions de validation")
    a = ap.parse_args()

    import mlflow
    params = load_params()
    cfg, env = env_cfg(params), params["active_env"]
    key = CFG_KEY[a.family]
    H = params["horizons"][a.kind]
    train, val, _ = load_splits(cfg)            # le test n'est jamais utilisé ici
    full = pd.concat([train, val])
    max_origins = a.max_origins or cfg.get("max_origins")
    candidates = expand_grid(params["tuning"][key])
    print(f"{len(candidates)} combinaisons pour {a.family}/{a.kind} (env {env})")

    setup_mlflow(params["tuning"]["experiment"])
    rows = []
    for i, over in enumerate(candidates, 1):
        cfg_i = {**cfg, key: {**cfg[key], **over}}
        with mlflow.start_run(run_name=f"{a.family}-{a.kind}-{i}"):
            mlflow.set_tags({"family": a.family, "kind": a.kind, "env": env,
                             "git_commit": git_commit(), "stage": "tuning"})
            mlflow.log_params({k: str(v) for k, v in over.items()})
            t0 = time.time()
            fc = build_forecaster(a.family, cfg_i, params).fit(train, val, H)
            res, _, _ = backtest(fc, full, len(val), H, params["backtest"]["origin_stride"], max_origins)
            mlflow.log_metrics({"val_mae": res["mae"], "val_rmse": res["rmse"],
                                "val_mape": res["mape"], "train_seconds": time.time() - t0})
        rows.append({"params": over, "val_mae": res["mae"], "val_rmse": res["rmse"],
                     "val_mape": res["mape"]})
        print(f"[{i}/{len(candidates)}] val MAE={res['mae']:.0f}  {over}")

    rows.sort(key=lambda r: r["val_mae"])
    out = ROOT / "tuning"
    out.mkdir(exist_ok=True)
    (out / f"{a.family}_{a.kind}.json").write_text(json.dumps({"env": env, "ranking": rows}, indent=2))
    print("Meilleur :", rows[0])


if __name__ == "__main__":
    main()