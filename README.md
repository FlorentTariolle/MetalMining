# PAO Metal Mining

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?logo=pandas&logoColor=white)](https://pandas.pydata.org/)

Large-scale analysis of heavy metal lyrics using Data Science and Natural Language Processing (NLP) techniques.

**Note:** "PAO" is a French acronym for "Projet d'Approfondissement et d'Ouverture" (Deepening and Opening Project), which is a school project at [INSA Rouen Normandie](https://www.insa-rouen.fr/en).

## Objective

Examine vocabulary, themes, emotions, and stylistic evolution of metal music through a large and representative corpus of songs.

## Project Structure

The project is organized into modular packages:

### `data_collection/`

- **`scraper.py`** : Distributed scraping of lyrics via DarkLyrics (quarter system for parallel work)
- **`metallum_webscraper.py`** : Scraping of musical genres via Metal Archives (Selenium)
- **`merge_progress_files.py`** : Merging of progress files and automatic language detection
- **`recalculate_languages.py`** : Language detection recalculation utilities

### `data_loading/`

- **`dataset_loader.py`** : Loading and parsing of the main dataset JSON file
- **`filters.py`** : Data filtering functions (language, genre, etc.)

### `metrics/`

- **`song_metrics.py`** : Main function for computing all song-level metrics
- **`swear_words.py`** : Swear word ratio calculation
- **`readability.py`** : Coleman–Liau Readability Index computation
- **`metalness.py`** : Metalness metric (word specificity to Metal vs Non-Metal corpus)
- **`metallitude.py`** : Metallitude metric (cross TF-IDF)
- **`sentiment.py`** : Sentiment analysis using VADER

### `clustering/`

- **`artists_tf_idf.py`** : TF-IDF vectorization for artists
- **`albums_tf_idf.py`** : TF-IDF vectorization for albums
- **`clustering_MRSW.py`** : Clustering based on Metalness, Readability, Swear words
- **`albums_clustering.py`** : Album-level clustering analysis
- **`cluster_labeling.py`** : Automatic cluster labeling and interpretation

### `visualization/`

- **`metrics_plots.py`** : General metric visualization functions
- **`sentiment_plots.py`** : Sentiment analysis visualizations
- **`wordcloud.py`** : Word cloud generation
- **`distribution.py`** : Data distribution plots

### `aggregation/`

- **`aggregation.py`** : Aggregation functions (by artist, by year, etc.)

### `scripts/`

Main analysis scripts:

- **`metrics_analysis.py`** : Swear words, readability, and "stupidity curve" analysis
- **`sentiment_analysis.py`** : Sentiment analysis and emotional valence
- **`metalness_computation.py`** : Metalness metric computation
- **`metallitude_computation.py`** : Metallitude metric computation
- **`dataset_distribution.py`** : Dataset statistics and distribution analysis
- **`top_romanian_artists.py`** : Analysis of Romanian metal artists
- **`clean_genres.py`** : Genre data cleaning utility

### `utils/`

- **`metalness_loader.py`** : Loading precomputed metalness data
- **`extract_top_bands.py`** : Utility for extracting top bands from dataset

### `resources/`

- **`swear_words_eng.txt`** : English swear words dictionary for profanity ratio
- **`stopwords_eng.txt`** : English stopwords list for text filtering
- **`vader_lexicon.txt`** : VADER sentiment lexicon

### Data Files

- **`data/dataset.json`** : Main dataset with lyrics, metadata, and detected language
- **`data/bands_genres_cleaned.json`** : Musical genres by band
- **`data/artists_list.json`** : List of artists for scraping
- **`cache/`** : Cached intermediate data files (hedonometer, lyrics data, etc.)
- **`output_data/`** : Generated output files (cluster labels, metrics, word rankings)
- **`output_pics/`** : Generated visualization images

## Installation

Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Main analysis scripts are located in the `scripts/` directory. Run them from the project root:

```bash
# Metrics analysis (swear words, readability)
python scripts/metrics_analysis.py [--json data/dataset.json] [--sample N]

# Sentiment analysis
python scripts/sentiment_analysis.py

# Metalness computation
python scripts/metalness_computation.py

# Metallitude computation
python scripts/metallitude_computation.py
```

Most scripts support command-line arguments for customizing input paths and parameters. Use `--help` for detailed options.

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

For complete details on methodology, results, visualizations, and conclusions, see **[REPORT.md](REPORT.md)**.

## Credits

Rayen, Mathis, Nizar, and Florent

## Sources

- [When Heavy Metal Meets Data Science](https://blog.lucaballore.com/)
- [GitHub - deep-metal](https://github.com/lballore/deep-metal)
- [The Hedonometer](https://hedonometer.org/words/labMT-en-v2/)
- [Encyclopaedia Metallum](https://www.metal-archives.com/)
