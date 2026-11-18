# Energy Forecast MLOps

Projet de prévision de la consommation électrique utilisant des techniques de Machine Learning et une architecture MLOps.

Le système réalise des prévisions à deux horizons :
- Court terme : 24 heures.
- Long terme : 168 heures (7 jours).

## Architecture

```text
Données OPSD
    |
    v
DVC
    |
    v
Entraînement et évaluation
    |
    v
MLflow
    |
    v
Registre des modèles
    |
    v
API FastAPI
    |
    v
Prometheus / Grafana
```

## Technologies utilisées

- Python 3.11
- FastAPI
- DVC
- MLflow
- Docker et Docker Compose
- Prometheus
- Grafana
- Git et GitHub
- DagsHub

## Installation

Cloner le dépôt :

```powershell
git clone https://github.com/Hafssa-MI/energy-forecast-mlops.git
cd energy-forecast-mlops
```

Créer un environnement virtuel :

```powershell
py -3.11 -m venv .venv
```

Activer l'environnement :

```powershell
.\.venv\Scripts\Activate.ps1
```

Installer les dépendances :

```powershell
pip install -r requirements.txt
```

Installer les dépendances de l'API si nécessaire :

```powershell
pip install -r requirements-api.txt
```

Configurer les accès GitHub et DagsHub, notamment les jetons nécessaires à DVC et MLflow.

## Pipeline DVC

Vérifier l'état des données :

```powershell
dvc status
```

Récupérer les données :

```powershell
dvc pull
```

Exécuter le pipeline :

```powershell
dvc repro
```

Envoyer les données et artefacts versionnés :

```powershell
dvc push
```

## Environnements de déploiement

Le projet comporte trois environnements Docker Compose :

| Environnement | API | Prometheus | Grafana |
|---|---:|---:|---:|
| DEV | 8001 | 9091 | 3001 |
| STAGING | 8002 | 9092 | 3002 |
| PROD | 8003 | 9093 | 3003 |

### DEV

```powershell
docker compose -p energy-dev --env-file envs/dev.env -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d --build
```

### STAGING

```powershell
docker compose -p energy-staging --env-file envs/staging.env -f docker/docker-compose.yml -f docker/docker-compose.staging.yml up -d --build
```

### PROD

```powershell
docker compose -p energy-prod --env-file envs/prod.env -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d --build
```

Pour vérifier les conteneurs :

```powershell
docker compose ps
```

Pour consulter les logs :

```powershell
docker compose logs -f api
```

Pour arrêter un environnement, utiliser la commande `docker compose down` avec les mêmes options `-p`, `--env-file` et `-f` que lors de son démarrage.

## Promotion des modèles

Les modèles sont enregistrés dans MLflow sous les noms :

- `energy-forecaster-short`
- `energy-forecaster-long`

La promotion est réalisée avec :

```powershell
python src/promote.py --env dev
python src/promote.py --env staging
python src/promote.py --env prod
```

La sélection repose sur `val_mae`. Une amélioration d'au moins 2 % est nécessaire pour promouvoir un nouveau modèle.

## Supervision

Prometheus collecte les métriques de l'API et Grafana permet de les visualiser.

La métrique principale de qualité des prévisions est :

`forecast_rolling_mae_mw`

L'alerte `ForecastErrorHigh` signale une dégradation de la qualité des prévisions lorsque le seuil configuré est dépassé.

## Documentation

La documentation détaillée est disponible dans le dossier `docs/` :

- `deploiement.md` : installation, configuration et déploiement des environnements.
- `rollback.md` : procédures de retour arrière.
- `api.md` : documentation de l'API.
- `docker.md` : configuration Docker.
- `mlflow.md` : suivi des expériences.
- `registre.md` : registre et promotion des modèles.
- `supervision.md` : supervision et réentraînement.
- `tuning.md` : réglage des modèles.
- `resultats-dev.md` : résultats expérimentaux en DEV.

## Équipe et passation

La répartition du travail et les informations de passation sont disponibles dans `docs/passation.md`.