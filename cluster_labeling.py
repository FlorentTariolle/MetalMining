#!/usr/bin/env python3
"""
Runs the existing MRSW clustering and annotates each cluster with the most common genres
from the labeled `bands_genres_cleaned.json` dictionary by applying a majority-vote rule.
"""

import argparse
import json
import os
from collections import Counter

import pandas as pd

from analyzer2 import load_list
from clustering_MRSW import (
    calculate_metrics,
    cluster_artists,
    csv_cache_path,
    plot_artist_clusters,
    top_bands_by_album_count,
    swear_path,
)
from metalness_loader import load_metalness_df
from process_wordcloud_metalness import load_music_data_with_lyrics, process_metal_songs


def load_cached_or_source_data(filepath: str | None) -> pd.DataFrame:
    if os.path.exists(csv_cache_path) and filepath is None:
        print(f"[INFO] Loading cached data from '{csv_cache_path}'...")
        return pd.read_csv(csv_cache_path)
    filepath = filepath or "data/dataset.json"
    print("[INFO] Cache not found or custom file provided. Loading from JSON...")
    songs_df = load_music_data_with_lyrics(filepath)
    songs_df.to_csv(csv_cache_path, index=False)
    print(f"[INFO] Data cached to '{csv_cache_path}'")
    return songs_df


def load_genres_lookup(json_path: str) -> dict[str, list[str]]:
    with open(json_path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    genres_lookup: dict[str, list[str]] = {}
    for artist, genres in raw.items():
        if not genres:
            continue
        normalized = [g.strip() for g in genres if isinstance(g, str) and g.strip()]
        if normalized:
            genres_lookup[artist] = normalized
    return genres_lookup


def label_clusters_with_genres(
    artist_df: pd.DataFrame, genres_lookup: dict[str, list[str]], top_k: int = 2
) -> pd.DataFrame:
    records = []
    for cluster_id, group in artist_df.groupby("cluster"):
        genre_counter = Counter()
        for artist in group.index:
            genre_counter.update(genres_lookup.get(artist, []))

        if cluster_id == -1 and not genre_counter:
            label = "Noise"
        elif genre_counter:
            label = " / ".join([genre for genre, _ in genre_counter.most_common(top_k)])
        else:
            label = "Unknown"

        records.append(
            {
                "cluster_id": cluster_id,
                "label": label,
                "genre_support": sum(genre_counter.values()),
                "cluster_size": len(group),
                "top_artists": ";".join(group.sort_values("metalness", ascending=False).head(3).index),
            }
        )

    return pd.DataFrame(records).sort_values("cluster_id").reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run MRSW clustering and label clusters with genres.")
    parser.add_argument(
        "-f",
        "--filepath",
        default=None,
        help="Path to the source JSON dataset (default: data/dataset.json).",
    )
    parser.add_argument(
        "-t",
        "--top-artists",
        type=int,
        default=100,
        help="How many artists (by album count) to include in the clustering.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output_pics",
        help="Directory to save the clustering visuals.",
    )
    parser.add_argument(
        "-g",
        "--genres",
        default="data/bands_genres_cleaned.json",
        help="Path to the JSON file mapping artists to genres.",
    )
    parser.add_argument(
        "-l",
        "--labels-output",
        default="output_data/cluster_labels.csv",
        help="Path where the generated labels summary should be saved.",
    )

    args = parser.parse_args()

    swears = load_list(swear_path)
    songs_df = load_cached_or_source_data(args.filepath)
    metal_df = process_metal_songs(songs_df)
    metalness_df = load_metalness_df()
    metalness_scores = pd.Series(metalness_df.Metalness.values, index=metalness_df.Word).to_dict()
    top_artists = top_bands_by_album_count(metal_df, top_bands=args.top_artists)
    metrics_df = calculate_metrics(top_artists, metalness_scores, swears)
    artist_summary = metrics_df.groupby("artist")[["metalness", "readability", "swear_word_ratio"]].mean()
    clustered_artists = cluster_artists(artist_summary, ["metalness"])

    genres_lookup = load_genres_lookup(args.genres)
    labeled_clusters = label_clusters_with_genres(clustered_artists, genres_lookup)

    label_map = labeled_clusters.set_index("cluster_id")["label"].to_dict()
    plot_artist_clusters(
        clustered_artists,
        args.output,
        "artist_clusters_optics_Metalness.png",
        "Artist Clustering Metalness",
        label_map,
    )

    os.makedirs(os.path.dirname(args.labels_output) or ".", exist_ok=True)
    labeled_clusters.to_csv(args.labels_output, index=False)
    print(f"Cluster labels saved to {args.labels_output}")


if __name__ == "__main__":
    main()

