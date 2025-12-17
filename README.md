# Metal Mining - Data Analysis Project

**Le Projet Metal Mining** est un projet dédié à l’analyse des paroles de musique metal à grande échelle.

L’objectif est d’examiner le vocabulaire, les thèmes, les émotions et les évolutions stylistiques du metal à travers un corpus de chansons suffisamment large et représentatif.

Le projet s’inscrit dans une démarche exploratoire : comprendre ce que les paroles révèlent du genre, comment elles varient selon les groupes ou les époques, et quelles tendances apparaissent lorsqu’on applique des méthodes d’analyse textuelle.

L’ensemble du travail repose sur la mise en place d’un pipeline complet allant de la collecte des textes jusqu’à la production de visualisations et d’indicateurs linguistiques.

# Collecte des données (Scraping)

La première étape du projet a consisté à constituer un dataset de paroles de chansons metal. Deux sources de données ont été utilisées : **DarkLyrics** pour les paroles et **Metal Archives** pour les métadonnées de genre.

## 1. Scraping des paroles via DarkLyrics

Le scraping principal repose sur la bibliothèque Python `metalparser`, qui permet d'interroger le site DarkLyrics de manière automatisée.

Le script `scraper.py` implémente un système de **scraping distribué** permettant à plusieurs utilisateurs de travailler en parallèle sur différentes portions du dataset :

- La liste complète des artistes est divisée en **4 quartiers** (quarters), chacun assigné à un utilisateur différent.
- Chaque utilisateur exécute le script avec son nom (`--user Florent`, `--user Nizar`, etc.) et ne traite que sa portion assignée.
- Un système de **sauvegarde progressive** enregistre l'état d'avancement après chaque artiste traité, permettant de reprendre le scraping en cas d'interruption.

Pour chaque artiste, le script récupère :
- les paroles de chaque chanson,
- les titres,
- les albums,
- les années de sortie,
- le type de publication (album, EP, démo),
- le numéro de piste.

Les fichiers de progression individuels (`progress1.json`, `progress2.json`, etc.) sont ensuite fusionnés via `merge_progress_files.py` pour constituer le fichier final `dataset.json`.

## 2. Scraping des genres via Metal Archives

Pour enrichir le dataset avec les genres musicaux de chaque groupe, un second script (`metallum_webscraper.py`) interroge le site **Metal Archives** (Encyclopaedia Metallum).

Ce scraping utilise **Selenium** avec un navigateur Chrome automatisé pour contourner les protections anti-bot du site :

- Le script applique des techniques de **stealth** (masquage des propriétés `webdriver`, user-agent personnalisé, etc.).
- Pour chaque groupe, il accède à sa page dédiée et extrait le genre depuis la section `#band_stats`.
- Un délai configurable entre les requêtes permet de respecter les limites du serveur.

Les genres récupérés sont sauvegardés dans `data/bands_genres.json`, puis nettoyés via `clean_genres.py` pour produire `bands_genres_cleaned.json`.

## 3. Fusion et enrichissement des données

Les fichiers de progression sont fusionnés via `merge_progress_files.py`, qui ajoute également une **détection automatique de la langue** pour chaque chanson (via la bibliothèque `langdetect`).

Le dataset final (`data/dataset.json`) contient pour chaque chanson :
- Artiste, album, titre
- Paroles complètes
- Année de sortie et type de publication
- Langue détectée automatiquement

Ce fichier constitue la base pour toutes les étapes d'analyse.

# I Analyse descriptive du corpus

## 1- Présence des paroles et structure du dataset

Avant de commencer les analyses textuelles, nous avons évalué la complétude du dataset.

La très grande majorité des titres disposent de leurs paroles, ce qui garantit la fiabilité des mesures linguistiques qui suivront. La structuration des publications montre également une prédominance nette des albums, tandis que les EP et les démos restent minoritaires.

![image.png](attachment:11f1a84d-dca2-4039-98f4-f882fa4d461d:image.png)

![image.png](attachment:340d1107-99cb-4430-b8c3-9b5ec5e4c30f:image.png)

Ces premiers résultats confirment que le corpus est suffisamment riche et cohérent pour mener l’ensemble des analyses prévues.

### 2. Répartition des artistes et des albums

Nous avons ensuite étudié la distribution du corpus par artiste et par album afin d’identifier les groupes les plus représentés.

![image.png](attachment:c45e053b-a081-42dc-9ef8-504789d4467a:image.png)

![image.png](attachment:1c98e75c-8de5-498b-be18-67ee9b4497ef:image.png)

Les artistes comme **Judas Priest**, **Alice Cooper**, **Rage**, **Motörhead** ou **Napalm Death** apparaissent comme particulièrement prolifiques, ce qui reflète leur longévité et l’importance de leur discographie dans l’histoire du metal.

## 3. Évolution temporelle de la production

L’analyse par année de sortie montre une croissance progressive du nombre de chansons depuis la fin des années 1970, suivie d’un pic majeur entre les années 2000 et 2015.

Cette dynamique correspond à l’expansion des sous-genres metal et à l’essor des plateformes de diffusion numérique.

![image.png](attachment:32f22caf-3ee4-435d-834c-47af9fc63c2f:image.png)

## 4. Répartition des langues

La majorité des chansons du corpus sont en anglais, ce qui est cohérent avec la place centrale de cette langue dans la scène metal internationale. La catégorie « Unknown » (6,2 %) regroupe surtout des titres dont la langue n’a pas pu être déterminée automatiquement, souvent faute d’informations suffisantes.

Les autres langues présentes — comme l’allemand, l’espagnol ou le finnois — apparaissent en proportions réduites mais témoignent de l’activité de plusieurs scènes nationales, notamment en Europe.

![image.png](attachment:c9568806-01a2-44dd-8e31-df893e6f1c3c:image.png)

![image.png](attachment:eb16a238-4182-4d23-b8a2-b0f51bfe2d89:90a25ecb-58aa-4415-b580-57d653235dfb.png)

# II Analyse linguistique et stylistique du metal

L’analyse linguistique repose sur quatre indicateurs complémentaires permettant de caractériser le langage et le style des paroles.

1. **Swear word ratio**
    
    Proportion de mots vulgaires dans une chanson.
    
    Il met en évidence l’usage d’un registre agressif, direct ou provocateur.
    
2. **Coleman–Liau Readability Index**
    
    Indice de lisibilité basé sur la longueur moyenne des mots et des phrases.
    
    Un score élevé indique des paroles plus complexes et structurées.
    
    ![image.png](attachment:90f2ec1e-672f-4427-9d93-8667ec1b3b0d:image.png)
    
3. **Proportion de “stupid songs”**
    
    Catégorie issue du jeu de données de référence, regroupant les morceaux considérés comme très simples ou basiques dans leur écriture.
    
    Elle permet d’identifier les chansons dont le contenu textuel est minimal ou très peu développé.
    
4. **Metalness**
    
    La métrique de Metalness est une mesure normalisée qui évalue à quel point un mot est spécifique au corpus "Metal" par rapport au corpus "Non-Metal".
    
    Elle repose sur la comparaison des fréquences d'apparition des mots dans les deux jeux de données. On expliquera les détails de calcul de cetter métrique dans  [6. Metalness](https://www.notion.so/6-Metalness-2cc87cb0143d806b8548e25e7f88a518?pvs=21) 
    

Ces quatre mesures constituent la base de l’analyse linguistique et stylistique du corpus.

## **1. Vulgarité et complexité : deux dimensions sans lien direct**

Le nuage de points montre que le swear word ratio et l’indice de lisibilité n’évoluent pas ensemble.

On observe des artistes très vulgaires avec des paroles relativement structurées, d’autres très simples avec peu ou pas de vulgarité, et une majorité regroupée dans une zone intermédiaire.

![image.png](attachment:dcbb4b14-4260-4e80-8e51-6e607ab2677c:image.png)

Dans notre corpus, les valeurs élevées du Coleman–Liau ne décrivent pas une véritable complexité littéraire : elles correspondent plutôt à une écriture légèrement plus dense, souvent équivalente à un niveau scolaire situé entre **fin de collège et début de lycée**.

Autrement dit, les textes “les plus complexes” du dataset restent accessibles, mais ils comportent davantage de mots par phrase ou un vocabulaire un peu plus développé.

Cette observation confirme que la vulgarité n’est pas un indicateur de la qualité ou du niveau d’écriture : elle relève d’un choix stylistique propre à certains sous-genres extrêmes.

## **2. Les extrêmes du spectre linguistique**

![image.png](attachment:4f9f4a7b-9436-4210-853d-a05290503f3c:82acaf95-2cad-49a5-925f-6befcb2b22e2.png)

Les résultats montrent deux profils opposés.

Les swear word ratios les plus élevés se retrouvent chez des groupes comme *Meat Shits*, *Anal Cunt* ou *Barbatos*, caractérisés par des textes très directs et une structure simple.

À l’inverse, les scores de lisibilité les plus élevés  apparaissent chez *Cynic*, *Dissection*, *Botanist* ou *Dark Tranquillity*, dont les paroles présentent en moyenne des phrases plus longues et un vocabulaire plus varié.

## **3. Évolution du swear word ratio**

![image.png](attachment:84a24bf5-4c6f-4a8c-bff4-70bca6a9a59a:image.png)

L’évolution du swear word ratio présente une dynamique claire. On observe une progression régulière entre la fin des années 1970 et le milieu des années 1990, période correspondant à l’apparition et à la structuration de plusieurs sous-genres caractérisés par un registre plus vulgaire.

À partir des années 2000, les valeurs se stabilisent autour d’un niveau constant, sans tendance à la hausse ou à la baisse.

Ces résultats indiquent que l’usage de termes vulgaires s’est installé comme une caractéristique propre à certains segments du genre, tout en restant stable à l’échelle du corpus global.

## **4. Tendances générales de lisibilité et de simplicité textuelle**

![image.png](attachment:7c8276d0-bcc4-4a37-a17e-d91d954a486b:image.png)

L’indice de lisibilité présente une légère augmentation au fil du temps. Les valeurs restent globalement compatibles avec un niveau situé entre le collège et le début du lycée, ce qui indique que les textes ne deviennent pas réellement complexes, mais montrent une tendance à des phrases un peu plus longues et un vocabulaire légèrement plus varié.

L’évolution observée correspond donc à un enrichissement modéré plutôt qu’à un changement structurel important.

![image.png](attachment:f7187c57-8fef-4c60-b385-09bd2e20af0a:image.png)

La relation entre le swear word ratio et la proportion de “stupid songs” met en évidence un comportement global du corpus : les artistes affichant un ratio d’insultes plus élevé ont également une fréquence plus importante de morceaux caractérisés par un texte minimal ou très court.

Cette association indique que la densité lexicale varie sensiblement d’un artiste à l’autre. La dispersion des valeurs montre une répartition continue, sans distinction nette ou clusters stricts, ce qui reflète une diversité de pratiques d’écriture plutôt qu’une séparation en catégories définies.

## 5. Nuage de mots

## 6. Metalness

### A. Prétraitement et Filtrage

Avant le calcul, deux filtres sont appliqués pour réduire le bruit statistique :

- **Seuil de fréquence :** Seuls les mots apparaissant au moins **5 fois** dans chaque corpus sont conservés (`v >= 5`). Cela élimine les mots trop rares qui fausseraient les ratios.
- **Intersection et Longueur :** Le calcul ne s'effectue que sur les mots présents dans les **deux** corpus (`intersection`) et possédant plus de 2 lettres, afin d'exclure les mots de liaison trop courts et non significatifs.

### B. Formulation Mathématique

Le score est calculé en deux étapes pour chaque mot w : le calcul du coefficient logarithmique, puis sa normalisation.

**a. Le coefficient de Metalness (Log-Ratio)**
Le code calcule d'abord le logarithme du rapport des fréquences brutes entre les deux corpus. Soit fmetal(w) la fréquence du mot dans le corpus Metal et fnon_metal(w) sa fréquence dans le corpus Non-Metal :

$$
coeff(w) = ln(\frac{f_{nonmetal}(w)}{f_{metal}(w)})
$$

- Si le mot est plus fréquent dans le Metal, coeff>0.
- Si le mot est plus fréquent dans le Non-Metal, coeff<0.

**b. La "Metalness" (Transformation Sigmoïde)**
Pour obtenir un score lisible et borné, on applique une fonction **sigmoïde** au coefficient. Cela transforme la valeur (qui va de −∞ à +∞) en une probabilité comprise entre 

$$
Metalness(w) = \frac{1}{1 + e^{-coeff(w)}}
$$

### C. Interprétation des scores

Si le score d’un mot est : 

- Proche de 1 : Le mot est fortement caractéristique du **Metal**
- Proche de 0 : Le mot est fortement caractéristique du genre **Non Metal**
- Autour de 0.5 : Le mot est neutre

---

# Crédits et outils utilisés

Ce projet a été réalisé dans le cadre du *Projet d'Approfondissement et d'Ouverture* (PAO) à l'INSA Rouen.

**Bibliothèques et outils :**
- `metalparser` (Luca Ballore) pour le scraping de DarkLyrics
- `Selenium` pour l'automatisation du navigateur (Metal Archives)
- `langdetect` pour la détection automatique des langues
- Stack Python data science : `pandas`, `numpy`, `matplotlib`, `seaborn`
- `scikit-learn` pour les analyses TF-IDF et le clustering