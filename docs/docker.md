\# Déploiement Docker – Energy Forecast MLOps



\## 1. Présentation



Le projet utilise Docker Compose pour déployer trois services :



\- \*\*API FastAPI\*\* : expose les endpoints de prédiction et les métriques.

\- \*\*Prometheus\*\* : collecte les métriques de l'API.

\- \*\*Grafana\*\* : permet de visualiser les métriques.



Trois environnements sont prévus : dev, staging et prod.



La même image Docker de l'API est utilisée dans les trois environnements. Les différences sont définies par les fichiers Compose et les fichiers de configuration propres à chaque environnement.



\## 2. Différences entre les environnements



| Configuration | Dev | Staging | Prod |

|---|---|---|---|

| Image API | Construite localement | Image figée | Image figée |

| Code monté en volume | Oui | Non | Non |

| Rechargement automatique | Oui | Non | Non |

| Niveau des logs | DEBUG | INFO | INFO |

| Redémarrage | Aucun | unless-stopped | always |

| Healthcheck API | Non | Oui | Oui |

| Limites CPU/RAM | Aucune | Aucune | Oui |

| Alias MLflow | dev | staging | production |

| Port API | 8001 | 8002 | 8003 |

| Port Prometheus | 9091 | 9092 | 9093 |

| Port Grafana | 3001 | 3002 | 3003 |



\### Environnement DEV



L'environnement de développement permet de modifier le code sans reconstruire l'image à chaque modification.



Les répertoires `src/` et `api/` sont montés dans le conteneur et Uvicorn utilise `--reload`.



\### Environnement STAGING



L'environnement staging utilise une image figée, sans montage du code source. Il reproduit un environnement proche de la production.



Les conteneurs redémarrent automatiquement sauf en cas d'arrêt manuel. Un healthcheck vérifie la disponibilité de l'API.



\### Environnement PROD



L'environnement de production utilise également une image figée, sans montage du code source.



Il possède :

\- Une politique de redémarrage `always`.

\- Un healthcheck avec un délai initial de 90 secondes.

\- Des limites de ressources CPU et mémoire.



Les limites configurées sont :

\- API : 2 CPU et 3 Go de mémoire.

\- Prometheus : 0,5 CPU et 512 Mo de mémoire.

\- Grafana : 0,5 CPU et 512 Mo de mémoire.



\## 3. Prérequis



Avant de démarrer un environnement :



\- Docker Desktop doit être lancé.

\- Les fichiers de données doivent être présents dans `data/processed` (commande `dvc pull` si nécessaire).

\- Les fichiers de configuration doivent être renseignés dans `envs/`.

\- Les identifiants DagsHub doivent être configurés dans les fichiers `.env`.

\- L'alias MLflow correspondant doit exister pour les deux modèles :

&#x20; - `energy-forecaster-short`

&#x20; - `energy-forecaster-long`



Les fichiers `.env` contenant des informations sensibles ne doivent pas être ajoutés à Git.



\## 4. Démarrage de l'environnement DEV



Depuis la racine du projet :



```powershell

docker compose -p energy-dev --env-file envs/dev.env -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up -d --build

```



Cette commande construit l'image Docker de l'API et démarre les trois services.



\### Vérification des conteneurs



```powershell

docker compose -p energy-dev --env-file envs/dev.env -f docker/docker-compose.yml -f docker/docker-compose.dev.yml ps

```



\### Consultation des logs



```powershell

docker compose -p energy-dev --env-file envs/dev.env -f docker/docker-compose.yml -f docker/docker-compose.dev.yml logs -f api

```



Pour quitter l'affichage des logs : `Ctrl + C`.



\### Vérification de l'API



```powershell

curl.exe http://localhost:8001/health

```



\### Arrêt de l'environnement DEV



```powershell

docker compose -p energy-dev down

```



\## 5. Démarrage de l'environnement STAGING



Prérequis : les deux modèles doivent posséder l'alias `staging` dans MLflow.



\### Démarrage



```powershell

docker compose -p energy-staging --env-file envs/staging.env -f docker/docker-compose.yml -f docker/docker-compose.staging.yml up -d --build

```



\### Vérification



```powershell

docker compose -p energy-staging --env-file envs/staging.env -f docker/docker-compose.yml -f docker/docker-compose.staging.yml ps

```



\### Logs



```powershell

docker compose -p energy-staging --env-file envs/staging.env -f docker/docker-compose.yml -f docker/docker-compose.staging.yml logs -f api

```



\### Test de l'API



```powershell

curl.exe http://localhost:8002/health

```



\### Arrêt



```powershell

docker compose -p energy-staging down

```



\## 6. Démarrage de l'environnement PROD



Prérequis : les deux modèles doivent posséder l'alias `production` dans MLflow.



\### Démarrage



```powershell

docker compose -p energy-prod --env-file envs/prod.env -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d --build

```



\### Vérification



```powershell

docker compose -p energy-prod --env-file envs/prod.env -f docker/docker-compose.yml -f docker/docker-compose.prod.yml ps

```



\### Logs



```powershell

docker compose -p energy-prod --env-file envs/prod.env -f docker/docker-compose.yml -f docker/docker-compose.prod.yml logs -f api

```



\### Test de l'API



```powershell

curl.exe http://localhost:8003/health

```



\### Arrêt



```powershell

docker compose -p energy-prod down

```



\## 7. Ports utilisés



| Service | DEV | STAGING | PROD |

|---|---:|---:|---:|

| API FastAPI | 8001 | 8002 | 8003 |

| Prometheus | 9091 | 9092 | 9093 |

| Grafana | 3001 | 3002 | 3003 |



Les interfaces sont accessibles depuis le navigateur :



\- DEV : API `http://localhost:8001`, Prometheus `http://localhost:9091`, Grafana `http://localhost:3001`.

\- STAGING : API `http://localhost:8002`, Prometheus `http://localhost:9092`, Grafana `http://localhost:3002`.

\- PROD : API `http://localhost:8003`, Prometheus `http://localhost:9093`, Grafana `http://localhost:3003`.



\## 8. Validation de la configuration



Avant de démarrer un environnement, il est possible de vérifier la syntaxe de sa configuration Compose avec `config`.



Exemple pour DEV :



```powershell

docker compose -p energy-dev --env-file envs/dev.env -f docker/docker-compose.yml -f docker/docker-compose.dev.yml config --quiet

```



Exemple pour STAGING :



```powershell

docker compose -p energy-staging --env-file envs/staging.env -f docker/docker-compose.yml -f docker/docker-compose.staging.yml config --quiet

```



Exemple pour PROD :



```powershell

docker compose -p t --env-file envs/prod.env -f docker/docker-compose.yml -f docker/docker-compose.prod.yml config

```



La validation de la configuration ne garantit pas que les modèles ou les services distants soient disponibles. Les alias correspondants doivent exister avant le démarrage réel.



\## 9. Exécution simultanée



Chaque environnement possède un nom de projet Docker Compose différent :



\- `energy-dev`

\- `energy-staging`

\- `energy-prod`



Les ports sont également différents. Il est donc possible de faire fonctionner les trois environnements simultanément, sous réserve que les ressources de la machine soient suffisantes et que les alias MLflow soient disponibles.



\## 10. Résultat de validation DEV



L'environnement DEV a été démarré et testé avec succès.



La commande `docker compose ps` a confirmé que les trois conteneurs étaient actifs :



\- `energy-dev-api-1`

\- `energy-dev-prometheus-1`

\- `energy-dev-grafana-1`



Les logs ont confirmé le chargement des deux modèles MLflow :

\- `energy-forecaster-short`, version 1, alias `dev`.

\- `energy-forecaster-long`, version 1, alias `dev`.



Le test de santé a retourné :



```json

{

&#x20; "status": "ok",

&#x20; "env": "dev",

&#x20; "alias": "dev",

&#x20; "models\_loaded": \["short", "long"]

}

```



Enfin, les trois conteneurs et le réseau de l'environnement DEV ont été arrêtés et supprimés avec succès à l'aide de `docker compose down`.



