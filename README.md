# Metal Mining - Data Analysis Project

Academic project developed for the _Projet d'Approfondissement et d'Ouverture_ (PAO) at INSA Rouen. This project collects, processes, and analyzes metal music lyrics to study linguistic patterns, genre characteristics, and lyrical content.

## Project Overview

The project is divided into three main phases:

1. **Data Collection**: Scraping metal lyrics and metadata from multiple sources
2. **Data Processing**: Cleaning, merging, and enriching the collected data
3. **Data Analysis**: Statistical and linguistic analysis of the lyrics

## Data Collection

### DarkLyrics Scraper (`scraper.py`)

- Scrapes artists, albums, and song lyrics from [DarkLyrics](http://www.darklyrics.com/)
- Supports multi-user distributed scraping by splitting artists into quarters
- Saves progress incrementally (`progress<quarter>.json`) for resumability
- Uses the `metalparser` library for web scraping

### Metal Archives Genre Scraper (`metallum_webscraper.py`)

- Scrapes genre information for top bands from [Metal Archives](https://www.metal-archives.com/)
- Uses Selenium for browser automation to bypass anti-bot measures
- Processes top bands extracted from the main dataset

### Data Merging (`merge_progress_files.py`)

- Merges progress files from all team members into a unified dataset
- Adds automatic language detection to each song using `langdetect`
- Outputs final dataset (`data/dataset.json`) with enriched metadata

## Data Processing

- **`extract_top_bands.py`**: Extracts top bands by song count for focused analysis
- **`clean_genres.py`**: Cleans and standardizes genre classifications
- **`recalculate_languages.py`**: Recalculates language detection with improved accuracy

## Data Analysis

### Basic Distribution Analysis (`analyzer.py`)

Visualizes dataset characteristics:

- Songs with/without lyrics distribution
- Publication types (albums, EPs, singles)
- Top bands by song/album count
- Temporal distribution (songs by release year)
- Language distribution across the dataset

### Advanced Linguistic Analysis (`analyzer2.py`)

Deep analysis of lyrical content following academic research methodology:

- **Readability Analysis**: Coleman-Liau Index computation
- **Swear Word Analysis**: Profanity ratio calculation
- **Stupidity Curve**: Relationship between readability and swear ratio
- **Temporal Evolution**: Changes in lyrical characteristics over time

### Metalness Analysis (`process_wordcloud_metalness.py`, `tf_idf.py`)

- Word frequency analysis and word cloud generation
- TF-IDF scoring to identify distinctive vocabulary
- Metalness computation comparing metal vs non-metal lyrics
- Visualizations highlighting characteristic vocabulary

### Clustering Analysis (`albums_clustering.py`)

- OPTICS clustering of albums based on lyrical content
- UMAP dimensionality reduction for visualization
- Album-level metalness scoring

## Prerequisites

Install required packages:

```bash
pip install -r requirements.txt
```

## Data Structure

The main dataset (`data/dataset.json`) contains:

- Artists with their albums and songs
- Song lyrics with language detection
- Album metadata (release year, type)
- Genre classifications (in separate files)

## Credits

This project utilizes:

- `metalparser` module developed by Luca Ballore for DarkLyrics scraping
- `langdetect` for automatic language detection
- Standard Python data science stack (pandas, numpy, matplotlib, seaborn)

## Current Status

The project has completed data collection from DarkLyrics and Metal Archives. The unified dataset includes metadata-enriched lyrics with language detection.
