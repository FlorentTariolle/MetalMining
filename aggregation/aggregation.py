"""Aggregation functions for grouping metrics by artist, album, or year."""

import pandas as pd
import numpy as np


def aggregate_by_artist(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate metrics by artist.
    
    Computes average swear_word_ratio, average readability_index, and song count per artist.
    
    Args:
        df: DataFrame with 'artist', 'swear_word_ratio', 'readability', and 'song' columns
        
    Returns:
        DataFrame aggregated by artist
    """
    return (df.groupby("artist")
              .agg(average_swear_word_ratio=("swear_word_ratio", "mean"),
                   average_readability_index=("readability", "mean"),
                   n_songs=("song", "count"))
              .reset_index())


def aggregate_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate metrics by release year.
    
    Computes average swear_word_ratio and average readability_index per year.
    
    Args:
        df: DataFrame with 'release_year', 'swear_word_ratio', and 'readability' columns
        
    Returns:
        DataFrame aggregated by year, sorted by release_year
    """
    return (df.groupby("release_year")
              .agg(average_swear_word_ratio=("swear_word_ratio", "mean"),
                   average_readability_index=("readability", "mean"))
              .reset_index()
              .sort_values("release_year"))


def aggregate_sentiment_by_artist(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate sentiment and other metrics by artist.
    
    Computes average sentiment, and optionally metalness, readability, and swear_word_ratio
    if these columns exist in the input DataFrame.
    
    Args:
        df: DataFrame with 'artist' and 'sentiment_index' columns, and optionally
            'metalness', 'readability', 'swear_word_ratio'
            
    Returns:
        DataFrame aggregated by artist, sorted by sentiment (descending)
    """
    if "artist" not in df.columns or "sentiment_index" not in df.columns:
        raise ValueError("Missing required columns 'artist' or 'sentiment_index'.")

    agg = {
        "sentiment": ("sentiment_index", "mean"),
    }

    if "metalness" in df.columns:
        agg["metalness"] = ("metalness", "mean")
    if "readability" in df.columns:
        agg["readability"] = ("readability", "mean")
    if "swear_word_ratio" in df.columns:
        agg["swear_word_ratio"] = ("swear_word_ratio", "mean")

    if "song" in df.columns:
        agg["n_songs"] = ("song", "count")
    else:
        agg["n_songs"] = ("lyrics", "count")

    out = (
        df.groupby("artist")
        .agg(**agg)
        .reset_index()
        .sort_values("sentiment", ascending=False)
        .reset_index(drop=True)
    )
    return out


def aggregate_sentiment_by_album(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate sentiment and other metrics by album.
    
    Computes average sentiment per album, and optionally metalness, readability,
    and swear_word_ratio if these columns exist in the input DataFrame.
    
    Args:
        df: DataFrame with 'album', 'artist', and 'sentiment_index' columns, and optionally
            'metalness', 'readability', 'swear_word_ratio', 'release_year', 'album_type'
            
    Returns:
        DataFrame aggregated by album, sorted by sentiment (descending)
    """
    required = ["album", "artist", "sentiment_index"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column '{col}'.")

    agg = {
        "sentiment": ("sentiment_index", "mean"),
    }

    if "metalness" in df.columns:
        agg["metalness"] = ("metalness", "mean")
    if "readability" in df.columns:
        agg["readability"] = ("readability", "mean")
    if "swear_word_ratio" in df.columns:
        agg["swear_word_ratio"] = ("swear_word_ratio", "mean")
    if "release_year" in df.columns:
        agg["release_year"] = ("release_year", "first")
    if "album_type" in df.columns:
        agg["album_type"] = ("album_type", "first")

    albums = (
        df.groupby("album")
        .agg(**agg, artist=("artist", "first"))
        .reset_index()
        .sort_values("sentiment", ascending=False)
        .reset_index(drop=True)
    )
    return albums


def build_stupidity_curve(df: pd.DataFrame, thresholds: np.ndarray, cl_thr: int = 3) -> pd.DataFrame:
    """
    Build the stupidity curve showing relationship between swear words and readability.
    
    For each swear word ratio threshold, computes the percentage of songs that have
    both a swear word ratio >= threshold and a readability <= cl_thr.
    
    Args:
        df: DataFrame with 'swear_word_ratio' and 'readability' columns
        thresholds: Array of swear word ratio thresholds to evaluate
        cl_thr: Coleman-Liau readability threshold (default: 3)
        
    Returns:
        DataFrame with 'swear_word_ratio' and 'stupid_songs_perc' columns
    """
    def percent_stupid(th: float) -> float:
        sub = df[df["swear_word_ratio"] >= th]
        if len(sub) == 0:
            return 0.0
        stupid = sub[sub["readability"] <= cl_thr]
        return round(100.0 * len(stupid) / len(sub), 2)

    return pd.DataFrame({
        "swear_word_ratio": thresholds,
        "stupid_songs_perc": [percent_stupid(r) for r in thresholds]
    })


def top_songs_by_sentiment(df: pd.DataFrame, n: int = 5) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Get top N most positive and most negative songs by sentiment.
    
    Args:
        df: DataFrame with 'sentiment_index' column and optionally 'artist', 'album', 'song'
        n: Number of top songs to return for each category
        
    Returns:
        Tuple of (positive_songs_df, negative_songs_df)
    """
    if "sentiment_index" not in df.columns:
        raise ValueError("Missing column 'sentiment_index'.")

    cols = [c for c in ["artist", "album", "song", "sentiment_index"] if c in df.columns]

    positive = df.sort_values("sentiment_index", ascending=False).head(n)[cols]
    negative = df.sort_values("sentiment_index", ascending=True).head(n)[cols]

    return positive, negative
