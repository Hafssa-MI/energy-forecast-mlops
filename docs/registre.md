# Registre des modèles MLflow et promotion

## 1. Présentation

Le registre MLflow permet de centraliser les modèles entraînés, de suivre leurs versions et de gérer leur cycle de vie entre les différents environnements.

Dans ce projet, deux modèles sont enregistrés :

- `energy-forecaster-short` : prévision à court horizon.
- `energy-forecaster-long` : prévision à long horizon.

## 2. Gestion des alias

Chaque modèle peut être associé à un alias qui indique son environnement :

| Alias | Environnement | Description |
|---|---|---|
| `dev` | Développement | Modèle en cours de développement et de validation |
| `staging` | Préproduction | Modèle candidat avant la mise en production |
| `production` | Production | Modèle validé pour une utilisation en production |

Les alias permettent de désigner une version précise d'un modèle sans devoir utiliser directement son numéro de version.

## 3. Commandes de promotion

Le script `src/promote.py` permet de promouvoir les modèles selon l'environnement cible.

```bash
python src/promote.py --env dev
python src/promote.py --env staging
python src/promote.py --env prod
```

Le script sélectionne le meilleur candidat à partir de la métrique `val_mae` et met à jour l'alias correspondant dans le registre MLflow.

## 4. Règle de promotion de 2 %

Une nouvelle version n'est promue que si son `val_mae` est inférieur d'au moins 2 % à celui du modèle actuellement associé à l'alias cible.

Cette règle évite de remplacer un modèle existant par une nouvelle version qui n'apporte pas une amélioration suffisamment importante.

Si aucun modèle n'existe encore pour l'alias, le premier candidat peut être enregistré.

## 5. Choix de la métrique val_mae

La métrique `val_mae` (Mean Absolute Error sur les données de validation) est utilisée pour comparer et sélectionner les modèles.

La métrique de test (`mae`) n'est pas utilisée pour la promotion, car les données de test doivent rester indépendantes de la sélection et servir à l'évaluation finale des performances.

Cette séparation permet d'éviter les biais liés à l'utilisation des données de test pendant la sélection des modèles.

## 6. Conclusion

Le registre MLflow assure le suivi des versions des modèles et facilite leur promotion entre les environnements de développement, de préproduction et de production. La règle d'amélioration de 2 % et l'utilisation de `val_mae` contribuent à rendre le processus de promotion plus fiable.