#!/usr/bin/env python3
"""
Metrics analysis: swear words, readability, and stupidity curves.

Analyzes swear word ratios, readability scores, and their relationships.
"""

import argparse
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loading import load_music_data_with_lyrics, process_metal_songs
from metrics import compute_song_metrics, load_list
from aggregation import aggregate_by_artist, aggregate_by_year, build_stupidity_curve
from visualization import line_plot_show, scatter_plot_show

DEFAULT_JSON = "data/dataset.json"
SWEAR_PATH = "resources/swear_words_eng.txt"
TOP_BANDS = 1000
STUPID_CL_THRESHOLD = 3
RATIO_RANGE = np.arange(0.00, 0.26, 0.01)


def keep_top_bands(df, top_bands):
    """Keep only the top bands by song count."""
    pop = (df.groupby("artist")["artist"].count()
             .reset_index(name="count")
             .sort_values("count", ascending=False)
             .head(top_bands))
    return df[df["artist"].isin(pop["artist"])].copy()


def run(json_path: str, swear_path: str, top_bands: int, seed: int, sample_size: int = None):
    """Main analysis function."""
    print("=" * 70)
    print("WARNING: This analysis performs computationally intensive operations")
    print("(swear word ratio and readability calculations for all songs).")
    print("The computation may take a very long time depending on dataset size.")
    print()
    print("Tip: Use --sample <N> to test with a smaller subset first.")
    print("=" * 70)
    print()
    
    # 1) Load data with lyrics and filter for English metal songs
    df_raw = load_music_data_with_lyrics(json_path)
    df = process_metal_songs(df_raw)

    # 1.5) Sample songs if sample_size is specified
    if sample_size is not None and len(df) > sample_size:
        print(f"Sampling {sample_size} songs from {len(df)} total songs")
        df = df.sample(n=sample_size, random_state=seed).reset_index(drop=True)

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
    """Main function with argument parsing."""
    p = argparse.ArgumentParser(description="Metrics analysis: swear words, readability, stupidity curves.")
    p.add_argument("--json", default=DEFAULT_JSON)
    p.add_argument("--swears", default=SWEAR_PATH)
    p.add_argument("--topbands", type=int, default=TOP_BANDS)
    p.add_argument("--seed", type=int, default=50)
    p.add_argument("--sample", type=int, default=None, help="Number of songs to sample for analysis")
    args = p.parse_args()
    run(args.json, args.swears, args.topbands, args.seed, args.sample)


if __name__ == "__main__":
    main()
