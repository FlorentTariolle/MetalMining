#!/usr/bin/python3
import os
import re
from argparse import ArgumentParser
import pandas as pd
from process_wordcloud_metalness import load_music_data_with_lyrics, process_metal_songs
from albums_clustering import calculate_average_metalness
import matplotlib.pyplot as plt
from sklearn.cluster import OPTICS
import umap
import nltk
from nltk.corpus import stopwords
from sklearn.preprocessing import StandardScaler
from analyzer2 import compute_song_metrics, load_list
csv_cache_path = "cache/lyrics_data.csv"
swear_path = "resources/swear_words_eng.txt"

try:
    base_stopwords = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    base_stopwords = set(stopwords.words('english'))

extra_tokens_to_remove = {'ve', 'dont', 'll', 'nt'}
custom_stopwords = base_stopwords.union(extra_tokens_to_remove)

def top_bands_by_album_count(df: pd.DataFrame, top_bands: int):
    top_artists_list = df.groupby('artist')['album'].nunique().nlargest(top_bands).index
    filtered_df = df[df['artist'].isin(top_artists_list)]
    return filtered_df

def calculate_metrics(metal_df: pd.DataFrame, metalness_scores: dict, swears: list) -> pd.DataFrame:
    print("Calculating metrics for individual songs...")
    out_df = metal_df.copy()
    out_df['lyrics'] = out_df['lyrics'].astype(str)
    out_df = compute_song_metrics(out_df, swears)
    out_df['metalness'] = out_df['lyrics'].apply(
        lambda x: calculate_average_metalness(x, metalness_scores)
    )
    return out_df


def calculate_text_metalness(lyrics_text, scores_dict):
    """
    Calculates metalness for a single string of text based on the provided dictionary.
    """
    if not isinstance(lyrics_text, str) or not lyrics_text:
        return 0.0

    # Tokenize and filter
    words = re.findall(r'\b\w+\b', lyrics_text.lower())
    filtered_words = [word for word in words if word not in custom_stopwords]

    if not filtered_words:
        return 0.0

    scores = [scores_dict.get(word, 0) for word in filtered_words]
    return sum(scores) / len(filtered_words)


def perform_clustering_and_viz(artist_df, output_dir):
    """
    Performs scaling, OPTICS clustering, and UMAP visualization.
    """
    scaler = StandardScaler(with_std=True, with_mean=True)
    features = ['metalness', 'readability', 'swear_word_ratio']
    X_scaled = scaler.fit_transform(artist_df[features])

    print("Running OPTICS clustering...")
    optics = OPTICS(min_samples=4, xi=0.05, min_cluster_size=0.05)
    labels = optics.fit_predict(X_scaled)

    artist_df['cluster'] = labels

    # Print stats
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    print(f"OPTICS found {n_clusters} clusters and {n_noise} noise points.")

    print("Running UMAP projection...")
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=42)
    embedding = reducer.fit_transform(X_scaled)

    artist_df['umap_1'] = embedding[:, 0]
    artist_df['umap_2'] = embedding[:, 1]

    plt.figure(figsize=(16, 12))
    noise_data = artist_df[artist_df['cluster'] == -1]
    plt.scatter(noise_data['umap_1'], noise_data['umap_2'],
                c='lightgrey', s=50, label='Noise', alpha=0.5)

    clustered_data = artist_df[artist_df['cluster'] != -1]
    scatter = plt.scatter(clustered_data['umap_1'], clustered_data['umap_2'],
                          c=clustered_data['cluster'], cmap='rainbow', s=120, edgecolors='k')

    texts_to_annotate = artist_df if len(artist_df) < 150 else artist_df.sample(150, random_state=42)

    for artist_name, row in texts_to_annotate.iterrows():
        clean_name = str(artist_name).replace('$', '\\$')
        plt.text(row['umap_1'], row['umap_2'], clean_name, fontsize=8, alpha=0.8)

    plt.title("Artist Clustering (Metalness, Readability, Profanity)", fontsize=16)
    plt.xlabel("UMAP Dimension 1")
    plt.ylabel("UMAP Dimension 2")
    plt.colorbar(scatter, label='OPTICS Cluster ID')
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "artist_clusters_optics.png")
    if os.path.exists(out_path):
        os.remove(out_path)
    plt.savefig(out_path, bbox_inches='tight', dpi=300)
    print(f"Plot saved to {out_path}")
    plt.close()
    plt.close()


if __name__ == "__main__":
    swears = load_list(swear_path)
    parser = ArgumentParser(description="parser")
    parser.add_argument("-f", "--filepath", default=None, help = "path to dataset in json format")
    parser.add_argument('-o', "--output", default=None, help="path to output csv metalness ranking")

    args = parser.parse_args()

    if os.path.exists(csv_cache_path) and args.filepath is None:
        print(f"[INFO] Loading cached data from '{csv_cache_path}'...")
        metal_songs = pd.read_csv(csv_cache_path)
    else:
        print("[INFO] Cache not found or custom file provided. Loading from JSON...")
        filepath = args.filepath if args.filepath is not None else 'data/dataset.json'
        metal_songs = load_music_data_with_lyrics(filepath)
        metal_songs.to_csv(csv_cache_path, index=False)
        print(f"[INFO] Data cached to '{csv_cache_path}'")
    metal_df = process_metal_songs(metal_songs)
    metalness_df = pd.read_csv("output_data/metalness.csv")
    metalness_scores = pd.Series(metalness_df.Metalness.values, index=metalness_df.Word).to_dict()
    top_bands = top_bands_by_album_count(metal_df, top_bands=50)
    top_bands_with_metrics = calculate_metrics(top_bands, metalness_scores, swears)
    top_bands_with_metrics_average = top_bands_with_metrics.groupby('artist')[["metalness", "readability", "swear_word_ratio"]].mean()
    perform_clustering_and_viz(top_bands_with_metrics_average, "output_pics")