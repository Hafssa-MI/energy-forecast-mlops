\# Guide de déploiement — Energy Forecast MLOps



\## 1. Objectif et architecture



Ce document décrit les étapes nécessaires pour installer, configurer, déployer et superviser le projet Energy Forecast MLOps.



Le projet permet de prévoir la consommation électrique à deux horizons :

\- Court terme : 24 heures.

\- Long terme : 168 heures (7 jours).



\### Architecture globale



```text

Données OPSD

&#x20;    |

&#x20;    v

DVC (gestion et versionnement des données)

&#x20;    |

&#x20;    v

Pipeline d'entraînement et d'évaluation

&#x20;    |

&#x20;    v

MLflow (suivi des expériences)

&#x20;    |

&#x20;    v

Registre MLflow (gestion des versions et alias)

&#x20;    |

&#x20;    v

API FastAPI (prédictions)

&#x20;    |

&#x20;    v

Prometheus (collecte des métriques)

&#x20;    |

&#x20;    v

Grafana (visualisation et supervision)

```



Docker Compose permet de déployer séparément les environnements DEV, STAGING et PROD.



\## 2. Prérequis



Les outils et accès suivants sont nécessaires :



| Outil ou accès | Utilisation |

|---|---|

| Python 3.11 | Exécution du pipeline et des scripts |

| Git | Gestion du code source |

| Docker Desktop | Exécution des services conteneurisés |

| Docker Compose | Orchestration des services |

| GitHub | Hébergement du code source |

| DagsHub | Hébergement des données DVC et du serveur MLflow |

| Jeton DagsHub | Authentification aux services distants |



Il faut également disposer des accès au dépôt GitHub et au projet DagsHub.



Les jetons d'accès doivent être configurés dans les variables d'environnement ou les fichiers locaux prévus à cet effet. Ils ne doivent jamais être publiés dans Git.



\## 3. Données



\### Source des données



Le projet utilise les données OPSD (\*Open Power System Data\*) pour réaliser les prévisions de consommation électrique.



La source doit être conservée avec ses informations de provenance et de licence. Il convient de consulter les métadonnées du jeu de données OPSD utilisé pour identifier précisément sa licence et ses conditions de réutilisation.



\### Colonnes utilisées



Les données temporelles et les valeurs de consommation électrique constituent les informations nécessaires à la préparation des séries temporelles et à l'entraînement des modèles.



Les noms exacts des colonnes dépendent du fichier source utilisé dans le pipeline.



\### Découpage des données



Le projet distingue quatre ensembles :



\- \*\*Train\*\* : données utilisées pour entraîner les modèles.

\- \*\*Validation\*\* : données utilisées pour comparer les modèles et sélectionner les meilleurs paramètres.

\- \*\*Test\*\* : données réservées à l'évaluation finale.

\- \*\*Stream\*\* : données envoyées progressivement à l'API pour simuler l'arrivée de nouvelles observations.



Le flux simulé permet de tester le fonctionnement d'un système en production : réception des observations, comparaison entre valeurs prédites et valeurs réelles, mise à jour des métriques et détection d'une éventuelle dérive.



\## 4. Pipeline DVC



DVC assure le versionnement des données et la reproductibilité du pipeline.



Les fichiers principaux sont :



\- `dvc.yaml` : définition des étapes du pipeline.

\- `dvc.lock` : versions et paramètres des dépendances du pipeline.

\- `params.yaml` : paramètres de configuration.

\- `.dvc/` : configuration DVC du projet.



\### Commandes principales



Vérifier la configuration :



```powershell

dvc status

```



Exécuter le pipeline :



```powershell

dvc repro

```



Envoyer les données et artefacts versionnés vers le stockage distant :



```powershell

dvc push

```



Récupérer les données et artefacts :



```powershell

dvc pull

```



Pour reproduire un entraînement, il faut disposer du code, des paramètres et des données nécessaires.



\## 5. Environnements



Le projet dispose de trois environnements indépendants.



| Élément | DEV | STAGING | PROD |

|---|---|---|---|

| Nom Docker Compose | `energy-dev` | `energy-staging` | `energy-prod` |

| Fichier de configuration | `envs/dev.env` | `envs/staging.env` | `envs/prod.env` |

| Fichier Compose | `docker-compose.dev.yml` | `docker-compose.staging.yml` | `docker-compose.prod.yml` |

| Port API | 8001 | 8002 | 8003 |

| Port Prometheus | 9091 | 9092 | 9093 |

| Port Grafana | 3001 | 3002 | 3003 |

| Alias MLflow | `dev` | `staging` | `production` |



Chaque environnement possède ses propres paramètres et ses propres ports.



Les fichiers `.env` contiennent les paramètres nécessaires au déploiement. Les fichiers `.env.example` servent de modèles de configuration. Les secrets doivent être renseignés localement.



\## 6. Commandes de déploiement



Les commandes suivantes sont exécutées depuis la racine du projet, sous PowerShell.



\### 6.1. Environnement DEV



Démarrer :



```powershell

docker compose -p energy-dev --env-file envs/dev.env -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d --build

```



Vérifier :



```powershell

docker compose -p energy-dev --env-file envs/dev.env -f docker/docker-compose.yml -f docker/docker-compose.dev.yml ps

```



Consulter les logs :



```powershell

docker compose -p energy-dev --env-file envs/dev.env -f docker/docker-compose.yml -f docker/docker-compose.dev.yml logs -f api

```



Tester l'API :



```powershell

curl.exe http://localhost:8001/health

```



Arrêter :



```powershell

docker compose -p energy-dev down

```



Interfaces :

\- API : http://localhost:8001

\- Prometheus : http://localhost:9091

\- Grafana : http://localhost:3001



\### 6.2. Environnement STAGING



Démarrer :



```powershell

docker compose -p energy-staging --env-file envs/staging.env -f docker/docker-compose.yml -f docker/docker-compose.staging.yml up -d --build

```



Vérifier :



```powershell

docker compose -p energy-staging --env-file envs/staging.env -f docker/docker-compose.yml -f docker/docker-compose.staging.yml ps

```



Consulter les logs :



```powershell

docker compose -p energy-staging --env-file envs/staging.env -f docker/docker-compose.yml -f docker/docker-compose.staging.yml logs -f api

```



Tester l'API :



```powershell

curl.exe http://localhost:8002/health

```



Arrêter :



```powershell

docker compose -p energy-staging down

```



Interfaces :

\- API : http://localhost:8002

\- Prometheus : http://localhost:9092

\- Grafana : http://localhost:3002



\### 6.3. Environnement PROD



Démarrer :



```powershell

docker compose -p energy-prod --env-file envs/prod.env -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d --build

```



Vérifier :



```powershell

docker compose -p energy-prod --env-file envs/prod.env -f docker/docker-compose.yml -f docker/docker-compose.prod.yml ps

```



Consulter les logs :



```powershell

docker compose -p energy-prod --env-file envs/prod.env -f docker/docker-compose.yml -f docker/docker-compose.prod.yml logs -f api

```



Tester l'API :



```powershell

curl.exe http://localhost:8003/health

```



Arrêter :



```powershell

docker compose -p energy-prod down

```



Interfaces :

\- API : http://localhost:8003

\- Prometheus : http://localhost:9093

\- Grafana : http://localhost:3003



\### 6.4. Validation de la configuration



Avant le démarrage, il est possible de vérifier la configuration Compose.



Exemple DEV :



```powershell

docker compose -p energy-dev --env-file envs/dev.env -f docker/docker-compose.yml -f docker/docker-compose.dev.yml config --quiet

```



Exemple STAGING :



```powershell

docker compose -p energy-staging --env-file envs/staging.env -f docker/docker-compose.yml -f docker/docker-compose.staging.yml config --quiet

```



Exemple PROD :



```powershell

docker compose -p energy-prod --env-file envs/prod.env -f docker/docker-compose.yml -f docker/docker-compose.prod.yml config --quiet

```



La validation de la configuration ne garantit pas que les modèles ou les services distants soient disponibles.



\## 7. Promotion des modèles



La promotion des modèles entre les environnements suit un processus contrôlé.



\### Promotion du code avec Git



Le processus de développement utilise les branches :



```text

feature/\*

&#x20;   |

&#x20;   v

&#x20;  dev

&#x20;   |

&#x20;   v

&#x20;staging

&#x20;   |

&#x20;   v

&#x20;  main

```



Les modifications sont intégrées par Pull Request afin de permettre la revue du code et l'exécution des vérifications CI.



\### Gestion des données avec DVC



Les données et artefacts nécessaires sont versionnés avec DVC.



Les commandes principales sont :



```powershell

dvc pull

dvc repro

dvc push

```



\### Promotion avec MLflow



Les modèles sont enregistrés dans le registre MLflow sous les noms :



\- `energy-forecaster-short`

\- `energy-forecaster-long`



Les alias utilisés sont :



| Alias | Environnement |

|---|---|

| `dev` | Développement |

| `staging` | Préproduction |

| `production` | Production |



Le script `src/promote.py` permet de promouvoir les modèles :



```powershell

python src/promote.py --env dev

python src/promote.py --env staging

python src/promote.py --env prod

```



\### Règle de promotion de 2 %



La sélection d'un nouveau modèle repose sur la métrique `val\_mae`, calculée sur les données de validation.



Un nouveau modèle est promu uniquement si sa `val\_mae` est inférieure d'au moins 2 % à celle du modèle actuellement associé à l'alias cible.



La métrique de test n'est pas utilisée pour la promotion. Elle reste réservée à l'évaluation finale afin d'éviter les biais de sélection.



\## 8. Supervision



La supervision repose sur deux outils :



\- \*\*Prometheus\*\* collecte les métriques exposées par l'API FastAPI.

\- \*\*Grafana\*\* permet de visualiser l'évolution des métriques.



\### Métrique principale



La métrique surveillée est :



```text

forecast\_rolling\_mae\_mw

```



Elle représente la MAE glissante en MW.



Deux horizons sont suivis :

\- `short` : 24 heures.

\- `long` : 168 heures.



\### Alerte



L'alerte `ForecastErrorHigh` est définie dans :



```text

monitoring/alerts.yml

```



Elle se déclenche lorsque la MAE glissante court terme dépasse 2000 MW pendant au moins deux minutes.



\### Vérification



Exemple pour DEV :



```powershell

(Invoke-WebRequest -UseBasicParsing http://localhost:8001/metrics).Content -split "`n" | Select-String "forecast\_rolling\_mae\_mw"

```



Les alertes Prometheus sont accessibles à :



http://localhost:9091/alerts



\### Procédure de réentraînement



Lorsqu'une dégradation est détectée :



1\. Analyser l'alerte dans Prometheus.

2\. Examiner les métriques dans Grafana.

3\. Vérifier les observations réelles reçues.

4\. Réentraîner les modèles en DEV.

5\. Comparer les nouveaux runs dans MLflow.

6\. Vérifier l'amélioration de `val\_mae`.

7\. Promouvoir le modèle si le gain atteint au moins 2 %.

8\. Recharger les modèles dans l'API.



Commande de rechargement :



```powershell

Invoke-RestMethod -Method Post http://localhost:8001/reload

```



Vérifier les modèles actifs :



```powershell

Invoke-RestMethod http://localhost:8001/model-info

```



\## 9. Retour arrière



En cas de problème après un déploiement, trois types de retour arrière sont possibles.



\### Retour arrière du modèle



Le registre MLflow utilise des alias pour désigner les versions actives.



En cas de dégradation, il faut réaffecter l'alias à la version précédente du modèle dans le registre MLflow, puis recharger les modèles dans l'API :



```powershell

Invoke-RestMethod -Method Post http://localhost:8001/reload

```



La version précédente doit être identifiée dans le registre avant de modifier l'alias.



\### Retour arrière du code



Pour annuler un commit déjà intégré, utiliser :



```powershell

git log --oneline

git revert <commit\_id>

git push

```



`git revert` crée un nouveau commit qui annule les changements du commit ciblé sans réécrire l'historique Git.



\### Retour arrière de l'image Docker



Il est possible de redéployer une image Docker précédente à partir de son tag conservé dans le registre d'images.



Il faut identifier le tag précédent, le sélectionner dans la configuration de déploiement et redémarrer les services concernés.



\## 10. Résultats et limites



Les résultats disponibles dans le dépôt comprennent les résultats DEV et les résultats de tuning sur validation.



Les résultats DEV ont été obtenus avec une configuration légère de 120 jours d'entraînement et 8 prévisions évaluées par modèle.



Ils valident le fonctionnement de la chaîne technique, mais ne représentent pas nécessairement les performances finales en production.



Le tableau ci-dessous reprend les résultats DEV disponibles :



| Modèle | Horizon | MAE (MW) | RMSE | MAPE (%) |

|---|---:|---:|---:|---:|

| Baseline | 24 h | 891 | 1 144 | 1,72 |

| SARIMA | 24 h | 2 631 | 3 933 | 5,11 |

| Prophet | 24 h | 4 282 | 5 066 | 8,91 |

| LSTM récursif | 24 h | 6 212 | 7 351 | 13,38 |

| LSTM direct | 24 h | 7 872 | 9 205 | 16,89 |

| Baseline | 168 h | 1 192 | 1 579 | 2,42 |

| SARIMA | 168 h | 4 552 | 5 947 | 9,42 |

| Prophet | 168 h | 4 903 | 5 724 | 10,45 |

| LSTM récursif | 168 h | 6 776 | 8 126 | 15,14 |

| LSTM direct | 168 h | 8 604 | 10 063 | 19,02 |



\*\*Limite :\*\* le fichier `docs/resultats-staging.md` n'est pas présent dans la version actuelle du dépôt. Le tableau final de staging devra être ajouté dès que les résultats correspondants seront disponibles.



Les résultats du tuning sont calculés sur validation. Le modèle LSTM récursif à 168 heures n'a pas encore été réglé. Les scores doivent donc être interprétés en tenant compte de ces limites.



\## 11. Dépannage



| Problème | Solution |

|---|---|

| Docker Compose ne démarre pas | Vérifier que Docker Desktop est démarré. |

| Port déjà utilisé | Vérifier les applications utilisant les ports 8001 à 8003, 9091 à 9093 et 3001 à 3003. |

| API inaccessible | Vérifier l'état des conteneurs avec `docker compose ps` et consulter les logs. |

| Erreur d'accès DagsHub | Vérifier le jeton et les variables d'environnement. |

| Modèle introuvable dans MLflow | Vérifier l'existence du modèle et de son alias dans le registre. |

| Données DVC manquantes | Exécuter `dvc pull` après avoir vérifié l'accès au dépôt distant. |

| Alerte de dérive | Examiner `forecast\_rolling\_mae\_mw`, les observations réelles et les prévisions dans Grafana. |



Pour diagnostiquer un problème Docker :



```powershell

docker compose ps

docker compose logs -f api

```



Pour vérifier l'état de DVC :



```powershell

dvc status

```



Pour vérifier les branches Git :



```powershell

git branch --show-current

git status

```



Pour toute erreur persistante, consulter les logs du service concerné et vérifier les paramètres de l'environnement utilisé.



\---



\*\*Fin du guide de déploiement Energy Forecast MLOps.\*\*

