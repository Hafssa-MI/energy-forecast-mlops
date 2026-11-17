# Suivi des expériences avec MLflow

Le serveur MLflow est hébergé sur DagsHub. Chaque entraînement d'un modèle crée un **run**.
Les runs sont rangés par **expérience**, une par environnement :
`energy-dev`, `energy-staging` et `energy-prod`.

## Contenu d'un run

**Paramètres** (ce qu'on a choisi avant l'entraînement)
- famille du modèle (baseline, sarima, prophet, lstm_direct, lstm_recursive) et horizon
  (court terme = 24 h, long terme = 168 h)
- environnement actif et taille des jeux de données (train, val, test en heures)
- hyperparamètres propres au modèle : ordres et saisonnalité pour SARIMA, fenêtre pour Prophet,
  nombre d'unités, epochs, taille de lot et fenêtre d'entrée pour le LSTM

**Métriques** (ce qu'on a mesuré sur la période de test)
- MAE (erreur absolue moyenne, en MW), RMSE, MAPE (erreur relative en %)
- temps d'entraînement en secondes, nombre de prévisions évaluées (origines du backtest)

**Artefacts** (fichiers attachés au run)
- graphique de l'erreur selon l'horizon et exemple de prévision comparée au réel
- le dossier du modèle sauvegardé (« bundle »), utilisé ensuite par le registre et l'API

**Tags** (pour retrouver et reproduire un résultat)
- famille, type d'horizon (short/long), environnement
- identifiant du commit Git et date de fin des données

## Comment comparer deux modèles
Dans l'interface MLflow : cocher plusieurs runs, puis *Compare*. On filtre par horizon avec
`tags.kind = "short"` ou `"long"`. Le critère principal est la MAE sur la période de test.