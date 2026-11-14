# Résultats en environnement dev

Configuration légère (120 jours d'entraînement, 8 prévisions évaluées par modèle).
Ces chiffres valident la chaîne technique, pas les performances réelles.

| Modèle | Horizon | MAE (MW) | RMSE | MAPE (%) |
|---|---|---|---|---|
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