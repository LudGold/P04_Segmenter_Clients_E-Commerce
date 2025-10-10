Projet de Segmentation Client RFM
1. Contexte et Objectif
L'objectif de ce projet est de segmenter la base de clients d'une entreprise e-commerce en utilisant leurs données transactionnelles. L'enjeu est de transformer des données brutes en segments de clients actionnables, permettant ainsi de personnaliser les actions marketing et d'améliorer la rétention.

Pour cela, nous utiliserons une analyse RFM (Récence, Fréquence, Monétaire) suivie d'un algorithme de clustering non supervisé pour regrouper les clients aux comportements similaires.

2. Le Dataset
la source provenant d'un dataset public nommé Olistdb.db, l'analyse se porte sur 112650 articles commmandés par 93358 clients.

3. Méthodologie et étapes du projet
Le projet s'st articiculé autour de 5 étapes : la construction du fichier client (sql), l'analyse exploratoire des données, le préprocessing avec la transformation logarithmique et la standardisation des données, puis le clustering
où sont testés 2 modèles : k-means et DbScan puis le choix du modele et enfin le profiling et interprétation des résultats.

4. Choix des méthodes utilisées
Choix de l'Analyse RFM : L'approche RFM a été choisie car c'est un standard de l'industrie du marketing, simple à calculer et très efficace pour qualifier le comportement d'achat des clients.
Choix de la Transformation Logarithmique : Cette étape était indispensable. Sans elle, les algorithmes de clustering (basés sur la distance) auraient été biaisés par les quelques clients aux valeurs monétaires ou de fréquence extrêmes.
Le graphique k-distance de DBSCAN a d'ailleurs confirmé que sans cette transformation, la structure des données était inutilisable.
Comparaison K-Means vs. DBSCAN : K-Means a nécessité de choisir et de tester un nombre de clusters k (déterminé via la méthode du coude et le score de silhouette).
DBSCAN, quant à lui, a montré qu'avec les paramètres choisis, une grande partie de nos clients étaient considérés comme du bruit, rendant la segmentation moins pertinente pour un objectif marketing global.

Modèle Final Retenu : K-Means
Le modèle K-Means (avec k=4) a été retenu car il a produit les segments les plus équilibrés, interprétables et directement actionnables d'un point de vue business.
Ce modèle a été ensuite reentrainer avec une nouvelle feature (review_score) mais son impact s'est revélé plutôt négatif : 2 clusterings, peu de variance donc aplanit les différences R, F, M

5. Résultats et interpretation
4 types de segments retenus dont le profil est le suivant : clients perdus, clients à risque, nouveaux clients, et clients dormants pouvant être utilisés directement par les équipes marketing

6. Execution du projet :
pip install -r requirements.txt (fichier à la racine du projet)
Exécution : Ouvrez et exécutez le notebook Jupyter nom_du_notebook.ipynb cellule par cellule. Le fichier de segmentation final sera généré à la racine du projet.
    
