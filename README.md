**Le PAO Metal Mining** est un projet dédié à l’analyse des paroles de musique metal à grande échelle.

L’objectif est d’examiner le vocabulaire, les thèmes, les émotions et les évolutions stylistiques du metal à travers un corpus de chansons suffisamment large et représentatif.

Le projet s’inscrit dans une démarche exploratoire : comprendre ce que les paroles révèlent du genre, comment elles varient selon les groupes ou les époques, et quelles tendances apparaissent lorsqu’on applique des méthodes d’analyse textuelle.

L’ensemble du travail repose sur la mise en place d’un pipeline complet allant de la collecte des textes jusqu’à la production de visualisations et d’indicateurs linguistiques.

# **I Collecte des données (Scraping)**

La première étape du projet a consisté à constituer un dataset de paroles de chansons metal. Deux sources de données ont été utilisées : **DarkLyrics** pour les paroles et **Metal Archives** pour les métadonnées de genre.

**1. Scraping des paroles via DarkLyrics**

Le scraping principal repose sur la bibliothèque Python `metalparser`, qui permet d'interroger le site DarkLyrics de manière automatisée.

Le script `scraper.py` implémente un système de **scraping distribué** permettant à plusieurs utilisateurs de travailler en parallèle sur différentes portions du dataset :

- La liste complète des artistes est divisée en **4 quartiers** (quarters), chacun assigné à un utilisateur différent.
- Chaque utilisateur exécute le script avec son nom (`-user Florent`, `-user Nizar`, etc.) et ne traite que sa portion assignée.
- Un système de **sauvegarde progressive** enregistre l'état d'avancement après chaque artiste traité, permettant de reprendre le scraping en cas d'interruption.

Pour chaque artiste, le script récupère :

- les paroles de chaque chanson,
- les titres,
- les albums,
- les années de sortie,
- le type de publication (album, EP, démo),
- le numéro de piste.

Les fichiers de progression individuels (`progress1.json`, `progress2.json`, etc.) sont ensuite fusionnés via `merge_progress_files.py` pour constituer le fichier final `dataset.json`.

**2. Scraping des genres via Metal Archives**

Pour enrichir le dataset avec les genres musicaux de chaque groupe, un second script (`metallum_webscraper.py`) interroge le site **Metal Archives** (Encyclopaedia Metallum).

Ce scraping utilise **Selenium** avec un navigateur Chrome automatisé pour contourner les protections anti-bot du site :

- Le script applique des techniques de **stealth** (masquage des propriétés `webdriver`, user-agent personnalisé, etc.).
- Pour chaque groupe, il accède à sa page dédiée et extrait le genre depuis la section `#band_stats`.
- Un délai configurable entre les requêtes permet de respecter les limites du serveur.

Les genres récupérés sont sauvegardés dans `data/bands_genres.json`, puis nettoyés via `clean_genres.py` pour produire `bands_genres_cleaned.json`.

**3. Fusion et enrichissement des données**

Les fichiers de progression sont fusionnés via `merge_progress_files.py`, qui ajoute également une **détection automatique de la langue** pour chaque chanson (via la bibliothèque `langdetect`).

Le dataset final (`data/dataset.json`) contient pour chaque chanson :

- Artiste, album, titre
- Paroles complètes
- Année de sortie et type de publication
- Langue détectée automatiquement

Ce fichier constitue la base pour toutes les étapes d'analyse.

# II Analyse descriptive du corpus

## 1. Présence des paroles et structure du dataset

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

# III Analyse linguistique et stylistique du metal

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

   Elle repose sur la comparaison des fréquences d'apparition des mots dans les deux jeux de données. Les détails de calcul sont présentées dans [6. Metalness](https://www.notion.so/6-Metalness-2cc87cb0143d806b8548e25e7f88a518?pvs=21)

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

Les swear word ratios les plus élevés se retrouvent chez des groupes comme _Meat Shits_, _Anal Cunt_ ou _Barbatos_, caractérisés par des textes très directs et une structure simple.

À l’inverse, les scores de lisibilité les plus élevés apparaissent chez _Cynic_, _Dissection_, _Botanist_ ou _Dark Tranquillity_, dont les paroles présentent en moyenne des phrases plus longues et un vocabulaire plus varié.

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

## 5. **Analyse des fréquences lexicales par nuages de mots**

Dans une démarche exploratoire visant à identifier les thématiques prédominantes, nous avons calculé les occurrences des termes dans chaque corpus afin de générer des nuages de mots distincts. Cette visualisation permet de mettre en évidence une dichotomie sémantique frappante entre les deux genres.

Le nuage de mots du corpus **« Non-Metal »** révèle un vocabulaire majoritairement ancré dans les registres sentimentaux et les relations interpersonnelles. On y observe une prédominance nette de verbes et de noms communs liés aux émotions et au quotidien, avec des termes centraux tels que « love », « baby », « know », « never » ou « time ».

![non_metal_wordcloud.png](attachment:9deb84ea-832f-4f31-9b1c-09aa0ef98492:non_metal_wordcloud.png)

À l’opposé, la visualisation du corpus **« Metal »** expose un champ lexical radicalement plus sombre et agressif. Les mots les plus fréquents, qui apparaissent ici de manière massive, appartiennent au registre de la violence, de la mort et du conflit. Des termes comme « blood », « kill », « death », « war », « fire » et « hell » saturent l'espace visuel, confirmant ainsi la singularité thématique du genre Metal par rapport aux standards de la musique populaire généraliste.

![image.png](attachment:d6387b46-665d-4ffe-89c2-f6c3b990e077:image.png)

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

**Les 20 mots les plus métal selon la “metalness”**

![image.png](attachment:36cef1d1-ae7a-416e-8396-ad24e1d8ae3d:image.png)

## 7. Metallitude

Après les premiers résultats de notre metalness implémentée juste avant, nous avons élaboré une métrique inédite nommée Métallitude. Contrairement à une approche TF-IDF standard appliquée à un unique corpus, notre méthode repose sur une pondération croisée entre les deux jeux de données.

Le score est calculé par le produit de deux composantes distinctes :

1. Le **Term Frequency (TF)** calculé sur le corpus **Métal**, reflétant l'importance d'un mot au sein du genre cible.
2. L'**Inverse Document Frequency (IDF)** calculé sur le corpus **Non-Métal**, mesurant la rareté (ou la banalité) de ce même mot dans le langage musical standard.

Cette approche différentielle permet de pénaliser les mots fréquents dans le Métal mais aussi courants ailleurs (ex: "love", "time"), tout en propulsant les termes omniprésents dans le Métal mais absents du corpus témoin (auxquels un score IDF maximal est attribué). Le résultat final est normalisé (MinMax Scaling) sur une échelle de 0 à 1 pour faciliter l'interprétation.

**Les 20 mots les plus “métal” selon notre metallitude :**

![image.png](attachment:c4944384-099a-4316-bd53-bd37a4bd061e:image.png)

# IV (médium 3)

# V Démarches exploratoires

## 1. Clustering des 50 groupes ayant le plus d’albums selon la “Metallitude”

![image.png](attachment:8c9b027a-51af-44c4-b625-328938dec776:image.png)

Dans cette partie, on a calculé la **métallitude** moyenne par groupe et on a appliqué un clustering de densité (OPTICS). Puis, on a visualisé nos résultats en projetant dans un espace 2D avec UMAP.

La visualisation des résultats via cette projection met en évidence des regroupements cohérents, mais soulève une limite importante en termes de représentation graphique.

**Critiques de la visualisation :**

L'usage de l'UMAP ici s'avère superflu, voire contre-intuitif. En projetant une donnée unidimensionnelle (le score de Metalness) dans un plan 2D, l'algorithme crée une structure en forme de "serpent" qui n'apporte pas d'information structurelle supplémentaire. Avec plus de temps, un **histogramme de distribution**. Cela aurait permis de lire directement les seuils de scores séparant les groupes sans la distorsion spatiale induite par la réduction de dimension.

**Interprétation et validation des clusters :**

Malgré les réserves méthodologiques évoquées sur la visualisation, il s'avère que ce clustering basé sur la seule **Metallitude** a produit les résultats les plus cohérents de notre étude. La séparation des groupes est si nette qu'elle nous a permis d'attribuer une étiquette de genre dominante à chaque cluster.

**Méthode d'attribution des labels :**

L'étiquetage automatique des clusters repose sur un système de **vote majoritaire** appliqué aux métadonnées de genre extraites de l'Encyclopaedia Metallum. Pour chaque cluster identifié par OPTICS, nous avons :

1. Collecté les genres associés à chaque artiste du cluster depuis le fichier `bands_genres_cleaned.json` (issu du scraping de Metal Archives).
2. Compté les occurrences de chaque genre au sein du cluster à l'aide d'un compteur de fréquences.
3. Attribué au cluster l'étiquette correspondant aux deux genres les plus fréquents, séparés par " / ".

Cette approche permet une classification automatique sans annotation manuelle, en exploitant les métadonnées externes pour valider la cohérence sémantique des regroupements obtenus par clustering.

Comme l'illustre la figure annotée ci-dessous, cette approche permet une classification automatique pertinente : les clusters se polarisent naturellement entre les genres « extrêmes » (Death/Thrash) caractérisés par une haute _Metalness_, et les genres « mélodiques » (Power/Heavy) aux scores plus modérés.

![image.png](attachment:17a7ad49-91f6-4d3f-87cc-8b0a5431325c:image.png)

## 2. Clustering des albums selon leur score moyen de “metalness”

Dans une démarche exploratoire, nous avons tenté de segmenter les albums en effectuant un clustering basé sur leur score moyen de **metalness**.

![image.png](attachment:ba170726-cad4-40d7-9238-628be734fba3:image.png)

Afin d'interpréter visuellement cette répartition, nous avons projeté les résultats dans un espace en deux dimensions via l'algorithme UMAP. Bien que le graphique laisse apparaître des regroupements distincts (clusters colorés), une revue critique effectuée avec l'équipe enseignante a mis en lumière une incohérence méthodologique fondamentale dans cette approche.

En effet, nous avons tenté de projeter une donnée intrinsèquement unidimensionnelle (le score scalaire de metalness) vers un espace 2D. Cette opération est logiquement redondante : le clustering sur une seule variable revient à définir des seuils sur une ligne, et l'usage de l'UMAP ici complexifie artificiellement l'information sans gain analytique réel. Cette étape n'a donc pas été conservée pour l'analyse finale, mais elle a constitué un point d'apprentissage important sur la nécessité d'utiliser des données d'entrées multivariées pour justifier l'usage d'algorithmes de réduction de dimension.

## 3. Clustering des top 50 artistes selon la métallitude/Profanity/Readability

Dans cette partie, nous avons appliqué l'algorithme OPTICS sur les 50 groupes ayant le plus d’albums, en utilisant un espace vectoriel tridimensionnel composé de la **Metalness**, de la **Readability** (lisibilité) et du **Swear Word Ratio**. La projection UMAP de ce clustering révèle une polarisation sémantique saisissante qui valide la pertinence de nos métriques.

L'espace s'organise selon un gradient horizontal clair :

- **À gauche (Cluster rouge/orangé) :** On retrouve les piliers du **Métal Extrême** (Death, Black, Grindcore) tels que _Napalm Death_, _Behemoth_, _Darkthrone_ ou _Cradle of Filth_. Ce regroupement s'explique par une forte utilisation du vocabulaire violent (haute Metalness) et un taux de vulgarité élevé, caractéristiques intrinsèques de ces sous-genres.
- **À droite (Cluster violet/bleu) :** À l'opposé, le clustering isole les groupes de **Power Metal** et de **Heavy Metal traditionnel** comme _Iron Maiden_, _Helloween_, _Stratovarius_ ou _Yngwie Malmsteen_. Ces groupes, bien que "Métal", utilisent un vocabulaire souvent plus lyrique, fantastique ou épique, résultant en une Metalness différente et une quasi-absence de jurons, ce qui les éloigne mathématiquement du premier groupe.
- **Au centre (Points gris) :** Les artistes non classés (bruit/outliers) comme _Judas Priest_, _Dream Theater_ ou _Alice Cooper_ occupent une position intermédiaire, suggérant un équilibre lexical qui ne sature aucune des trois métriques observées.

En conclusion, la combinaison de la vulgarité, de la complexité du texte et de la "métallitude" suffit à recréer la distinction fondamentale entre le métal "mélodique" et le métal "extrême".

![image.png](attachment:a031c17a-2518-4e54-8a7a-a1c05f4d4ffc:image.png)

## 4. Clustering des 50 artistes ayant le plus d’albums selon la metallitude/Happiness

**Définition de la happiness :**

Pour quantifier la tonalité affective des paroles, nous nous sommes appuyés sur le dictionnaire de valence émotionnelle développé par le projet **Hedonometer**. Cette ressource lexicale repose sur une liste composite des 10 000 mots les plus fréquents de la langue anglaise, extraits de sources variées (Google Books, New York Times, Twitter et paroles de chansons).

La particularité de ce lexique réside dans sa méthode d'annotation : chaque mot a été évalué via une campagne de _crowdsourcing_ (Amazon Mechanical Turk), où des annotateurs humains ont attribué un score de ressenti sur une échelle de **1 (triste)** à **9 (heureux)**.

Dans le cadre de notre étude, la « Happiness » d'un texte est ainsi calculée en effectuant la moyenne des scores de valence des mots présents dans les paroles, permettant de situer chaque album sur un axe allant de la détresse émotionnelle à l'euphorie.

**Clustering :**

En croisant notre métrique de spécificité lexicale (**Metallitude**) avec l'analyse de valence émotionnelle (**Happiness**), le clustering révèle une polarisation encore plus marquée que précédemment. La projection UMAP dessine une trajectoire diagonale quasi-linéaire qui suggère une **corrélation inverse forte** :plus un groupe utilise un vocabulaire spécifique au métal, plus la tonalité émotionnelle de ses textes est négative.

![artist_clusters_optics_Happiness.png](attachment:a7eb1d70-1993-46f5-9c88-b52c063193a4:artist_clusters_optics_Happiness.png)

Cette analyse sépare distinctement deux mondes :

- **Le pôle Épique et Positif (Cluster violet - Haut Gauche) :** On y retrouve les figures du Power Metal et du Heavy Metal mélodique comme _Helloween_, _Stratovarius_, _Yngwie Malmsteen_ ou _Iron Maiden_. Leur position indique des textes moins saturés en vocabulaire "metal" exclusif et une valence émotionnelle plus élevée (plus "joyeuse" ou héroïque).
- **Le pôle Sombre et Extrême (Cluster rouge - Bas Droite) :** À l'opposé, les groupes de Death et Black Metal comme _Napalm Death_, _Behemoth_, _Darkthrone_ ou _Sodom_ sont isolés dans une zone de "bonheur minimal" et de "métallitude maximale".

Ce graphique confirme une hypothèse structurelle du genre :

L'identité lexicale du métal extrême se construit intrinsèquement sur la négativité et la détresse émotionnelle, là où le métal traditionnel conserve une part de positivité lexicale.

# VI Conclusion

Le projet **PAO Metal Mining** a permis de valider l’apport des techniques de Data Science et du Traitement Automatique du Langage (NLP) pour l’analyse musicologique à grande échelle. En structurant un pipeline complet, allant de la collecte distribuée de milliers de titres jusqu’à l’analyse multivariée, nous avons pu objectiver les caractéristiques stylistiques d’un genre souvent réduit à des stéréotypes.

**Enseignements méthodologiques**

Au-delà des résultats musicaux, ce projet a constitué un laboratoire d’apprentissage méthodologique. La critique de nos propres visualisations (notamment l’usage inapproprié de l’UMAP sur des données unidimensionnelles) a souligné l’importance de l’adéquation entre la nature des données et les algorithmes de projection.

À l’inverse, le succès du clustering multivarié (Metalness/Readability/Profanity) confirme que l’identité d’un groupe de metal peut être prédite avec une grande fiabilité uniquement à partir de ses textes, sans aucune analyse du signal audio.

**Perspectives**

Ce travail exploratoire ouvre la voie à des analyses plus poussées.

L'intégration de modèles de langage profonds (LLM) pourrait permettre de dépasser l'approche par "sac de mots" (Bag-of-Words) pour analyser la sémantique et les structures narratives des chansons.

De même, le croisement de ces données textuelles avec des descripteurs audio (tempo, distorsion) permettrait de dresser une cartographie encore plus exhaustive de l'univers metal.

# VI Sources

[When heavy metal meets data science | Episode I](https://blog.lucaballore.com/when-heavy-metal-meets-data-science-2e840897922e)

[When heavy metal meets data science | Episode II](https://blog.lucaballore.com/when-heavy-metal-meets-data-science-3fc32e9096fa)

[When heavy metal meets data science | Episode III](https://blog.lucaballore.com/when-heavy-metal-meets-data-science-episode-iii-9f6e4772847e)

[GitHub - lballore/deep-metal: NLP analysis on heavy metal lyrics and NN-based lyrics generator](https://github.com/lballore/deep-metal)

[The Hedonometer](https://hedonometer.org/words/labMT-en-v2/)

[Home - Encyclopaedia Metallum: The Metal Archives](https://www.metal-archives.com/)
