"""Entraîne UN modèle (famille + horizon), l'évalue, le journalise dans MLflow.
Usage : python src/train.py --family sarima --kind short"""
import argparse
import json
import time

import matplotlib
import mlflow
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import (ROOT, backtest, env_cfg, git_commit, load_params, load_splits, setup_mlflow)
from forecasters import FAMILIES, build_forecaster


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True, choices=list(FAMILIES))
    ap.add_argument("--kind", required=True, choices=["short", "long"])
    a = ap.parse_args()

    params = load_params()
    cfg, env = env_cfg(params), params["active_env"]
    H = params["horizons"][a.kind]
    train, val, test = load_splits(cfg)
    full = pd.concat([train, val, test])
    out_dir = ROOT / "models" / f"{a.family}_{a.kind}"
    (ROOT / "metrics").mkdir(exist_ok=True)

    setup_mlflow(cfg["mlflow_experiment"])
    with mlflow.start_run(run_name=f"{a.family}-{a.kind}"):
        mlflow.set_tags({"family": a.family, "kind": a.kind, "env": env, "candidate": "true",
                         "git_commit": git_commit(), "data_end": str(full.index[-1])})
        mlflow.log_params({"horizon": H, "train_hours": len(train), "val_hours": len(val),
                           "test_hours": len(test), "active_env": env})
        mlflow.log_params({f"{a.family}.{k}": str(v) for k, v in
                           (cfg.get("sarima") if a.family == "sarima" else
                            cfg.get("prophet") if a.family == "prophet" else
                            cfg.get("lstm") if a.family.startswith("lstm") else {}).items()})

        t0 = time.time()
        fc = build_forecaster(a.family, cfg, params).fit(train, val, H)
        mlflow.log_metric("train_seconds", time.time() - t0)

        res, P, T = backtest(fc, full, len(test), H, params["backtest"]["origin_stride"],
                             cfg.get("max_origins"))
        mlflow.log_metrics({k: res[k] for k in ("mae", "rmse", "mape")})
        mlflow.log_metric("n_origins", res["n_origins"])
        print(f"[{a.family}/{a.kind}] MAE={res['mae']:.0f} MW  RMSE={res['rmse']:.0f}  "
              f"MAPE={res['mape']:.2f}%  ({res['n_origins']} origines)")

        fig, ax = plt.subplots(2, 1, figsize=(9, 6))
        ax[0].plot(res["mae_by_step"])
        ax[0].set(title="Erreur absolue moyenne selon l'horizon", xlabel="heures après l'origine", ylabel="MAE (MW)")
        ax[1].plot(T[-1], label="réel")
        ax[1].plot(P[-1], label="prévu")
        ax[1].set(title="Dernière origine du test", ylabel="MW")
        ax[1].legend()
        fig.tight_layout()
        fig.savefig(ROOT / "metrics" / f"{a.family}_{a.kind}.png", dpi=120)
        plt.close(fig)
        mlflow.log_artifact(str(ROOT / "metrics" / f"{a.family}_{a.kind}.png"), "plots")

        fc.save(out_dir)
        mlflow.log_artifacts(str(out_dir), "bundle")     # le "bundle" sera enregistré dans le Registry
        (ROOT / "metrics" / f"{a.family}_{a.kind}.json").write_text(
            json.dumps({k: res[k] for k in ("mae", "rmse", "mape")}, indent=2))


if __name__ == "__main__":
    main()
