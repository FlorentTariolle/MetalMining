#!/usr/bin/env python3
"""
Script to analyze the lyrics distribution of the metal music dataset, following the guidance of the first article of the Medium.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Language code to name mapping
LANGUAGE_MAP = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'ro': 'Romanian',
    'pt': 'Portuguese',
    'nl': 'Dutch',
    'pl': 'Polish',
    'ru': 'Russian',
    'tr': 'Turkish',
    'ja': 'Japanese',
    'zh': 'Chinese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'sv': 'Swedish',
    'fi': 'Finnish',
    'cs': 'Czech',
    'hu': 'Hungarian',
    'el': 'Greek',
    'ca': 'Catalan',
    'no': 'Norwegian',
    'sl': 'Slovenian',
    'hr': 'Croatian'
}

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
            release_year = album_info.get('release_year', 'Unknown')
            for song in album_info['songs']:
                lyrics = song.get('lyrics', '').strip()
                has_lyrics = bool(lyrics) and len(lyrics) >= 5
                # Language is now pre-calculated in the dataset
                language = song.get('language', 'unknown')
                # Convert language code to readable name if needed
                language = LANGUAGE_MAP.get(language, language) if language != 'unknown' else 'Unknown'
                songs_data.append({
                    'artist': artist_name,
                    'album': album_name,
                    'song': song['title'],
                    'release_year': release_year,
                    'has_lyrics': has_lyrics,
                    'lyrics_status': 'With Lyrics' if has_lyrics else 'Without Lyrics',
                    'language': language
                })
    
    df_songs = pd.DataFrame(songs_data)
    
    album_types = []
    
    for artist_name, artist_info in dataset.items():
        for album_name, album_info in artist_info['albums'].items():
            album_type = album_info.get('album_type', 'Unknown')
            if album_type.lower() == 'demo':
                album_type = 'Demo'
            elif album_type.lower() == 'album':
                album_type = 'Album'
            album_types.append(album_type)
    
    df_albums = pd.DataFrame({'album_type': album_types})
    
    return df_songs, df_albums


def analyze_lyrics_distribution(df_songs, df_albums):
    """Analyze and visualize the distribution of music with and without lyrics"""
    
    # With vs Without Lyrics
    plt.figure(figsize=(8, 6))
    lyrics_counts = df_songs['lyrics_status'].value_counts()
    colors = ['#ff9999', '#66b3ff']
    total = lyrics_counts.sum()
    percentages = [(status, f"{status} ({(count/total*100):.1f}%)") for status, count in lyrics_counts.items()]
    labels = [label for _, label in percentages]
    plt.pie(lyrics_counts.values, colors=colors, startangle=90)
    plt.legend(labels, title="Lyrics Status", loc="center left", bbox_to_anchor=(1, 0.5))
    plt.title('Distribution of Songs: With vs Without Lyrics', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.show()

    # Publication types pie chart
    plt.figure(figsize=(8, 6))
    type_counts = df_albums['album_type'].value_counts()
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#cc99ff']
    total = type_counts.sum()
    percentages = [(type_, f"{type_} ({(count/total*100):.1f}%)") for type_, count in type_counts.items()]
    labels = [label for _, label in percentages]
    plt.pie(type_counts.values, colors=colors[:len(type_counts)], startangle=90)
    plt.legend(labels, title="Publication Types", loc="center left", bbox_to_anchor=(1, 0.5))
    plt.title('Distribution of Publication Types', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.show()

    # Top 10 bands by song count
    plt.figure(figsize=(10, 6))
    top_bands = df_songs['artist'].value_counts().head(10)
    plt.barh(top_bands.index[::-1], top_bands.values[::-1])
    plt.title('Top 10 Bands by Song Count', fontsize=12, fontweight='bold')
    plt.xlabel('Number of Songs')
    plt.ylabel('Bands')
    plt.tight_layout()
    plt.show()
    
    # Top 10 bands by album count
    plt.figure(figsize=(10, 6))
    top_bands_albums = df_songs.groupby('artist')['album'].nunique().sort_values(ascending=False).head(10)
    plt.barh(top_bands_albums.index[::-1], top_bands_albums.values[::-1])
    plt.title('Top 10 Bands by Album Count', fontsize=12, fontweight='bold')
    plt.xlabel('Number of Albums')
    plt.ylabel('Bands')
    plt.tight_layout()
    plt.show()

    # Distribution of songs over the years
    plt.figure(figsize=(12, 6))
    year_data = df_songs[df_songs['release_year'] != 'Unknown'].copy()
    year_data['release_year'] = pd.to_numeric(year_data['release_year'], errors='coerce')
    year_data = year_data.dropna(subset=['release_year'])
    year_counts = year_data['release_year'].value_counts().sort_index()
    
    plt.bar(year_counts.index, year_counts.values)
    plt.title('Distribution of Songs Over the Years', fontsize=12, fontweight='bold')
    plt.xlabel('Release Year')
    plt.ylabel('Number of Songs')
    plt.xticks(year_counts.index, rotation=45)
    plt.tight_layout()
    plt.show()

    # Language distribution for songs with lyrics (Top 4 + Other)
    plt.figure(figsize=(8, 6))
    language_counts = df_songs[df_songs['has_lyrics']]['language'].value_counts()
    top_languages = language_counts.head(4)
    other_count = language_counts[4:].sum() if len(language_counts) > 4 else 0
    if other_count > 0:
        top_languages['Other Languages'] = other_count
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#cc99ff']
    total = top_languages.sum()
    percentages = [(lang, f"{lang} ({(count/total*100):.1f}%)") for lang, count in top_languages.items()]
    labels = [label for _, label in percentages]
    plt.pie(top_languages.values, colors=colors[:len(top_languages)], startangle=90)
    plt.legend(labels, title="Languages", loc="center left", bbox_to_anchor=(1, 0.5))
    plt.title('Distribution of Song Languages (Top 4 + Other)', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.show()

    # Language distribution table (Top 20)
    plt.figure(figsize=(8, 10))
    plt.title('Top 20 Languages in Songs', fontsize=12, fontweight='bold', pad=20)
    language_counts = df_songs[df_songs['has_lyrics']]['language'].value_counts()
    top_20_languages = language_counts.head(20)
    language_table = pd.DataFrame({
        'Language': top_20_languages.index,
        'Song Count': top_20_languages.values,
        'Percentage': (top_20_languages / top_20_languages.sum() * 100).round(1)
    })
    table = plt.table(cellText=language_table.values,
                    colLabels=language_table.columns,
                    loc='center',
                    cellLoc='center',
                    colColours=['#f0f0f0'] * 3)
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    
    return df_songs, df_albums


if __name__ == "__main__":
    df_songs, df_albums = load_music_data()
    analyze_lyrics_distribution(df_songs, df_albums)