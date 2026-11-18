\# Fiche de passation — Energy Forecast MLOps



\## 1. Objectif



Cette fiche présente la répartition du travail réalisé sur le projet Energy Forecast MLOps ainsi que les informations nécessaires pour assurer sa continuité.



\## 2. Répartition du travail



Le travail a été réalisé en plusieurs phases.



| Phase | Responsable | Travail réalisé |

|---|---|---|

| Phase 1 | Armin | Première phase de développement et mise en place des composants du projet. |

| Phase 2 | Hanane | Deuxième phase de développement, intégration et réalisation des tâches attribuées. |

| Finalisation | Armin et Hanane | Intégration des contributions, vérifications, documentation et finalisation du projet. |



Cette répartition reflète les responsabilités respectives pendant les différentes phases.



\## 3. Architecture du projet



Le projet Energy Forecast MLOps repose sur les composants suivants :



\- OPSD : source des données de consommation électrique.

\- DVC : gestion et versionnement des données.

\- Pipeline Python : préparation des données, entraînement et évaluation.

\- MLflow : suivi des expériences et gestion des modèles.

\- Registre MLflow : gestion des versions et des alias.

\- FastAPI : exposition des prédictions.

\- Docker Compose : déploiement des environnements.

\- Prometheus : collecte des métriques.

\- Grafana : visualisation et supervision.



\## 4. Environnements disponibles



Trois environnements sont prévus :



| Environnement | API | Prometheus | Grafana |

|---|---:|---:|---:|

| DEV | 8001 | 9091 | 3001 |

| STAGING | 8002 | 9092 | 3002 |

| PROD | 8003 | 9093 | 3003 |



Les fichiers de configuration sont stockés dans le dossier `envs/`.



\## 5. Fichiers importants



| Fichier ou dossier | Rôle |

|---|---|

| `dvc.yaml` | Définition du pipeline DVC |

| `dvc.lock` | Verrouillage des dépendances du pipeline |

| `params.yaml` | Paramètres du projet |

| `src/` | Scripts d'entraînement et de promotion |

| `api/` | Application FastAPI |

| `docker/` | Fichiers Docker Compose et Dockerfile |

| `monitoring/` | Configuration Prometheus et simulation du flux |

| `docs/` | Documentation technique |



\## 6. Procédures principales



Récupérer les données :



```powershell

dvc pull

```



Exécuter le pipeline :



```powershell

dvc repro

```



Démarrer un environnement Docker Compose : consulter `docs/deploiement.md`.



Promouvoir un modèle :



```powershell

python src/promote.py --env dev

```



Recharger les modèles de l'API DEV :



```powershell

Invoke-RestMethod -Method Post http://localhost:8001/reload

```



\## 7. Points d'attention



\- Conserver les jetons DagsHub et autres secrets hors du dépôt Git.

\- Vérifier la disponibilité des données et des modèles avant le déploiement.

\- Vérifier les alias MLflow correspondant à l'environnement.

\- Utiliser `val\_mae` pour la sélection des modèles.

\- Respecter la règle d'amélioration de 2 % lors de la promotion.

\- Contrôler les métriques Prometheus et les tableaux de bord Grafana.

\- Consulter les procédures de rollback en cas de régression.



\## 8. Documentation de référence



Les documents suivants facilitent la reprise du projet :



\- `docs/deploiement.md`

\- `docs/rollback.md`

\- `docs/api.md`

\- `docs/docker.md`

\- `docs/mlflow.md`

\- `docs/registre.md`

\- `docs/supervision.md`

\- `docs/tuning.md`



\## 9. Conclusion



Le projet a été développé en plusieurs phases avec une contribution d'Armin lors de la première phase, de Hanane lors de la deuxième phase et une finalisation commune.



Cette documentation facilite la compréhension de l'architecture, le déploiement des environnements, la supervision et la continuité du travail.

