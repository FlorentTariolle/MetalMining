"""Visualization functions for sentiment analysis."""

import pandas as pd
import matplotlib.pyplot as plt


def plot_sentiment_distribution(df: pd.DataFrame, title: str = "Metal songs") -> None:
    """
    Plot histogram of sentiment distribution.
    
    Args:
        df: DataFrame with 'sentiment_index' column
        title: Title prefix for the plot
    """
    if "sentiment_index" not in df.columns:
        return

    plt.figure(figsize=(10, 6))
    df["sentiment_index"].hist(bins=40)
    plt.title(f"Sentiment distribution – {title}")
    plt.xlabel("Sentiment (VADER compound)")
    plt.ylabel("Songs")
    plt.tight_layout()
    plt.show()


def plot_artist_scatter_metalness_sentiment(df: pd.DataFrame) -> None:
    """
    Plot scatter plot of metalness vs sentiment for artists.
    
    Args:
        df: DataFrame with 'metalness' and 'sentiment' columns
    """
    if "metalness" not in df.columns or "sentiment" not in df.columns:
        return

    plt.figure(figsize=(10, 7))
    plt.scatter(df["metalness"], df["sentiment"], alpha=0.7, s=30)
    plt.xlabel("Metalness")
    plt.ylabel("Sentiment (average VADER)")
    plt.title("Artists: metalness vs sentiment")
    plt.tight_layout()
    plt.show()


def build_emotional_arc(df: pd.DataFrame, artist: str) -> pd.DataFrame:
    """
    Build emotional arc for an artist showing sentiment progression across albums.
    
    Args:
        df: DataFrame with 'artist', 'album', 'sentiment_index', and optionally 'release_year'
        artist: Artist name to build arc for
        
    Returns:
        DataFrame with album sentiment averages, optionally sorted by release year
    """
    required = ["artist", "album", "sentiment_index"]
    for col in required:
        if col not in df.columns:
            raise ValueError("Missing required columns.")

    subset = df[df["artist"] == artist]
    if subset.empty:
        raise ValueError(f"No songs for '{artist}'.")

    arc = (
        subset.groupby("album")["sentiment_index"]
        .mean()
        .reset_index()
        .rename(columns={"sentiment_index": "average_sentiment"})
    )

    if "release_year" in subset.columns:
        years = subset.groupby("album")["release_year"].min().reset_index()
        arc = arc.merge(years, on="album", how="left")
        arc = arc.sort_values(["release_year", "album"]).reset_index(drop=True)
    else:
        arc = arc.sort_values("album").reset_index(drop=True)

    return arc


def plot_emotional_arc(arc_df: pd.DataFrame, artist: str) -> None:
    """
    Plot emotional arc for an artist.
    
    Args:
        arc_df: DataFrame from build_emotional_arc()
        artist: Artist name for the plot title
    """
    if arc_df.empty:
        return

    plt.figure(figsize=(10, 5))
    x = range(len(arc_df))
    plt.plot(x, arc_df["average_sentiment"], marker="o")
    plt.xticks(x, arc_df["album"], rotation=45, ha="right")
    plt.title(f"Emotional arc – {artist}")
    plt.xlabel("Album")
    plt.ylabel("Average sentiment (VADER)")
    plt.tight_layout()
    plt.show()


def build_sentiment_path(df: pd.DataFrame, artist: str) -> pd.DataFrame:
    """
    Build sentiment path showing evolution of sentiment and metalness across albums.
    
    Args:
        df: DataFrame with 'artist', 'album', 'sentiment_index', 'metalness', and optionally 'release_year'
        artist: Artist name to build path for
        
    Returns:
        DataFrame with album-level sentiment and metalness, optionally sorted by release year
    """
    required = ["artist", "album", "sentiment_index", "metalness"]
    for col in required:
        if col not in df.columns:
            raise ValueError("Missing required columns for sentiment path.")

    subset = df[df["artist"] == artist]
    if subset.empty:
        raise ValueError(f"No songs for '{artist}'.")

    grouped = (
        subset.groupby("album")
        .agg(
            sentiment=("sentiment_index", "mean"),
            metalness=("metalness", "mean"),
            release_year=("release_year", "min"),
        )
        .reset_index()
    )

    if "release_year" in grouped.columns:
        grouped = grouped.sort_values("release_year").reset_index(drop=True)

    return grouped


def plot_sentiment_path(df_path: pd.DataFrame, artist: str) -> None:
    """
    Plot sentiment path showing evolution in metalness-sentiment space.
    
    Args:
        df_path: DataFrame from build_sentiment_path()
        artist: Artist name for the plot title
    """
    if df_path.empty:
        return

    plt.figure(figsize=(12, 8))
    x = df_path["metalness"]
    y = df_path["sentiment"]

    plt.plot(x, y, marker="o", linewidth=1.5)

    for _, row in df_path.iterrows():
        plt.text(
            row["metalness"] + 0.001,
            row["sentiment"] + 0.001,
            row["album"],
            fontsize=9,
        )

    plt.xlabel("Metalness (avg per album)")
    plt.ylabel("Sentiment (avg per album)")
    plt.title(f"Sentiment path – {artist}")
    plt.tight_layout()
    plt.show()
