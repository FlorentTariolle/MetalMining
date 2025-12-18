"""Sentiment analysis using VADER."""

import os
import pandas as pd
from typing import Optional
import nltk
from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.data import find
from tqdm import tqdm


def ensure_nltk_resources():
    """Ensure required NLTK resources are downloaded."""
    nltk.data.path.append(os.path.join(os.getcwd(), "resources"))
    for resource in ["punkt", "vader_lexicon"]:
        try:
            find(resource)
        except LookupError:
            nltk.download(resource)


def words_happiness(words_metalness_dataset: pd.DataFrame,
                    happiness_dataset: pd.DataFrame) -> pd.DataFrame:
    """
    Merge metalness dataset with happiness scores (Hedonometer).
    
    Args:
        words_metalness_dataset: DataFrame with 'Word' column
        happiness_dataset: DataFrame with 'Word' and 'Happiness Score' columns
        
    Returns:
        Merged DataFrame sorted by happiness score
    """
    output = (
        pd.merge(
            words_metalness_dataset,
            happiness_dataset,
            on="Word",
            how="left",
        )
        .sort_values("Happiness Score", ascending=False)
        .drop(columns=["Word in English"])
        .dropna(subset=["Happiness Score"])
        .reset_index(drop=True)
    )
    return output


def measure_lyrics_sentiment(text: str) -> float:
    """
    Measure sentiment of lyrics using VADER sentiment analyzer.
    
    Args:
        text: The text to analyze
        
    Returns:
        Average compound sentiment score (-1 to 1)
    """
    if not isinstance(text, str):
        return 0.0
    text = text.strip()
    if not text:
        return 0.0

    sentences = tokenize.sent_tokenize(text)
    if not sentences:
        return 0.0

    sid = SentimentIntensityAnalyzer()
    values = [sid.polarity_scores(s)["compound"] for s in sentences]
    return float(sum(values) / len(values))


def add_sentiment_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add sentiment_index column to DataFrame by analyzing lyrics.
    
    Args:
        df: DataFrame with 'lyrics' column
        
    Returns:
        DataFrame with added 'sentiment_index' column
    """
    if "lyrics" not in df.columns:
        raise ValueError("Missing column 'lyrics'.")

    out = df.copy()
    tqdm.pandas()
    out["sentiment_index"] = (
        out["lyrics"].fillna("").astype(str).progress_apply(measure_lyrics_sentiment)
    )
    return out
