#!/usr/bin/env python3
"""
Script to extract the top 50 bands by song count from the dataset.
"""

import json
import pandas as pd
import argparse

DEFAULT_JSON = "data/dataset.json"
TOP_N = 100


def load_music_data(filepath: str) -> pd.DataFrame:
    """Load and process music data from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
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
    
    songs_data = []
    
    for artist_name, artist_info in dataset.items():
        for album_name, album_info in artist_info.get('albums', {}).items():
            for song in album_info.get('songs', []):
                songs_data.append({
                    'artist': artist_name,
                    'album': album_name,
                    'song': song.get('title', '')
                })
    
    df = pd.DataFrame(songs_data)
    return df


def get_top_bands(df: pd.DataFrame, top_n: int = TOP_N) -> list:
    """Get the top N bands by song count."""
    # Count songs per artist
    artist_counts = df['artist'].value_counts()
    
    # Get top N artists
    top_bands = artist_counts.head(top_n)
    
    # Return list of band names
    return top_bands.index.tolist()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Extract top bands by song count")
    parser.add_argument("-f", "--filepath", default=DEFAULT_JSON,
                        help=f"Path to dataset JSON file (default: {DEFAULT_JSON})")
    parser.add_argument("-n", "--top", type=int, default=TOP_N,
                        help=f"Number of top bands to extract (default: {TOP_N})")
    args = parser.parse_args()
    
    print(f"Loading dataset from {args.filepath}...")
    df = load_music_data(args.filepath)
    
    print(f"Calculating top {args.top} bands by song count...")
    top_bands = get_top_bands(df, args.top)
    
    print(f"\nTop {len(top_bands)} bands:")
    print("=" * 60)
    for i, band in enumerate(top_bands, 1):
        count = df[df['artist'] == band].shape[0]
        print(f"{i:2d}. {band:40s} ({count} songs)")
    
    return top_bands


if __name__ == "__main__":
    top_bands_list = main()
    # The list is returned and can be used programmatically
    # print(f"\nList of top bands: {top_bands_list}")
