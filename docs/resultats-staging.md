\# Résultats de l'entraînement final – Staging



\## 1. Informations générales



\- \*\*Date :\*\* 18 novembre 2026

\- \*\*Environnement :\*\* staging

\- \*\*Branche Git :\*\* `feature/staging-training`

\- \*\*Commit de départ :\*\* `4ef328c`

\- \*\*Commit d'activation staging :\*\* `00dc3c8`

\- \*\*Expérience MLflow :\*\* `energy-staging`

\- \*\*Durée approximative :\*\* 35 min 45 s

\- \*\*Commande exécutée :\*\* `dvc repro`



\## 2. Configuration matérielle



L'entraînement a été effectué sur la configuration suivante :



| Composant | Configuration |

|---|---|

| Processeur | Intel Core i7-1185G7, 11th Gen |

| Nombre de cœurs | 4 |

| Threads logiques | 8 |

| Mémoire RAM | 31,69 Go |



\## 3. Protocole expérimental



L'objectif est de réaliser un entraînement final des modèles dans l'environnement staging avec les hyperparamètres retenus pendant la phase de tuning.



Les modèles ont été entraînés sur l'historique d'entraînement complet disponible. La validation est utilisée pour comparer les modèles et sélectionner le meilleur selon la métrique MAE (`val\_mae`).



Le jeu de test est utilisé uniquement pour mesurer les performances finales. Les résultats du test ne sont pas utilisés pour modifier les hyperparamètres ni sélectionner les modèles.



Dix entraînements ont été exécutés :



\- Baseline : short et long.

\- SARIMA : short et long.

\- Prophet : short et long.

\- LSTM Direct : short et long.

\- LSTM Recursive : short et long.



Les étapes de préparation des données (`download`, `clean`, `split`) ont été ignorées par DVC car leurs résultats étaient déjà à jour.



\## 4. Résultats détaillés



Les métriques sont exprimées en MW pour MAE et RMSE, et en pourcentage pour MAPE.



| Modèle | Horizon | VAL MAE | VAL RMSE | VAL MAPE | Test MAE | Test RMSE | Test MAPE |

|---|---|---:|---:|---:|---:|---:|---:|

| Baseline | Short | 2630,82 | 4501,74 | 5,43 % | 1355,27 | 1824,87 | 2,65 % |

| Baseline | Long | 2758,23 | 4674,59 | 5,73 % | 1381,19 | 1865,47 | 2,69 % |

| SARIMA | Short | 3406,84 | 4591,30 | 6,83 % | 3335,54 | 4604,96 | 6,65 % |

| SARIMA | Long | 4624,64 | 5532,61 | 9,53 % | 4317,84 | 5425,92 | 8,74 % |

| Prophet | Short | 2539,61 | 3204,78 | 5,43 % | 2570,52 | 3266,68 | 5,19 % |

| Prophet | Long | 2546,65 | 3238,17 | 5,50 % | 2562,92 | 3251,32 | 5,16 % |

| LSTM Direct | Short | 1576,85 | 2256,68 | 3,30 % | 1229,89 | 1558,88 | 2,43 % |

| LSTM Direct | Long | 3092,24 | 4368,70 | 6,71 % | 2200,40 | 2714,76 | 4,55 % |

| LSTM Recursive | Short | 1263,65 | 1760,81 | 2,61 % | 1037,31 | 1324,32 | 2,07 % |

| LSTM Recursive | Long | 2295,59 | 2927,38 | 4,85 % | 1679,56 | 2078,03 | 3,43 % |



\## 5. Sélection des meilleurs modèles



La sélection est réalisée à partir du MAE de validation (`val\_mae`).



\### Horizon Short



Le modèle LSTM Recursive obtient le meilleur MAE de validation avec 1263,65 MW.



Sur le test, son MAE est de 1037,31 MW contre 1355,27 MW pour la baseline.



Il réduit donc l'erreur absolue moyenne de test d'environ 23,5 % par rapport à la baseline.



\### Horizon Long



Le modèle LSTM Recursive obtient également le meilleur MAE de validation avec 2295,59 MW.



Cependant, son MAE de test atteint 1679,56 MW, contre 1381,19 MW pour la baseline.



La baseline est donc meilleure sur le test pour cet horizon. L'écart correspond à une erreur supérieure d'environ 21,6 % pour le LSTM Recursive.



Cette différence montre que le meilleur modèle en validation n'est pas nécessairement le meilleur sur le jeu de test.



\## 6. Analyse générale



Les résultats montrent que les modèles LSTM sont globalement compétitifs, particulièrement pour l'horizon short.



Le LSTM Recursive obtient les meilleurs résultats de validation sur les deux horizons. Il présente également les meilleurs résultats de test pour l'horizon short.



Pour l'horizon long, la baseline conserve de meilleures performances sur le test. Ce résultat doit être pris en compte avant toute décision de déploiement.



SARIMA présente les erreurs les plus élevées parmi les modèles comparés sur les deux horizons. Prophet obtient des performances intermédiaires.



Les résultats doivent être interprétés en tenant compte de la séparation entre validation et test. Le jeu de test n'a pas servi à choisir les hyperparamètres.



\## 7. Limites et précautions



Plusieurs limites doivent être prises en compte :



\- Les données concernent un seul pays.

\- Les variables météorologiques, notamment la température, ne sont pas intégrées.

\- Le jeu de test couvre une période d'environ une année.

\- Les performances peuvent varier selon les périodes et les conditions du système énergétique.

\- L'early stopping des modèles LSTM utilise les performances de validation ; celles-ci ne constituent donc pas une mesure totalement indépendante.



Une évaluation complémentaire sur plusieurs périodes et avec des variables exogènes pourrait améliorer l'analyse.



\## 8. Traçabilité et reproductibilité



L'expérience finale est enregistrée dans MLflow sous le nom `energy-staging`.



Les dix exécutions sont disponibles dans cette expérience, avec leurs métriques et leurs informations de suivi.



Le pipeline est géré par DVC. Le fichier `dvc.lock` conserve les informations relatives aux stages et aux dépendances utilisées.



\- \*\*Commit de départ :\*\* `4ef328c`

\- \*\*Commit d'activation de staging :\*\* `00dc3c8`

\- \*\*Commande de reproduction :\*\* `dvc repro`

\- \*\*Expérience MLflow :\*\* `energy-staging`



Après validation, les changements de `dvc.lock` et les métriques seront versionnés avec Git et les artefacts seront envoyés vers le stockage distant avec `dvc push`.



\## 9. Conclusion



L'entraînement final en staging des dix configurations de modèles a été réalisé avec succès.



Le LSTM Recursive est sélectionné selon la validation pour les horizons short et long. Toutefois, les résultats de test montrent qu'il améliore la baseline uniquement pour l'horizon short.



Pour l'horizon long, la baseline reste plus performante sur le test. Cette distinction est importante pour une décision de promotion vers la production.



Les résultats, les métriques et les artefacts sont conservés afin de garantir la traçabilité et la reproductibilité de cette expérimentation.

