#!/usr/bin/env python3
"""
TF-IDF based metallitude computation.

Computes metallitude scores using TF-IDF approach (TF on Metal, IDF on Non-Metal).
"""

import argparse
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loading import load_music_data_with_lyrics, process_metal_songs, process_non_metal_songs
from metrics.metallitude import process_idf_scores


def _get_project_root():
    """Get project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    """Run TF-IDF metallitude analysis."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filepath", default=None, help="path to dataset in json format")
    parser.add_argument('-o', "--output", default=None, help="path to output csv metalness ranking")

    args = parser.parse_args()
    project_root = _get_project_root()
    csv_cache_path = os.path.join(project_root, "cache", "lyrics_data.csv")

    # Load metal dataset
    if os.path.exists(csv_cache_path) and args.filepath is None:
        print(f"[INFO] Loading cached data from '{csv_cache_path}'...")
        df_songs = pd.read_csv(csv_cache_path)
    else:
        print("[INFO] Cache not found or custom file provided. Loading from JSON...")
        filepath = args.filepath if args.filepath is not None else os.path.join(project_root, 'data', 'dataset.json')
        df_songs = load_music_data_with_lyrics(filepath)
        df_songs.to_csv(csv_cache_path, index=False)
        print(f"[INFO] Data cached to '{csv_cache_path}'")

    # Load non-metal dataset
    try:
        non_metal_dataset = pd.read_csv(os.path.join(project_root, "cache", "non_metal_lyrics.csv"))
    except FileNotFoundError:
        print("Warning: Non-metal dataset not found. Creating empty dataset.")
        non_metal_dataset = pd.DataFrame(columns=['Lyric', 'language'])

    # Process songs
    metal_df = process_metal_songs(df_songs)
    non_metal_df = process_non_metal_songs(non_metal_dataset)
    
    # Compute metallitude
    output_path = args.output if args.output else os.path.join(project_root, "output_data", "metallitude.csv")
    process_idf_scores(metal_df, non_metal_df, output=output_path)


if __name__ == "__main__":
    main()
