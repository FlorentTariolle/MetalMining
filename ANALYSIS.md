# Detailed Analysis - PAO Metal Mining

Complete documentation of the methodology, results, and analyses of the project.

**Note:** "PAO" is a French acronym for "Projet d'Approfondissement et d'Ouverture" (Deepening and Opening Project), which is a school project at INSA Rouen.

# **I Data Collection (Scraping)**

The first step of the project consisted of building a dataset of metal song lyrics. Two data sources were used: **DarkLyrics** for lyrics and **Metal Archives** for genre metadata.

**1. Lyrics Scraping via DarkLyrics**

The main scraping relies on the Python library `metalparser`, which allows automated querying of the DarkLyrics website.

The `scraper.py` script implements a **distributed scraping** system allowing multiple users to work in parallel on different portions of the dataset:

- The complete artist list is divided into **4 quarters**, each assigned to a different user.
- Each user runs the script with their name (`-user Florent`, `-user Nizar`, etc.) and only processes their assigned portion.
- A **progressive saving** system records the progress state after each processed artist, allowing scraping to resume in case of interruption.

For each artist, the script retrieves:

- lyrics of each song,
- titles,
- albums,
- release years,
- publication type (album, EP, demo),
- track number.

Individual progress files (`progress1.json`, `progress2.json`, etc.) are then merged via `merge_progress_files.py` to create the final `dataset.json` file.

**2. Genre Scraping via Metal Archives**

To enrich the dataset with musical genres for each band, a second script (`metallum_webscraper.py`) queries the **Metal Archives** (Encyclopaedia Metallum) website.

This scraping uses **Selenium** with an automated Chrome browser to bypass the site's anti-bot protections:

- The script applies **stealth** techniques (masking `webdriver` properties, custom user-agent, etc.).
- For each band, it accesses its dedicated page and extracts the genre from the `#band_stats` section.
- A configurable delay between requests allows respecting server limits.

Retrieved genres are saved in `data/bands_genres.json`, then cleaned via `clean_genres.py` to produce `bands_genres_cleaned.json`.

**3. Data Merging and Enrichment**

Progress files are merged via `merge_progress_files.py`, which also adds **automatic language detection** for each song (via the `langdetect` library).

The final dataset (`data/dataset.json`) contains for each song:

- Artist, album, title
- Complete lyrics
- Release year and publication type
- Automatically detected language

This file forms the basis for all analysis steps.

# II Descriptive Analysis of the Corpus

## 1. Lyrics Presence and Dataset Structure

Before starting textual analyses, we evaluated the completeness of the dataset.

The vast majority of titles have their lyrics, which guarantees the reliability of the linguistic measures that follow. The publication structure also shows a clear predominance of albums, while EPs and demos remain in the minority.

![image.png](attachment:11f1a84d-dca2-4039-98f4-f882fa4d461d:image.png)

![image.png](attachment:340d1107-99cb-4430-b8c3-9b5ec5e4c30f:image.png)

These initial results confirm that the corpus is sufficiently rich and coherent to conduct all planned analyses.

### 2. Distribution of Artists and Albums

We then studied the distribution of the corpus by artist and by album to identify the most represented groups.

![image.png](attachment:c45e053b-a081-42dc-9ef8-504789d4467a:image.png)

![image.png](attachment:1c98e75c-8de5-498b-be18-67ee9b4497ef:image.png)

Artists like **Judas Priest**, **Alice Cooper**, **Rage**, **Motörhead**, or **Napalm Death** appear particularly prolific, reflecting their longevity and the importance of their discography in metal history.

## 3. Temporal Evolution of Production

The analysis by release year shows a progressive growth in the number of songs since the late 1970s, followed by a major peak between 2000 and 2015.

This dynamic corresponds to the expansion of metal subgenres and the rise of digital distribution platforms.

![image.png](attachment:32f22caf-3ee4-435d-834c-47af9fc63c2f:image.png)

## 4. Language Distribution

The majority of songs in the corpus are in English, which is consistent with the central place of this language in the international metal scene. The "Unknown" category (6.2%) mainly groups titles whose language could not be automatically determined, often due to insufficient information.

Other languages present—such as German, Spanish, or Finnish—appear in reduced proportions but testify to the activity of several national scenes, particularly in Europe.

![image.png](attachment:c9568806-01a2-44dd-8e31-df893e6f1c3c:image.png)

![image.png](attachment:eb16a238-4182-4d23-b8a2-b0f51bfe2d89:90a25ecb-58aa-4415-b580-57d653235dfb.png)

# III Linguistic and Stylistic Analysis of Metal

The linguistic analysis relies on four complementary indicators to characterize the language and style of lyrics.

1. **Swear word ratio**

   Proportion of profane words in a song.

   It highlights the use of an aggressive, direct, or provocative register.

2. **Coleman–Liau Readability Index**

   Readability index based on average word and sentence length.

   A high score indicates more complex and structured lyrics.

   ![image.png](attachment:90f2ec1e-672f-4427-9d93-8667ec1b3b0d:image.png)

3. **Proportion of "stupid songs"**

   Category from the reference dataset, grouping tracks considered very simple or basic in their writing.

   It allows identifying songs whose textual content is minimal or very underdeveloped.

4. **Metalness**

   The Metalness metric is a normalized measure that evaluates how specific a word is to the "Metal" corpus compared to the "Non-Metal" corpus.

   It relies on comparing word occurrence frequencies in both datasets. Calculation details are presented in [6. Metalness](https://www.notion.so/6-Metalness-2cc87cb0143d806b8548e25e7f88a518?pvs=21)

These four measures form the basis of the linguistic and stylistic analysis of the corpus.

## **1. Profanity and Complexity: Two Unrelated Dimensions**

The scatter plot shows that swear word ratio and readability index do not evolve together.

We observe very profane artists with relatively structured lyrics, others very simple with little or no profanity, and a majority grouped in an intermediate zone.

![image.png](attachment:dcbb4b14-4260-4e80-8e51-6e607ab2677c:image.png)

In our corpus, high Coleman–Liau values do not describe true literary complexity: they rather correspond to slightly denser writing, often equivalent to a school level between **end of middle school and beginning of high school**.

In other words, the "most complex" texts in the dataset remain accessible, but they contain more words per sentence or a slightly more developed vocabulary.

This observation confirms that profanity is not an indicator of quality or writing level: it relates to a stylistic choice specific to certain extreme subgenres.

## **2. The Extremes of the Linguistic Spectrum**

![image.png](attachment:4f9f4a7b-9436-4210-853d-a05290503f3c:82acaf95-2cad-49a5-925f-6befcb2b22e2.png)

The results show two opposite profiles.

The highest swear word ratios are found in bands like _Meat Shits_, _Anal Cunt_, or _Barbatos_, characterized by very direct texts and simple structure.

Conversely, the highest readability scores appear in _Cynic_, _Dissection_, _Botanist_, or _Dark Tranquillity_, whose lyrics present on average longer sentences and more varied vocabulary.

## **3. Evolution of Swear Word Ratio**

![image.png](attachment:84a24bf5-4c6f-4a8c-bff4-70bca6a9a59a:image.png)

The evolution of swear word ratio shows a clear dynamic. We observe a regular progression between the late 1970s and the mid-1990s, a period corresponding to the appearance and structuring of several subgenres characterized by a more profane register.

From the 2000s onwards, values stabilize around a constant level, with no upward or downward trend.

These results indicate that the use of profane terms has established itself as a characteristic specific to certain segments of the genre, while remaining stable at the global corpus scale.

## **4. General Trends in Readability and Textual Simplicity**

![image.png](attachment:7c8276d0-bcc4-4a37-a17e-d91d954a486b:image.png)

The readability index shows a slight increase over time. Values remain globally compatible with a level between middle school and beginning of high school, which indicates that texts do not become truly complex, but show a tendency toward slightly longer sentences and a slightly more varied vocabulary.

The observed evolution therefore corresponds to moderate enrichment rather than an important structural change.

![image.png](attachment:f7187c57-8fef-4c60-b385-09bd2e20af0a:image.png)

The relationship between swear word ratio and the proportion of "stupid songs" highlights a global behavior of the corpus: artists displaying a higher profanity ratio also have a higher frequency of tracks characterized by minimal or very short text.

This association indicates that lexical density varies significantly from one artist to another. The dispersion of values shows a continuous distribution, without clear distinction or strict clusters, which reflects a diversity of writing practices rather than a separation into defined categories.

## 5. **Lexical Frequency Analysis via Word Clouds**

In an exploratory approach to identify predominant themes, we calculated term occurrences in each corpus to generate distinct word clouds. This visualization highlights a striking semantic dichotomy between the two genres.

The word cloud of the **"Non-Metal"** corpus reveals a vocabulary mainly anchored in emotional registers and interpersonal relationships. We observe a clear predominance of verbs and common nouns related to emotions and daily life, with central terms such as "love", "baby", "know", "never", or "time".

![non_metal_wordcloud.png](attachment:9deb84ea-832f-4f31-9b1c-09aa0ef98492:non_metal_wordcloud.png)

Conversely, the visualization of the **"Metal"** corpus exposes a radically darker and more aggressive lexical field. The most frequent words, which appear here massively, belong to the register of violence, death, and conflict. Terms like "blood", "kill", "death", "war", "fire", and "hell" saturate the visual space, thus confirming the thematic singularity of the Metal genre compared to generalist popular music standards.

![image.png](attachment:d6387b46-665d-4ffe-89c2-f6c3b990e077:image.png)

## 6. Metalness

### A. Preprocessing and Filtering

Before calculation, two filters are applied to reduce statistical noise:

- **Frequency threshold:** Only words appearing at least **5 times** in each corpus are kept (`v >= 5`). This eliminates words that are too rare and would skew the ratios.
- **Intersection and Length:** Calculation is performed only on words present in **both** corpora (`intersection`) and having more than 2 letters, to exclude linking words that are too short and non-significant.

### B. Mathematical Formulation

The score is calculated in two steps for each word w: calculation of the logarithmic coefficient, then its normalization.

**a. The Metalness Coefficient (Log-Ratio)**
The code first calculates the logarithm of the ratio of raw frequencies between the two corpora. Let fmetal(w) be the frequency of the word in the Metal corpus and fnon_metal(w) its frequency in the Non-Metal corpus:

$$
coeff(w) = ln(\frac{f_{nonmetal}(w)}{f_{metal}(w)})
$$

- If the word is more frequent in Metal, coeff>0.
- If the word is more frequent in Non-Metal, coeff<0.

**b. "Metalness" (Sigmoid Transformation)**
To obtain a readable and bounded score, a **sigmoid** function is applied to the coefficient. This transforms the value (which ranges from −∞ to +∞) into a probability between

$$
Metalness(w) = \frac{1}{1 + e^{-coeff(w)}}
$$

### C. Score Interpretation

If a word's score is:

- Close to 1: The word is strongly characteristic of **Metal**
- Close to 0: The word is strongly characteristic of the **Non-Metal** genre
- Around 0.5: The word is neutral

**The 20 most metal words according to "metalness"**

![image.png](attachment:36cef1d1-ae7a-416e-8396-ad24e1d8ae3d:image.png)

## 7. Metallitude

After the initial results of our previously implemented metalness, we developed a novel metric called Metallitude. Unlike a standard TF-IDF approach applied to a single corpus, our method relies on cross-weighting between the two datasets.

The score is calculated by the product of two distinct components:

1. **Term Frequency (TF)** calculated on the **Metal** corpus, reflecting the importance of a word within the target genre.
2. **Inverse Document Frequency (IDF)** calculated on the **Non-Metal** corpus, measuring the rarity (or banality) of the same word in standard musical language.

This differential approach penalizes words frequent in Metal but also common elsewhere (e.g., "love", "time"), while boosting terms omnipresent in Metal but absent from the reference corpus (to which a maximum IDF score is attributed). The final result is normalized (MinMax Scaling) on a scale from 0 to 1 to facilitate interpretation.

**The 20 most "metal" words according to our metallitude:**

![image.png](attachment:c4944384-099a-4316-bd53-bd37a4bd061e:image.png)

# IV (medium 3)

# V Exploratory Approaches

## 1. Clustering of the 50 Bands with the Most Albums According to "Metallitude"

![image.png](attachment:8c9b027a-51af-44c4-b625-328938dec776:image.png)

In this section, we calculated the average **metallitude** per band and applied density clustering (OPTICS). Then, we visualized our results by projecting into a 2D space with UMAP.

Visualizing results via this projection highlights coherent groupings but raises an important limitation in terms of graphical representation.

**Visualization Critiques:**

The use of UMAP here proves superfluous, even counter-intuitive. By projecting one-dimensional data (the Metalness score) into a 2D plane, the algorithm creates a "snake"-shaped structure that does not provide additional structural information. With more time, a **distribution histogram** would have allowed directly reading the score thresholds separating groups without the spatial distortion induced by dimension reduction.

**Cluster Interpretation and Validation:**

Despite the methodological reservations mentioned about visualization, it turns out that this clustering based solely on **Metallitude** produced the most coherent results of our study. The separation of groups is so clear that it allowed us to assign a dominant genre label to each cluster.

**Label Attribution Method:**

Automatic cluster labeling relies on a **majority voting** system applied to genre metadata extracted from Encyclopaedia Metallum. For each cluster identified by OPTICS, we:

1. Collected genres associated with each artist in the cluster from the `bands_genres_cleaned.json` file (from Metal Archives scraping).
2. Counted occurrences of each genre within the cluster using a frequency counter.
3. Assigned to the cluster the label corresponding to the two most frequent genres, separated by " / ".

This approach enables automatic classification without manual annotation, exploiting external metadata to validate the semantic coherence of groupings obtained by clustering.

As illustrated in the annotated figure below, this approach enables relevant automatic classification: clusters naturally polarize between "extreme" genres (Death/Thrash) characterized by high _Metalness_, and "melodic" genres (Power/Heavy) with more moderate scores.

![image.png](attachment:17a7ad49-91f6-4d3f-87cc-8b0a5431325c:image.png)

## 2. Clustering of Albums According to Their Average "Metalness" Score

In an exploratory approach, we attempted to segment albums by performing clustering based on their average **metalness** score.

![image.png](attachment:ba170726-cad4-40d7-9238-628be734fba3:image.png)

To visually interpret this distribution, we projected the results into a two-dimensional space via the UMAP algorithm. Although the graph shows distinct groupings (colored clusters), a critical review conducted with the teaching team highlighted a fundamental methodological inconsistency in this approach.

Indeed, we attempted to project intrinsically one-dimensional data (the scalar metalness score) into a 2D space. This operation is logically redundant: clustering on a single variable amounts to defining thresholds on a line, and using UMAP here artificially complicates the information without real analytical gain. This step was therefore not retained for the final analysis, but it constituted an important learning point on the necessity of using multivariate input data to justify the use of dimension reduction algorithms.

## 3. Clustering of Top 50 Artists According to Metallitude/Profanity/Readability

In this section, we applied the OPTICS algorithm to the 50 bands with the most albums, using a three-dimensional vector space composed of **Metalness**, **Readability**, and **Swear Word Ratio**. The UMAP projection of this clustering reveals a striking semantic polarization that validates the relevance of our metrics.

The space organizes according to a clear horizontal gradient:

- **On the left (Red/orange cluster):** We find the pillars of **Extreme Metal** (Death, Black, Grindcore) such as _Napalm Death_, _Behemoth_, _Darkthrone_, or _Cradle of Filth_. This grouping is explained by heavy use of violent vocabulary (high Metalness) and a high profanity rate, intrinsic characteristics of these subgenres.
- **On the right (Purple/blue cluster):** Conversely, clustering isolates **Power Metal** and traditional **Heavy Metal** groups like _Iron Maiden_, _Helloween_, _Stratovarius_, or _Yngwie Malmsteen_. These bands, although "Metal", use vocabulary often more lyrical, fantastical, or epic, resulting in different Metalness and quasi-absence of profanity, which mathematically distances them from the first group.
- **In the center (Gray points):** Unclassified artists (noise/outliers) like _Judas Priest_, _Dream Theater_, or _Alice Cooper_ occupy an intermediate position, suggesting a lexical balance that does not saturate any of the three observed metrics.

In conclusion, the combination of profanity, text complexity, and "metallitude" is sufficient to recreate the fundamental distinction between "melodic" metal and "extreme" metal.

![image.png](attachment:a031c17a-2518-4e54-8a7a-a1c05f4d4ffc:image.png)

## 4. Clustering of the 50 Artists with the Most Albums According to Metallitude/Happiness

**Definition of Happiness:**

To quantify the affective tone of lyrics, we relied on the emotional valence dictionary developed by the **Hedonometer** project. This lexical resource is based on a composite list of the 10,000 most frequent words in English, extracted from various sources (Google Books, New York Times, Twitter, and song lyrics).

The particularity of this lexicon lies in its annotation method: each word was evaluated via a _crowdsourcing_ campaign (Amazon Mechanical Turk), where human annotators attributed a feeling score on a scale from **1 (sad)** to **9 (happy)**.

In the context of our study, the "Happiness" of a text is calculated by taking the average of valence scores of words present in the lyrics, allowing each album to be positioned on an axis ranging from emotional distress to euphoria.

**Clustering:**

By crossing our lexical specificity metric (**Metallitude**) with emotional valence analysis (**Happiness**), clustering reveals an even more marked polarization than previously. The UMAP projection draws a quasi-linear diagonal trajectory suggesting a **strong inverse correlation**: the more a group uses vocabulary specific to metal, the more negative the emotional tone of its texts.

![artist_clusters_optics_Happiness.png](attachment:a7eb1d70-1993-46f5-9c88-b52c063193a4:artist_clusters_optics_Happiness.png)

This analysis distinctly separates two worlds:

- **The Epic and Positive Pole (Purple cluster - Top Left):** We find figures of Power Metal and melodic Heavy Metal like _Helloween_, _Stratovarius_, _Yngwie Malmsteen_, or _Iron Maiden_. Their position indicates texts less saturated with exclusive "metal" vocabulary and higher emotional valence (more "joyful" or heroic).
- **The Dark and Extreme Pole (Red cluster - Bottom Right):** Conversely, Death and Black Metal groups like _Napalm Death_, _Behemoth_, _Darkthrone_, or _Sodom_ are isolated in a zone of "minimal happiness" and "maximum metallitude".

This graph confirms a structural hypothesis of the genre:

The lexical identity of extreme metal is intrinsically built on negativity and emotional distress, where traditional metal retains a part of lexical positivity.

# VI Conclusion

The **PAO Metal Mining** project validated the contribution of Data Science and Natural Language Processing (NLP) techniques for large-scale musicological analysis. By structuring a complete pipeline, from distributed collection of thousands of titles to multivariate analysis, we were able to objectify the stylistic characteristics of a genre often reduced to stereotypes.

**Methodological Lessons**

Beyond musical results, this project constituted a methodological learning laboratory. The critique of our own visualizations (notably the inappropriate use of UMAP on one-dimensional data) highlighted the importance of adequacy between data nature and projection algorithms.

Conversely, the success of multivariate clustering (Metalness/Readability/Profanity) confirms that a metal band's identity can be predicted with high reliability solely from its texts, without any audio signal analysis.

**Perspectives**

This exploratory work opens the way to more advanced analyses.

The integration of deep language models (LLM) could allow going beyond the "bag of words" approach to analyze semantics and narrative structures of songs.

Similarly, crossing this textual data with audio descriptors (tempo, distortion) would allow drawing an even more exhaustive cartography of the metal universe.

# VI Sources

[When heavy metal meets data science | Episode I](https://blog.lucaballore.com/when-heavy-metal-meets-data-science-2e840897922e)

[When heavy metal meets data science | Episode II](https://blog.lucaballore.com/when-heavy-metal-meets-data-science-3fc32e9096fa)

[When heavy metal meets data science | Episode III](https://blog.lucaballore.com/when-heavy-metal-meets-data-science-episode-iii-9f6e4772847e)

[GitHub - lballore/deep-metal: NLP analysis on heavy metal lyrics and NN-based lyrics generator](https://github.com/lballore/deep-metal)

[The Hedonometer](https://hedonometer.org/words/labMT-en-v2/)

[Home - Encyclopaedia Metallum: The Metal Archives](https://www.metal-archives.com/)
