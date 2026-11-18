\# Procédures de retour arrière (Rollback)



\## 1. Objectif



Ce document décrit les procédures à suivre pour revenir à une version stable du système Energy Forecast MLOps lorsqu'un problème apparaît après une mise à jour.



Le retour arrière peut concerner :

\- Le modèle MLflow.

\- Le code source.

\- L'image Docker.



L'objectif est de rétablir rapidement un fonctionnement stable sans perdre la traçabilité des modifications.



\## 2. Retour arrière du modèle MLflow



Le registre MLflow contient les modèles :

\- `energy-forecaster-short`

\- `energy-forecaster-long`



Les alias permettent d'identifier les versions utilisées dans chaque environnement :

\- `dev`

\- `staging`

\- `production`



\### Procédure



1\. Ouvrir le registre MLflow sur DagsHub.

2\. Identifier le modèle concerné.

3\. Consulter les versions disponibles.

4\. Identifier la dernière version stable.

5\. Réaffecter l'alias de l'environnement à cette version.

6\. Recharger les modèles dans l'API.



Exemple pour l'environnement DEV :



```powershell

Invoke-RestMethod -Method Post http://localhost:8001/reload

```



Vérifier les modèles chargés :



```powershell

Invoke-RestMethod http://localhost:8001/model-info

```



Pour STAGING et PROD, utiliser respectivement les ports API `8002` et `8003`.



\## 3. Retour arrière du code source avec Git



Lorsqu'une modification du code provoque une régression, il est possible d'annuler le commit concerné avec `git revert`.



\### Identifier le commit



```powershell

git log --oneline

```



\### Annuler la modification



```powershell

git revert <commit\_id>

```



Remplacer `<commit\_id>` par l'identifiant du commit à annuler.



\### Envoyer le retour arrière



```powershell

git push

```



Cette méthode crée un nouveau commit qui annule les modifications précédentes sans supprimer l'historique Git.



Pour les branches protégées, effectuer le retour arrière via une branche dédiée et une Pull Request.



\## 4. Retour arrière de l'image Docker



Lorsqu'une nouvelle image Docker provoque un dysfonctionnement, il faut revenir à une image précédente connue comme stable.



\### Procédure



1\. Identifier le tag de l'image actuellement déployée.

2\. Identifier le tag précédent correspondant à une version stable.

3\. Modifier la configuration Docker pour utiliser ce tag.

4\. Redémarrer les services concernés.

5\. Vérifier l'état des conteneurs.

6\. Tester l'API et les modèles chargés.



Vérifier les conteneurs :



```powershell

docker compose ps

```



Consulter les logs :



```powershell

docker compose logs -f api

```



La disponibilité d'une ancienne image dépend de sa conservation dans le registre Docker.



\## 5. Vérifications après rollback



Après chaque opération de retour arrière :



\- Vérifier que les conteneurs sont actifs.

\- Vérifier que l'API répond correctement.

\- Vérifier les versions des modèles chargés.

\- Vérifier les métriques exposées.

\- Contrôler Prometheus et Grafana.



Exemple de vérification de santé pour DEV :



```powershell

curl.exe http://localhost:8001/health

```



Vérifier les métriques :



```powershell

curl.exe http://localhost:8001/metrics

```



\## 6. Conclusion



Les procédures de rollback permettent de rétablir une version stable du système en cas de problème.



Le registre MLflow permet de revenir à une version précédente du modèle, Git permet d'annuler une modification du code et Docker permet de redéployer une image stable conservée précédemment.

