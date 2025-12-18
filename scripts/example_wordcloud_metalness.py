#!/usr/bin/env python3
"""
Example script: Word cloud generation and metalness computation.

This script demonstrates how to use the refactored modules to generate
word clouds and compute metalness scores based on word frequencies.
"""

import argparse
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loading import load_music_data_with_lyrics, process_metal_songs, process_non_metal_songs
from metrics.metalness import compute_metalness
from visualization import (
    plot_word_cloud,
    plot_word_cloud_Debauchery,
    get_word_frequence_distribution,
)


def _get_project_root():
    """Get project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    """Run word cloud and metalness analysis."""
    parser = argparse.ArgumentParser(description="Analyze lyrics data from a JSON file.")
    parser.add_argument("-f", "--filepath", default=None,
                        help="Path to json file (ex: `data/dataset.json`).")
    parser.add_argument("-o", "--output", default=None,
                        help="Path to output image. If not provided, image won't be saved.")
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

    # Create output directories if they don't exist
    os.makedirs(os.path.join(project_root, "output_data"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "output_pics"), exist_ok=True)
    
    # Process songs
    df_metal_songs = process_metal_songs(df_songs)
    df_non_metal_songs = process_non_metal_songs(non_metal_dataset)
    
    # Compute word frequency distributions
    metal_word_freq_dist = get_word_frequence_distribution(df_metal_songs, text_column='lyrics')
    non_metal_word_freq_dist = get_word_frequence_distribution(df_non_metal_songs, text_column='Lyric')
    
    # Compute metalness
    words_metalness_df = compute_metalness(metal_word_freq_dist, non_metal_word_freq_dist).sort_values(
        by='metalness', ascending=False
    ).reset_index().drop(columns='index')
    
    # Save metalness scores
    words_metalness_df.to_csv(os.path.join(project_root, "output_data", "words_metalness.csv"))
    words_metalness_top100 = words_metalness_df.head(100)
    words_metalness_bot100 = words_metalness_df.tail(100)
    words_metalness_top100.to_csv(os.path.join(project_root, "output_data", "words_metalness_top100.csv"))
    words_metalness_bot100.to_csv(os.path.join(project_root, "output_data", "words_metalness_bot100.csv"))
    
    # Generate word clouds
    plot_word_cloud(metal_word_freq_dist, args.output)
    plot_word_cloud(non_metal_word_freq_dist, os.path.join(project_root, "output_pics", "non_metal_wordcloud.png"))
    plot_word_cloud_Debauchery(df_metal_songs)


if __name__ == "__main__":
    main()
