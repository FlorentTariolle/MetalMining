#!/usr/bin/python3

from process_wordcloud_metalness import load_music_data_with_lyrics,process_metal_songs, process_non_metal_songs
import pandas as pd
from argparse import ArgumentParser
import os
import nltk
import numpy as np
from nltk.corpus import stopwords
from sklearn.preprocessing import MinMaxScaler

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
WORD_COLUMN_METAL = "lyrics"
WORD_COLUMN_NON_METAL = "Lyric"
csv_cache_path = "cache/lyrics_data.csv"

# Load non-metal dataset if it exists, otherwise create empty DataFrame
try:
    non_metal_dataset = pd.read_csv("cache/non_metal_lyrics.csv")
except FileNotFoundError:
    print("Warning: Non-metal dataset not found. Creating empty dataset.")
    non_metal_dataset = pd.DataFrame(columns=['Lyric', 'language'])

try:
    base_stopwords = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    base_stopwords = set(stopwords.words('english'))

def process_idf_scores(metal_df, non_metal_df, output = None):
    # Treat each song's lyrics as a document
    metal_documents = metal_df[WORD_COLUMN_METAL].astype(str).tolist()
    non_metal_documents = non_metal_df[WORD_COLUMN_NON_METAL].astype(str).tolist()
    extra_tokens_to_remove = {'ve', 'dont', 'll', 'nt'}
    custom_stopwords = base_stopwords.union(extra_tokens_to_remove)
    # Calculate TF for the metal dataset
    tf_vectorizer = CountVectorizer(stop_words=list(custom_stopwords))
    tf_metal_matrix = tf_vectorizer.fit_transform(metal_documents)
    tf_metal_words = tf_vectorizer.get_feature_names_out()
    total_tf_metal = np.array(tf_metal_matrix.sum(axis=0)).ravel()
    tf_df = pd.DataFrame({'Word': tf_metal_words, 'TF_metal': total_tf_metal})

    # Calculate IDF for the non-metal dataset
    idf_vectorizer = TfidfVectorizer(stop_words='english')
    idf_vectorizer.fit(non_metal_documents)
    idf_non_metal_words = idf_vectorizer.get_feature_names_out()
    idf_scores = idf_vectorizer.idf_
    idf_df = pd.DataFrame({'Word': idf_non_metal_words, 'IDF_non_metal': idf_scores})

    # Merge TF and IDF dataframes
    metalness_df = pd.merge(tf_df, idf_df, on='Word', how='left')

    max_idf = np.log(len(non_metal_documents) + 1) + 1
    metalness_df['IDF_non_metal'].fillna(max_idf, inplace=True)

    # Calculate the custom "Metalness" score
    scaler = MinMaxScaler(feature_range=(0, 1), clip=True)
    metalness_df['Metalness'] = metalness_df['TF_metal'] * metalness_df['IDF_non_metal']
    metalness_df["Metalness"] = scaler.fit_transform(metalness_df[["Metalness"]])
    # Sort by the new metalness score
    metalness_df = metalness_df.sort_values(by='Metalness', ascending=False)

    print("--- Metalness score (TF_metal * IDF_non_metal) ---")
    print(metalness_df.head(20))

    if output:
        if os.path.exists(output):
                os.remove(output)
        os.makedirs("output_data", exist_ok=True)
        metalness_df.to_csv(output, index=False)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", "--filepath", default=None, help = "path to dataset in json format")
    parser.add_argument('-o', "--output", default=None, help="path to output csv metalness ranking")

    args = parser.parse_args()

    if os.path.exists(csv_cache_path) and args.filepath is None:
        print(f"[INFO] Loading cached data from '{csv_cache_path}'...")
        df_songs = pd.read_csv(csv_cache_path)
    else:
        print("[INFO] Cache not found or custom file provided. Loading from JSON...")
        filepath = args.filepath if args.filepath is not None else 'data/dataset.json'
        df_songs = load_music_data_with_lyrics(filepath)
        df_songs.to_csv(csv_cache_path, index=False)
        print(f"[INFO] Data cached to '{csv_cache_path}'")

    metal_df = process_metal_songs(df_songs)
    non_metal_df = process_non_metal_songs(non_metal_dataset)
    process_idf_scores(metal_df, non_metal_df, output=args.output)
