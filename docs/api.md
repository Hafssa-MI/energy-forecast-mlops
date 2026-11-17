
# API de prévision de consommation électrique

## Présentation

L'API est développée avec FastAPI. Elle charge les modèles enregistrés dans MLflow via un alias configurable et expose des endpoints pour générer des prévisions, recevoir des observations réelles et suivre les performances avec Prometheus.

## Démarrage local

Activer l'environnement virtuel, configurer les variables d'environnement puis lancer :

```bash
uvicorn api.app:app --port 8000
```

## Endpoints disponibles

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/health` | Vérifie l'état de l'API et les modèles chargés |
| GET | `/model-info` | Retourne les informations sur les modèles actifs |
| POST | `/reload` | Recharge les modèles depuis MLflow |
| GET | `/forecast/short?horizon=24` | Prévision à court terme, jusqu'à 24 heures |
| GET | `/forecast/long?horizon=168` | Prévision à long terme, jusqu'à 168 heures |
| POST | `/observations` | Reçoit les observations réelles et calcule les erreurs |
| GET | `/metrics` | Expose les métriques au format Prometheus |

## Exemple d'utilisation

### Prévision à court terme

```bash
curl.exe "http://localhost:8000/forecast/short?horizon=6"
```

### Prévision à long terme

```bash
curl.exe "http://localhost:8000/forecast/long?horizon=24"
```

### Envoi d'observations réelles

```bash
curl.exe -X POST "http://localhost:8000/observations" -H "Content-Type: application/json" -d "[{\"timestamp\":\"2020-09-01 00:00:00\",\"value_mw\":42000}]"
```

### Consultation des métriques

```bash
curl.exe http://localhost:8000/metrics
```

## Variables d'environnement

| Variable | Valeur par défaut | Description |
|---|---|---|
| `ENV` | `dev` | Environnement actif |
| `MODEL_ALIAS` | `dev` | Alias MLflow utilisé pour charger les modèles |
| `MLFLOW_TRACKING_URI` | `http://localhost:5000` | URI du serveur MLflow |
| `DATA_DIR` | `data/processed` | Répertoire des données historiques |
| `MODEL_CACHE` | `/tmp/model_cache` | Répertoire de cache des modèles |
| `LOG_LEVEL` | `INFO` | Niveau de journalisation |

Les variables `MLFLOW_TRACKING_USERNAME` et `MLFLOW_TRACKING_PASSWORD` permettent de configurer l'authentification auprès de DagsHub. Elles doivent rester confidentielles.
