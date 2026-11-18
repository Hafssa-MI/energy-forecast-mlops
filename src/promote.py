
"""Promotion des modèles dans le MLflow Model Registry (via les alias).
python src/promote.py --env dev     meilleur run de energy-dev      -> alias 'dev'
python src/promote.py --env staging meilleur run de energy-staging -> alias 'staging'
python src/promote.py --env prod     version 'staging' validée   -> alias 'production'
Sélection sur la MAE de VALIDATION (val_mae), jamais sur le test.
Un modèle n'est promu que s'il est meilleur que l'actuel d'au moins `promotion_margin`."""
import argparse
import os

import mlflow
from mlflow.tracking import MlflowClient

from common import load_params

ALIAS = {"dev": "dev", "staging": "staging", "prod": "production"}


def current(client, name, alias):
    try:
        return client.get_model_version_by_alias(name, alias)
    except Exception:
        return None


def better(new_mae, old, margin):
    return old is None or new_mae < float(old.tags["mae"]) * (1 - margin)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", required=True, choices=list(ALIAS))
    env = ap.parse_args().env
    params = load_params()
    margin = params["promotion_margin"]
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    client = MlflowClient()

    for kind in ("short", "long"):
        name, alias = f"energy-forecaster-{kind}", ALIAS[env]
        old = current(client, name, alias)
        if env == "prod":  # on promeut la version validée en staging
            src = current(client, name, "staging")
            if src is None:
                print(f"[{kind}] aucun modèle 'staging' à promouvoir")
                continue
            version, mae, family = src.version, float(src.tags["mae"]), src.tags["family"]
        else:  # on choisit le meilleur run de l'expérience
            exp = client.get_experiment_by_name(params["envs"][env]["mlflow_experiment"])
            runs = client.search_runs(
                [exp.experiment_id],
                f"tags.kind = '{kind}' and tags.candidate = 'true' and metrics.val_mae > 0",
                order_by=["metrics.val_mae ASC"],
                max_results=1,
            )
            if not runs:
                print(f"[{kind}] aucun run trouvé")
                continue
            r = runs[0]
            mae, family = r.data.metrics["val_mae"], r.data.tags["family"]
            if not better(mae, old, margin):
                print(f"[{kind}] {family} (MAE {mae:.0f}) n'améliore pas '{alias}' de {margin:.0%} : pas de promotion")
                continue
            mv = mlflow.register_model(f"runs:/{r.info.run_id}/bundle", name)
            client.set_model_version_tag(name, mv.version, "mae", str(mae))
            client.set_model_version_tag(name, mv.version, "family", family)
            version = mv.version
        if env == "prod" and not better(mae, old, margin):
            print(f"[{kind}] la version {version} n'améliore pas 'production' de {margin:.0%} : pas de promotion")
            continue
        client.set_registered_model_alias(name, alias, version)
        print(f"[{kind}] {name} v{version} ({family}, MAE {mae:.0f}) -> alias '{alias}'")


if __name__ == "__main__":
    main()
