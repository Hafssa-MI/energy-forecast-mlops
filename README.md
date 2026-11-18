# Prévision de la consommation électrique (P8)
![CI](https://github.com/Hafssa-MI/energy-forecast-mlops/actions/workflows/ci.yml/badge.svg)
Projet MLOps : séries temporelles et déploiement multi-environnements (dev, staging, prod).
Outils : Git/GitHub, DVC, MLflow, Docker, FastAPI, Prometheus, Grafana.
## Données (DVC)
Les données et modèles sont versionnés avec DVC. Le stockage distant est hébergé sur DagsHub.
Après un `git pull`, récupérer les données avec `dvc pull`. L'identifiant et le jeton DagsHub
se configurent en local avec `dvc remote modify dagshub --local ...` (jamais dans Git).
## Suivi des expériences (MLflow sur DagsHub)
Le tracking et le registre des modèles sont hébergés sur DagsHub. Dans chaque terminal,
définir avant tout entraînement (le jeton n'est jamais versionné) :

    $env:MLFLOW_TRACKING_URI="https://dagshub.com/Hafssa-MI/energy-forecast-mlops.mlflow"
    $env:MLFLOW_TRACKING_USERNAME="<utilisateur DagsHub>"
    $env:MLFLOW_TRACKING_PASSWORD="<jeton DagsHub>"

Vérifier la connexion : `python scripts/check_mlflow.py`.
Une expérience par environnement : energy-dev, energy-staging, energy-prod.
## Reproduire le pipeline
    git pull
    dvc pull
    python scripts/use_env.py dev      # ou staging / prod
    dvc repro                          # entraîne les 5 modèles x 2 horizons
    dvc metrics show                   # compare les résultats
Variables MLflow à définir avant dvc repro : voir la section MLflow.

## API FastAPI

L'API expose les endpoints de prévision, de réception des observations réelles et les métriques Prometheus.

Consultez la [documentation de l'API](docs/api.md) pour les détails.