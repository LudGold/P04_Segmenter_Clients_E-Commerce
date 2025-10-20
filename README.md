# Projet de Segmentation Client RFM

## 1. Contexte et Objectif

L’objectif de ce projet est de **segmenter la base de clients** d’une entreprise e-commerce à partir de leurs données transactionnelles.  
L’enjeu : **transformer les données brutes** en segments de clients exploitables afin de :
- Personnaliser les actions marketing  
- Améliorer la rétention et la satisfaction client  

Pour cela, nous avons mis en place une **analyse RFM** (*Récence, Fréquence, Monétaire*) suivie d’un algorithme de **clustering non supervisé**.

---

## 2. Jeu de Données

Les données proviennent du **dataset public [Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)**.  
L’analyse porte sur :
- **112 650 commandes**
- **93 358 clients uniques**

---

## 3. Méthodologie et Étapes du Projet

Le projet s’articule autour de **5 grandes étapes** :

1. **Construction du fichier client** en SQL (jointures et agrégations des tables `orders`, `customers`, `order_items`…)
2. **Analyse exploratoire** (EDA) pour identifier la distribution et la dispersion des variables R, F, M  
3. **Préprocessing** :
   - Transformation logarithmique  
   - Standardisation des données  
4. **Clustering non supervisé** :
   - Test de deux modèles : `K-Means` et `DBSCAN`
   - Sélection du modèle optimal selon le **score de silhouette** et la **méthode du coude**
5. **Profiling et interprétation des segments**

---

## 4. Choix des Méthodes

###  Analyse RFM
L’analyse RFM est un **standard marketing** simple et efficace pour qualifier le comportement d’achat des clients.

### Transformation Logarithmique
Étape indispensable : sans cette normalisation, les clients aux dépenses extrêmes auraient biaisé le clustering basé sur la distance.

### Modèles testés
| Modèle | Particularité | Résultat |
|:--------|:---------------|:----------|
| **K-Means** | Nécessite un choix de *k* (nombre de clusters) via méthode du coude et silhouette | ✅ Retenu – segmentation équilibrée et interprétable |
| **DBSCAN** | Ne demande pas de *k*, mais sensible aux paramètres `eps` et `min_samples` | ❌ Trop de bruit, peu de structure exploitable |

---

## 5. Modèle Final Retenu

### **K-Means (k=4)**
Ce modèle a produit les **segments les plus équilibrés, stables et interprétables** :
- Clusters directement actionnables par les équipes marketing
- Bonne séparation R, F, M
- Silhouette score satisfaisant (≈ 0.39)

###  Test d’une variable supplémentaire : `review_score`
Un réentraînement a été réalisé avec la variable de satisfaction client.  
→ Résultat : **score de silhouette amélioré (0.64)** mais **perte de granularité** (2 clusters au lieu de 4).  
Le modèle RFM seul a donc été conservé pour sa richesse interprétative.

---

## 6. Résultats et Interprétation

| Segment | Profil client | Action marketing possible |
|:--------|:----------------|:---------------------------|
| **0 – Clients perdus** | anciens, peu actifs, faible dépense | relance / réactivation |
| **1 – Clients à risque** | achat passé, fréquence faible | offres ciblées |
| **2 – Nouveaux clients** | récents, panier moyen correct | fidélisation |
| **3 – Clients dormants** | anciens bons clients mais inactifs | campagnes de retour |

Les **segments sont directement exploitables** pour cibler les actions marketing selon le cycle de vie client.

---

## 7. Exécution du Projet

### Installation
```bash
pip install -r requirements.txt

    
