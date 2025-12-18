#!/usr/bin/env python3
"""
Sentiment analysis with metalness and emotional arcs.

Analyzes sentiment, metalness, and emotional progression of artists.
"""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loading import load_music_data_with_lyrics, process_metal_songs
from metrics import add_sentiment_index, compute_songs_metalness_from_lyrics
from metrics.sentiment import ensure_nltk_resources
from aggregation import aggregate_sentiment_by_artist, aggregate_sentiment_by_album, top_songs_by_sentiment
from visualization import (
    plot_sentiment_distribution,
    plot_artist_scatter_metalness_sentiment,
    build_emotional_arc,
    plot_emotional_arc,
    build_sentiment_path,
    plot_sentiment_path,
)
from utils.metalness_loader import load_metalness_df


def _get_project_root():
    """Get project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    """Run sentiment analysis."""
    project_root = _get_project_root()
    
    # Load metal dataset
    try:
        metal_df = pd.read_csv(os.path.join(project_root, "cache", "lyrics_data.csv"))
    except FileNotFoundError:
        print("Warning: Metal dataset not found. Creating cache")
        metal_df = load_music_data_with_lyrics(os.path.join(project_root, "data", "dataset.json"))

    # Load metalness scores
    try:
        words_metalness_df = load_metalness_df()
        metal_dict = dict(zip(words_metalness_df["Word"].str.lower(), words_metalness_df["Metalness"]))
        metal_df["metalness"] = metal_df["lyrics"].fillna("").apply(
            lambda x: compute_songs_metalness_from_lyrics(x, metal_dict))
    except FileNotFoundError:
        print("Warning: Words metalness dataset not found. Please compute metalness first.")
        metal_df["metalness"] = None

    # Process songs
    metal_df = process_metal_songs(metal_df)

    # Compute sentiment
    ensure_nltk_resources()
    cache_path = os.path.join(project_root, "cache", "lyrics_with_sentiment.csv")
    if os.path.exists(cache_path):
        print("Loading cached sentiment data...")
        metal_with_sent = pd.read_csv(cache_path)
    else:
        print("Sentiment cache not found. Computing sentiment.")
        metal_with_sent = add_sentiment_index(metal_df)
        metal_with_sent.to_csv(cache_path, index=False)
        print("Sentiment data saved to", cache_path)

    # Top songs by sentiment
    pos, neg = top_songs_by_sentiment(metal_with_sent, n=5)
    print("\nTOP POSITIVE SONGS:\n", pos.to_string(index=False))
    print("\nTOP NEGATIVE SONGS:\n", neg.to_string(index=False))

    # Aggregate by artist and album
    artists_sent = aggregate_sentiment_by_artist(metal_with_sent)
    print("\nARTISTS SENTIMENT:\n", artists_sent.head(10).to_string(index=False))

    albums_sent = aggregate_sentiment_by_album(metal_with_sent)
    print("\nALBUMS SENTIMENT:\n", albums_sent.head(10).to_string(index=False))

    # Visualizations
    plot_sentiment_distribution(metal_with_sent)
    plot_artist_scatter_metalness_sentiment(artists_sent)

    # Emotional arcs for specific artists
    try:
        arc = build_emotional_arc(metal_with_sent, "Opeth")
        plot_emotional_arc(arc, "Opeth")
    except Exception as exc:
        print("Error building emotional arc:", exc)

    try:
        path_df = build_sentiment_path(metal_with_sent, "Opeth")
        plot_sentiment_path(path_df, "Opeth")
    except Exception as exc:
        print("Error building sentiment path:", exc)


if __name__ == "__main__":
    main()
