
### Résultats (MAE de validation, en MW, environ 20 prévisions par score)

| Modèle        | Meilleur réglage                               | 24 h      | 168 h     |
|---------------|------------------------------------------------|-----------|-----------|
| LSTM récursif | Fenêtre 336, 32 unités                         | **1 126** | Non réglé |
| LSTM direct   | 24 h : 336 / 32 ; 168 h : 168 / 64             | 1 442     | 2 849     |
| Prophet       | Toutes les données (`window_days: null`)       | 2 682     | **2 574** |
| SARIMA        | Fenêtre 42 j ; (1,0,1) à 24 h, (2,0,1) à 168 h | 3 438     | 4 657     |

### Protocole et limites

- **Protocole d'évaluation :** Les résultats sont calculés uniquement sur l'ensemble de validation. Une prévision est effectuée tous les trois jours. L'ensemble de test n'a pas été utilisé durant cette comparaison.
- **LSTM récursif à 168 h :** Ce modèle n'a pas encore été réglé pour l'horizon de 168 heures. Une évaluation spécifique serait nécessaire pour déterminer ses performances sur cet horizon.
- **Limite de l'évaluation :** Les modèles LSTM utilisent un arrêt anticipé (*Early Stopping*) basé sur les performances de validation. Cela peut rendre les scores légèrement optimistes, puisque cet ensemble intervient également dans le choix de la meilleure époque d'entraînement.
