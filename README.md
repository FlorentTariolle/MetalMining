# PAO Metal Mining

Large-scale analysis of heavy metal lyrics using Data Science and Natural Language Processing (NLP) techniques.

**Note:** "PAO" is a French acronym for "Projet d'Approfondissement et d'Ouverture" (Deepening and Opening Project), which is a school project at INSA Rouen.

## Credits

Rayen, Mathis, Nizar, and Florent

## Objective

Examine vocabulary, themes, emotions, and stylistic evolution of metal music through a large and representative corpus of songs.

## Project Structure

### Data Collection

- **`scraper.py`** : Distributed scraping of lyrics via DarkLyrics (quarter system for parallel work)
- **`metallum_webscraper.py`** : Scraping of musical genres via Metal Archives (Selenium)
- **`merge_progress_files.py`** : Merging of progress files and automatic language detection

### Analysis

- **Linguistic metrics** : Swear word ratio, Coleman–Liau Readability Index, Metalness, Metallitude
- **Clustering** : Analysis of artists and albums according to different metric combinations
- **Visualizations** : Word clouds, UMAP projections, temporal analyses

### Data

- **`data/dataset.json`** : Main dataset with lyrics, metadata, and detected language
- **`data/bands_genres_cleaned.json`** : Musical genres by band

## Main Metrics

1. **Swear word ratio** : Proportion of profane words
2. **Coleman–Liau Readability Index** : Text complexity
3. **Metalness** : Specificity of a word to the Metal corpus vs Non-Metal (log-ratio + sigmoid)
4. **Metallitude** : Cross TF-IDF (TF on Metal, IDF on Non-Metal)

## Key Results

- Clear distinction between "extreme" metal (Death/Black) and "melodic" metal (Power/Heavy) via multivariate clustering
- Inverse correlation between Metallitude and Happiness (emotional valence)
- Temporal evolution of vocabulary and profanity since the 1970s

## Detailed Documentation

For complete details on methodology, results, visualizations, and conclusions, see **[ANALYSIS.md](ANALYSIS.md)**.

## Sources

- [When heavy metal meets data science](https://blog.lucaballore.com/when-heavy-metal-meets-data-science-2e840897922e) (Episodes I, II, III)
- [GitHub - deep-metal](https://github.com/lballore/deep-metal)
- [The Hedonometer](https://hedonometer.org/words/labMT-en-v2/)
- [Encyclopaedia Metallum](https://www.metal-archives.com/)
