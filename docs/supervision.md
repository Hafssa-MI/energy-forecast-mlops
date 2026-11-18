# Supervision et procédure de réentraînement

## 1. Objectif

La supervision permet de surveiller la qualité des prédictions du système Energy Forecast et de détecter une éventuelle dérive entre les consommations prédites et les consommations réelles.

Prometheus collecte les métriques exposées par l'API FastAPI. Grafana permet de visualiser l'évolution de ces métriques.

## 2. Métrique surveillée

La métrique principale utilisée pour surveiller la qualité des prédictions est :

`forecast_rolling_mae_mw`

Elle représente la MAE glissante (Mean Absolute Error) en MW.

Deux horizons sont surveillés :
- `short` : prévisions à court terme (24 heures).
- `long` : prévisions à long terme (168 heures).

La métrique est mise à jour lorsque les observations réelles sont reçues et comparées aux prévisions correspondantes.

## 3. Configuration de l'alerte Prometheus

L'alerte `ForecastErrorHigh` est définie dans `monitoring/alerts.yml`.

```yaml
groups:
  - name: forecast-quality
    rules:
      - alert: ForecastErrorHigh
        expr: forecast_rolling_mae_mw{kind="short"} > 2000
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "MAE glissante court terme > 2000 MW : envisager un réentraînement"
```

Le seuil retenu est de 2000 MW. Il correspond à environ 1,78 fois la MAE de validation de 1126 MW du meilleur modèle court terme retenu lors du tuning en staging.

L'alerte passe à l'état `FIRING` lorsque la MAE court terme dépasse 2000 MW pendant au moins deux minutes.

## 4. Simulation d'une dérive

Pour tester le mécanisme de supervision, le flux de production simulé est envoyé à l'API avec une perturbation artificielle.

Commande utilisée sous PowerShell :

```powershell
python monitoring\simulate_stream.py --shock-from 10 --shock 1.25 --delay 2
```

Paramètres :
- `--shock-from 10` : applique la perturbation à partir du 11e jour.
- `--shock 1.25` : augmente artificiellement les valeurs de consommation de 25 %.
- `--delay 2` : attend deux secondes entre deux jours simulés.

La simulation porte sur 30 jours de données.

## 5. Vérification de l'alerte

L'alerte est consultable dans Prometheus :

http://localhost:9091/alerts

La métrique peut être vérifiée directement depuis l'API :

```powershell
(Invoke-WebRequest -UseBasicParsing http://localhost:8001/metrics).Content -split "`n" | Select-String "forecast_rolling_mae_mw"
```

Lors du test réalisé :
- MAE court terme : 2210,90 MW.
- Seuil configuré : 2000 MW.
- État de l'alerte : `FIRING`.

L'alerte a donc été déclenchée avec succès.

## 6. Procédure de traitement d'une alerte

Lorsqu'une alerte `ForecastErrorHigh` est déclenchée, la procédure suivante doit être appliquée.

### Étape 1 : Analyser la dérive

- Consulter l'alerte dans Prometheus.
- Examiner l'évolution de la MAE dans Grafana.
- Vérifier les dernières observations reçues.
- Rechercher les changements de comportement dans les données de consommation.
- Déterminer si la dégradation est temporaire ou persistante.

### Étape 2 : Réentraîner en environnement DEV

- Utiliser les données disponibles dans l'environnement de développement.
- Lancer le processus de réentraînement et d'évaluation.
- Enregistrer les nouveaux runs dans l'expérience MLflow `energy-dev`.
- Conserver les paramètres, métriques et versions des modèles.

### Étape 3 : Comparer les modèles dans MLflow

Comparer le nouveau modèle avec le modèle actuellement utilisé.

Les critères de comparaison comprennent :
- La MAE sur les données de validation.
- Le type et la configuration du modèle.
- Les paramètres d'entraînement.
- La qualité des prévisions sur l'horizon court terme.

Le nouveau modèle doit présenter une amélioration d'au moins 2 % pour être candidat à la promotion.

### Étape 4 : Promouvoir le modèle

Utiliser le script `src/promote.py` pour effectuer la promotion du modèle lorsque le gain mesuré dépasse 2 %.

La promotion permet de remplacer le modèle actuellement utilisé par un modèle plus performant, selon la logique de promotion définie dans le projet.

### Étape 5 : Recharger les modèles de l'API

Après la promotion, demander à l'API de recharger les modèles :

```powershell
Invoke-RestMethod -Method Post http://localhost:8001/reload
```

Vérifier ensuite les versions actives :

```powershell
Invoke-RestMethod http://localhost:8001/model-info
```

Enfin, continuer à surveiller les métriques dans Prometheus et Grafana afin de vérifier le retour à une qualité de prédiction satisfaisante.

## 7. Conclusion

La supervision permet de détecter automatiquement une dégradation de la qualité des prévisions grâce à Prometheus.

La procédure de réentraînement permet ensuite d'analyser la dérive, de développer un meilleur modèle en DEV, de comparer les résultats dans MLflow et de promouvoir le modèle si le gain dépasse 2 %.

Le rechargement de l'API avec `/reload` permet de prendre en compte le nouveau modèle sans reconstruire toute l'application.