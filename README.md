# Prévision de la consommation électrique (P8)
Projet MLOps : séries temporelles et déploiement multi-environnements (dev, staging, prod).
Outils : Git/GitHub, DVC, MLflow, Docker, FastAPI, Prometheus, Grafana.
## Données (DVC)
Les données et modèles sont versionnés avec DVC. Le stockage distant est hébergé sur DagsHub.
Après un `git pull`, récupérer les données avec `dvc pull`. L'identifiant et le jeton DagsHub
se configurent en local avec `dvc remote modify dagshub --local ...` (jamais dans Git).