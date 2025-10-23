#!/usr/bin/env python3
"""
Script to analyze the lyrics distribution of the metal music dataset, following the guidance of the second article of the Medium.
"""

import argparse
import json
import os
import re
import string
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from readability import ColemanLiauIndex

DEFAULT_JSON = "data/dataset.json"
SWEAR_PATH = "resources/swear_words_eng.txt"
TOP_BANDS = 1000
STUPID_CL_THRESHOLD = 3
RATIO_RANGE = np.arange(0.00, 0.26, 0.01)


def load_list(path: str) -> List[str]:
    """Load a text file (1 element/line) and return a list in lowercase."""
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [ln.strip().lower() for ln in f if ln.strip()]


def load_music_data_with_lyrics(json_path: str) -> pd.DataFrame:
    """Load music data with lyrics directly from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle nested dataset structure
    if 'dataset' in data and 'dataset' in data['dataset']:
        # Double nested: {"dataset": {"dataset": {...}}}
        dataset = data['dataset']['dataset']
    elif 'dataset' in data:
        # Single nested: {"dataset": {...}}
        dataset = data['dataset']
    else:
        # Direct structure: {...}
        dataset = data
    
    rows = []
    for artist, artist_data in dataset.items():
        for album_name, album_data in artist_data.get("albums", {}).items():
            for song in album_data.get("songs", []):
                rows.append({
                    "artist": artist,
                    "album": album_name,
                    "song": song.get("title", ""),
                    "lyrics": (song.get("lyrics", "") or "").strip(),
                    "language": song.get("language", "unknown"),
                    "release_year": album_data.get("release_year", "Unknown"),
                    "album_type": album_data.get("album_type", "Unknown")
                })
    
    df = pd.DataFrame(rows)
    df["has_lyrics"] = df["lyrics"].str.len() >= 5
    df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")
    return df


def process_metal_songs(df: pd.DataFrame) -> pd.DataFrame:
    """Filter for English songs with lyrics."""
    # Simple filtering: only English songs with lyrics
    mask = (df["language"] == "en") & (df["lyrics"].fillna("").str.len() >= 5)
    return df.loc[mask].copy()

def _prep_text(text: str) -> str:
    """Clean text: lowercase, replace \n, remove punctuation (replaced with spaces)."""
    t = (text or "").lower().replace("\\n", " ")
    return t.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))


def swear_ratio(text: str, swear_words: List[str]) -> float:
    """Calculate swear word ratio: exact occurrences / total number of tokens."""
    t = _prep_text(text)
    toks = [w for w in t.split() if w]
    if not toks:
        return 0.0
    total = 0
    for w in swear_words:
        total += len(list(re.finditer(rf"\b{re.escape(w)}\b", t)))
    return total / len(toks)


def readability_cl(text: str) -> int:
    """Calculate Coleman–Liau index (integer ≥ 1)."""
    t = (text or "").replace("\\n", " ")
    try:
        return max(1, int(ColemanLiauIndex(t).grade_level))
    except Exception:
        return 1


def compute_song_metrics(df: pd.DataFrame, swears: List[str]) -> pd.DataFrame:
    """Compute swear word ratio and readability for each song."""
    out = df.copy()
    out["swear_word_ratio"] = out["lyrics"].apply(lambda t: swear_ratio(t, swears))
    out["readability"] = out["lyrics"].apply(readability_cl)
    return out


def keep_top_bands(df: pd.DataFrame, top_bands: int) -> pd.DataFrame:
    """Keep only the top bands by song count."""
    pop = (df.groupby("artist")["artist"].count()
             .reset_index(name="count")
             .sort_values("count", ascending=False)
             .head(top_bands))
    return df[df["artist"].isin(pop["artist"])].copy()


def aggregate_by_artist(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate metrics by artist."""
    return (df.groupby("artist")
              .agg(average_swear_word_ratio=("swear_word_ratio", "mean"),
                   average_readability_index=("readability", "mean"),
                   n_songs=("song", "count"))
              .reset_index())


def aggregate_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate metrics by release year."""
    return (df.groupby("release_year")
              .agg(average_swear_word_ratio=("swear_word_ratio", "mean"),
                   average_readability_index=("readability", "mean"))
              .reset_index()
              .sort_values("release_year"))


def build_stupidity_curve(df: pd.DataFrame, thresholds: np.ndarray, cl_thr: int = STUPID_CL_THRESHOLD) -> pd.DataFrame:
    """Build the stupidity curve showing relationship between swear words and readability."""
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

def line_plot_show(df: pd.DataFrame, x: str, y: str, xlabel: str, ylabel: str, title: str, figsize=(12, 6)) -> None:
    """Plot a simple line chart and display it."""
    plt.figure(figsize=figsize)
    plt.plot(df[x].values, df[y].values, marker="o")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.show()


def scatter_plot_show(df: pd.DataFrame, x: str, y: str, xlabel: str, ylabel: str, title: str, figsize=(10, 10)) -> None:
    """Plot a simple scatter plot and display it."""
    plt.figure(figsize=figsize)
    plt.scatter(df[x].values, df[y].values, s=25, alpha=0.7)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.show()

def run(json_path: str, swear_path: str, top_bands: int, seed: int) -> None:
    """Main analysis function with improved logic and output."""
    # 1) Load data with lyrics and filter for English metal songs
    df_raw = load_music_data_with_lyrics(json_path)
    df = process_metal_songs(df_raw)

    # 2) Keep only top bands by song count
    df = keep_top_bands(df, top_bands)

    # 3) Compute metrics for each song
    swears = load_list(swear_path)
    df = compute_song_metrics(df, swears)

    # 4) Aggregate by artist and year
    artists = aggregate_by_artist(df)
    yearly = aggregate_by_year(df)

    # 5) Print detailed statistics
    print("\nTop 10 songs by swear_word_ratio:")
    print(df.sort_values("swear_word_ratio", ascending=False)[
        ["artist", "song", "swear_word_ratio"]
    ].head(10).to_string(index=False))

    print("\nTop 10 songs by readability (highest = more difficult):")
    print(df.sort_values("readability", ascending=False)[
        ["artist", "song", "readability"]
    ].head(10).to_string(index=False))

    print("\nTop 10 artists by average_swear_word_ratio:")
    print(artists.sort_values("average_swear_word_ratio", ascending=False)[
        ["artist", "average_swear_word_ratio", "n_songs"]
    ].head(10).to_string(index=False))

    print("\nTop 10 artists by average_readability_index:")
    print(artists.sort_values("average_readability_index", ascending=False)[
        ["artist", "average_readability_index", "n_songs"]
    ].head(10).to_string(index=False))

    # 6) Display visualizations
    sample_n = min(150, len(artists))
    if sample_n > 0:
        scatter_plot_show(
            artists.sample(n=sample_n, random_state=seed),
            x="average_readability_index",
            y="average_swear_word_ratio",
            xlabel="Coleman–Liau readability score",
            ylabel="Fraction of swear words in lyrics",
            title="Swear words vs Coleman–Liau (artists)",
        )

    line_plot_show(
        yearly, "release_year", "average_swear_word_ratio",
        "Release year", "Average swear words ratio",
        "Evolution of average swear words ratio in metal lyrics",
    )
    line_plot_show(
        yearly, "release_year", "average_readability_index",
        "Release year", "Average Coleman–Liau score",
        "Evolution of average Coleman–Liau score of metal lyrics",
    )

    # 7) Build and display stupidity curve
    curve = build_stupidity_curve(df, RATIO_RANGE, STUPID_CL_THRESHOLD)
    line_plot_show(
        curve, "swear_word_ratio", "stupid_songs_perc",
        "Swear word ratio", 'Percent of "stupid songs"',
        'Proportionality between swear word ratio and percent of "stupid songs"',
    )


def main():
    """Main function with improved argument parsing."""
    p = argparse.ArgumentParser(description="Episode II — words, readability, stupidity (display only).")
    p.add_argument("--json", default=DEFAULT_JSON)
    p.add_argument("--swears", default=SWEAR_PATH)
    p.add_argument("--topbands", type=int, default=TOP_BANDS)
    p.add_argument("--seed", type=int, default=50)
    args = p.parse_args()
    run(args.json, args.swears, args.topbands, args.seed)

if __name__ == "__main__":
    main()
