"""Functions for loading music dataset from JSON files."""

import json
import pandas as pd
from tqdm import tqdm
from typing import Tuple

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


def load_music_data(filepath: str = 'data/dataset.json') -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load and process music data from JSON file.
    
    Returns a tuple of (songs DataFrame, albums DataFrame).
    The songs DataFrame includes basic metadata, while albums DataFrame
    includes album type information.
    """
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


def load_music_data_with_lyrics(filepath: str = 'data/dataset.json') -> pd.DataFrame:
    """
    Load and process music data from a JSON file, including lyrics and pre-calculated language.

    Args:
        filepath (str): Path to the JSON data file.

    Returns:
        pd.DataFrame: Processed DataFrame containing song metadata and lyrics.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    songs_data = []

    # Handle nested dataset structure
    if 'dataset' in data and 'dataset' in data['dataset']:
        dataset = data['dataset']['dataset']
    elif 'dataset' in data:
        dataset = data['dataset']
    else:
        dataset = data

    total_songs = sum(
        len(album_info.get('songs', []))
        for artist_info in dataset.values()
        for album_info in artist_info.get('albums', {}).values()
    )

    with tqdm(total=total_songs, desc='Loading songs', unit='song') as pbar:
        for artist_name, artist_info in dataset.items():
            for album_name, album_info in artist_info.get('albums', {}).items():
                release_year = album_info.get('release_year', 'Unknown')
                for song in album_info.get('songs', []):
                    lyrics = song.get('lyrics', '').strip()
                    has_lyrics = bool(lyrics) and len(lyrics) >= 5
                    # Language is now pre-calculated in the dataset
                    language = song.get('language', 'unknown')
                    # Convert language code to readable name if needed
                    language = LANGUAGE_MAP.get(language, language) if language != 'unknown' else 'Unknown'
                    songs_data.append({
                        'artist': artist_name,
                        'album': album_name,
                        'song': song.get('title', ''),
                        'release_year': release_year,
                        'has_lyrics': has_lyrics,
                        'lyrics_status': 'With Lyrics' if has_lyrics else 'Without Lyrics',
                        'language': language,
                        'lyrics': lyrics,
                        'album_type': album_info.get('album_type', 'Unknown')
                    })
                    pbar.update(1)

    df_songs = pd.DataFrame(songs_data)
    return df_songs
