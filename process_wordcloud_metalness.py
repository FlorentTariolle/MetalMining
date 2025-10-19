#!/usr/bin/env python3

import json
import os
from langdetect import detect
from langdetect import LangDetectException
from wordcloud import WordCloud
from analyzer import LANGUAGE_MAP
import argparse
import numpy as np
from tqdm import tqdm
import nltk

nltk.download('punkt', quiet=True)
try:
    nltk.download('punkt_tab', quiet=True)
except Exception:
    pass

from nltk.tokenize import RegexpTokenizer
from nltk import FreqDist
import string
import pandas as pd
import matplotlib.pyplot as plt

csv_cache_path = "cache/lyrics_data.csv"
non_metal_dataset = pd.read_csv("cache/non_metal_lyrics.csv")


def load_music_data_with_lyrics(filepath='data/progress2.json'):
    """
    Load and process music data from a JSON file, including lyrics and language detection.

    Args:
        filepath (str): Path to the JSON data file.

    Returns:
        pd.DataFrame: Processed DataFrame containing song metadata and lyrics.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    songs_data = []

    total_songs = sum(
        len(album_info.get('songs', []))
        for artist_info in data.get('dataset', {}).values()
        for album_info in artist_info.get('albums', {}).values()
    )

    with tqdm(total=total_songs, desc='Loading songs', unit='song') as pbar:
        for artist_name, artist_info in data.get('dataset', {}).items():
            for album_name, album_info in artist_info.get('albums', {}).items():
                release_year = album_info.get('release_year', 'Unknown')
                for song in album_info.get('songs', []):
                    lyrics = song.get('lyrics', '').strip()
                    has_lyrics = bool(lyrics) and len(lyrics) >= 5
                    if has_lyrics:
                        try:
                            language = detect(lyrics)
                        except LangDetectException:
                            language = 'None'
                    else:
                        language = 'None'
                    language = LANGUAGE_MAP.get(language, language) if language != 'None' else 'None'
                    songs_data.append({
                        'artist': artist_name,
                        'album': album_name,
                        'song': song.get('title', ''),
                        'release_year': release_year,
                        'has_lyrics': has_lyrics,
                        'lyrics_status': 'With Lyrics' if has_lyrics else 'Without Lyrics',
                        'language': language,
                        'lyrics': lyrics
                    })
                    pbar.update(1)

    df_songs = pd.DataFrame(songs_data)
    return df_songs


STOPWORDS = list(set([str(line.rstrip('\n')) for line in open("resources/stopwords_eng.txt", "r")]))
PUNCTUATION = list(string.punctuation) + ['..', '...', '’', "''", '``', '`']

def drop_songs_with_no_lyrics(dataframe):
    """
    Drop all songs without lyrics from the given DataFrame.

    Args:
        dataframe (pd.DataFrame): Input DataFrame containing song data.

    Returns:
        pd.DataFrame: DataFrame with only songs that have lyrics.
    """
    initial_count = len(dataframe)
    dataframe = dataframe[dataframe['has_lyrics']]
    final_count = len(dataframe)
    print(f"Dropped {initial_count - final_count} songs without lyrics.")
    return dataframe


def drop_songs_that_are_not_english(dataframe):
    """
    Drop all songs that are not in English from the given DataFrame.

    Args:
        dataframe (pd.DataFrame): Input DataFrame containing song data.

    Returns:
        pd.DataFrame: DataFrame with only English-language songs.
    """
    initial_count = len(dataframe)
    dataframe = dataframe[dataframe['language'] == 'English']
    final_count = len(dataframe)
    print(f"Dropped {initial_count - final_count} songs that are not in English.")
    return dataframe


def process_metal_songs(dataframe):
    df = dataframe.copy()
    df = drop_songs_with_no_lyrics(df)
    df = drop_songs_that_are_not_english(df)
    return df

def process_non_metal_songs(dataframe):
    df = dataframe.copy()
    df_english = df[df['language'] == 'en']
    print(f"Non-metal songs before filtering: {len(df)}, after filtering for English: {len(df_english)}")
    return df_english



def get_word_frequence_distribution(df, text_column='lyrics'):
    """
    Compute word frequency distribution from a text column in the DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing the text data.
        text_column (str): Column name containing the text (lyrics).

    Returns:
        FreqDist: NLTK frequency distribution of words.
    """
    words_corpus = " ".join(df[text_column].dropna().astype(str).values)
    words_corpus = words_corpus.lower().replace('\\n', ' ')
    try:
        tokens = nltk.word_tokenize(words_corpus)
    except LookupError:
        nltk.download('punkt', quiet=True)
        try:
            tokens = nltk.word_tokenize(words_corpus)
        except LookupError:
            tokenizer = RegexpTokenizer(r'\w+')
            tokens = tokenizer.tokenize(words_corpus)

    word_freq_dist = FreqDist(tokens)

    # remove punctuation and stopwords
    for stopword in STOPWORDS:
        if stopword in word_freq_dist:
            del word_freq_dist[stopword]

    for punctuation in PUNCTUATION:
        if punctuation in word_freq_dist:
            del word_freq_dist[punctuation]

    return word_freq_dist


def plot_word_cloud(freq, output_path=None):
    """
    Generate and either save the image or not depending on output_path.

    Args:
        freq (FreqDist): Word frequency distribution.
        output_path (str, optional): Path to save the word cloud image.
                                     If None, the image will not be saved.
    """
    wordcloud = WordCloud(width=800, height=400, background_color='black').generate_from_frequencies(freq)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Lyrics', fontsize=20)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, bbox_inches='tight')
        print(f"Word cloud saved to {output_path}")


def plot_word_cloud_Debauchery(dataframe):
    """
    Generate and display a word cloud for Linkin Park lyrics.
    """
    Debauchery_songs = dataframe[dataframe['artist'] == 'Debauchery']
    Debauchery_word_freq_dist = get_word_frequence_distribution(Debauchery_songs, text_column='lyrics')
    plot_word_cloud(Debauchery_word_freq_dist)
    print(Debauchery_word_freq_dist.most_common(20))
    plt.savefig("output_pics/Debauchery_wordcloud.png", bbox_inches='tight')

def compute_metalness(wfd_metal, wfd_non_metal):
    no_metal_wfd = {k:v for k,v in wfd_non_metal.items() if v >= 5}
    metal_wfd = {k:v for k,v in wfd_metal.items() if v >= 5}
    metalness  = {}

    for word in tqdm(metal_wfd.keys() & no_metal_wfd.keys(), desc="Computing metalness", unit="word"):
        if len(word)>2:
            metalness_coeff = np.log((metal_wfd[word])/(no_metal_wfd[word]))
            metalness[word] = 1 / (1 + np.exp(-metalness_coeff))

    metalness_df = pd.DataFrame({
        'words': list(metalness.keys()),
        'metalness': list(metalness.values())
    })

    return metalness_df



if __name__ == "__main__":
    """
    Main execution flow:
    - Parses arguments for input JSON and optional output image path.
    - Loads and filters song lyrics data.
    - Computes word frequencies.
    - Plots or saves the word cloud.
    - Prints the top 20 most common words.
    """
    parser = argparse.ArgumentParser(description="Analyze lyrics data from a JSON file.")
    parser.add_argument("-f", "--filepath",default = None,
                        help="Path to json file (ex: `data/progress2.json`).")
    parser.add_argument("-o", "--output", default=None,
                        help="Path to output image. If not provided, image won't be saved.")
    args = parser.parse_args()

    if os.path.exists(csv_cache_path) and args.filepath is None:
        print(f"[INFO] Loading cached data from '{csv_cache_path}'...")
        df_songs = pd.read_csv(csv_cache_path)
    else:
        print("[INFO] Cache not found or custom file provided. Loading from JSON...")
        df_songs = load_music_data_with_lyrics(args.filepath)
        df_songs.to_csv(csv_cache_path, index=False)
        print(f"[INFO] Data cached to '{csv_cache_path}'")

    df_metal_songs = process_metal_songs(df_songs)
    df_non_metal_songs = process_non_metal_songs(non_metal_dataset)
    metal_word_freq_dist = get_word_frequence_distribution(df_metal_songs, text_column='lyrics')
    non_metal_word_freq_dist = get_word_frequence_distribution(df_non_metal_songs, text_column='Lyric')
    words_metalness_df = compute_metalness(metal_word_freq_dist, non_metal_word_freq_dist).sort_values(by='metalness', ascending=False).reset_index().drop(columns='index')
    words_metalness_df.to_csv("output_data/words_metalness.csv")
    words_metalness_top100 = words_metalness_df.head(100)
    words_metalness_bot100 = words_metalness_df.tail(100)
    words_metalness_top100.to_csv("output_data/words_metalness_top100.csv")
    words_metalness_bot100.to_csv("output_data/words_metalness_bot100.csv")
    plot_word_cloud(metal_word_freq_dist, args.output)
    plot_word_cloud(non_metal_word_freq_dist, "output_pics/non_metal_wordcloud.png")
    plot_word_cloud_Debauchery(df_metal_songs)


