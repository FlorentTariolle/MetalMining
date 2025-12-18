#!/usr/bin/env python3
"""
Script to list the top 10 Romanian artists by song count.
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loading import load_music_data


def _get_project_root():
    """Get project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_top_romanian_artists(df_songs, top_n=10):
    """Get top N Romanian artists by song count."""
    # Filter for Romanian songs (language code 'ro' is converted to 'Romanian' by load_music_data)
    romanian_songs = df_songs[df_songs['language'] == 'Romanian'].copy()
    
    if len(romanian_songs) == 0:
        print("No Romanian songs found in the dataset.")
        return None
    
    # Count songs per artist
    artist_counts = romanian_songs['artist'].value_counts()
    
    # Get top N artists
    top_artists = artist_counts.head(top_n)
    
    # Count unique Romanian artists
    num_romanian_artists = len(artist_counts)
    
    return top_artists, len(romanian_songs), num_romanian_artists

def main():
    parser = argparse.ArgumentParser(description="List top Romanian artists by song count")
    parser.add_argument("-f", "--filepath", default=None,
                        help="Path to dataset JSON file (default: data/dataset.json)")
    parser.add_argument("-n", "--top", type=int, default=10,
                        help="Number of top artists to display (default: 10)")
    args = parser.parse_args()
    
    print("Loading dataset...")
    if args.filepath is None:
        args.filepath = os.path.join(_get_project_root(), 'data', 'dataset.json')
    
    # load_music_data returns (df_songs, df_albums) tuple, we only need the songs
    df_songs, _ = load_music_data(args.filepath)
    
    print("Analyzing Romanian artists...")
    result = get_top_romanian_artists(df_songs, args.top)
    
    if result is None:
        return
    
    top_artists, total_romanian_songs, num_romanian_artists = result
    
    print(f"\nTotal Romanian songs in dataset: {total_romanian_songs}")
    print(f"Total Romanian artists in dataset: {num_romanian_artists}")
    print(f"\nTop {len(top_artists)} Romanian Artists by Song Count:")
    print("=" * 60)
    
    for rank, (artist, count) in enumerate(top_artists.items(), 1):
        print(f"{rank:2d}. {artist:40s} {count:5d} songs")

if __name__ == "__main__":
    main()
