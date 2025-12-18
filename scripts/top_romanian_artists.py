#!/usr/bin/env python3
"""
Script to list the top 10 Romanian artists by song count.
"""

import json
import pandas as pd
import argparse

def load_music_data(filepath='data/dataset.json'):
    """Load and process music data from JSON file"""
    
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
        for album_name, album_info in artist_info['albums'].items():
            for song in album_info['songs']:
                # Language is stored as language code (e.g., 'ro' for Romanian)
                language = song.get('language', 'unknown')
                songs_data.append({
                    'artist': artist_name,
                    'album': album_name,
                    'song': song['title'],
                    'language': language
                })
    
    df_songs = pd.DataFrame(songs_data)
    return df_songs

def get_top_romanian_artists(df_songs, top_n=10):
    """Get top N Romanian artists by song count."""
    # Filter for Romanian songs (language code 'ro')
    romanian_songs = df_songs[df_songs['language'] == 'ro'].copy()
    
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
    parser.add_argument("-f", "--filepath", default='data/dataset.json',
                        help="Path to dataset JSON file (default: data/dataset.json)")
    parser.add_argument("-n", "--top", type=int, default=10,
                        help="Number of top artists to display (default: 10)")
    args = parser.parse_args()
    
    print("Loading dataset...")
    df_songs = load_music_data(args.filepath)
    
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

