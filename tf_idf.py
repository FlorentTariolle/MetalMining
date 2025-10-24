#!/usr/bin/python3

from process_wordcloud_metalness import load_music_data_with_lyrics,process_metal_songs, process_non_metal_songs
import pandas as pd
from argparse import ArgumentParser
import os

from sklearn.feature_extraction.text import TfidfVectorizer
WORD_COLUMN_METAL = "lyrics"
WORD_COLUMN_NON_METAL = "Lyric"
csv_cache_path = "cache/lyrics_data.csv"

# Load non-metal dataset if it exists, otherwise create empty DataFrame
try:
    non_metal_dataset = pd.read_csv("cache/non_metal_lyrics.csv")
except FileNotFoundError:
    print("Warning: Non-metal dataset not found. Creating empty dataset.")
    non_metal_dataset = pd.DataFrame(columns=['Lyric', 'language'])

def process_idf_scores(metal_df, non_metal_df, output = None):
    metal_corpus = ' '.join(metal_df[WORD_COLUMN_METAL].astype(str).tolist())
    non_metal_corpus = ' '.join(non_metal_df[WORD_COLUMN_NON_METAL].astype(str).tolist())
    documents = [metal_corpus, non_metal_corpus]
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(documents)
    feature_names = vectorizer.get_feature_names_out()
    print(feature_names)
    metal_idf_scores = X[1].toarray().flatten()
    metalness_df  = pd.DataFrame({"Word" : feature_names,
                                  "Metalness" :  metal_idf_scores})
    metalness_df = metalness_df.sort_values(by='Metalness', ascending=False)
    print("--- Metalness score by word using (TF-IDF) ---")
    print(metalness_df.head(20))
    if output:
        metalness_df.to_csv(output, index=False)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", "--filepath", default='None', help = "path to dataset in json format")
    parser.add_argument('-o', "--output", default=None, help="path to output csv metalness ranking")

    args = parser.parse_args()

    if os.path.exists(csv_cache_path) and args.filepath is None:
        print(f"[INFO] Loading cached data from '{csv_cache_path}'...")
        df_songs = pd.read_csv(csv_cache_path)
    else:
        print("[INFO] Cache not found or custom file provided. Loading from JSON...")
        df_songs = load_music_data_with_lyrics(args.filepath)
        df_songs.to_csv(csv_cache_path, index=False)
        print(f"[INFO] Data cached to '{csv_cache_path}'")

    metal_df = process_metal_songs(df_songs)
    non_metal_df = process_non_metal_songs(non_metal_dataset)
    process_idf_scores(metal_df, non_metal_df, output=args.output)