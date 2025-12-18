#!/usr/bin/python3
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from argparse import ArgumentParser
import pandas as pd

from metrics.sentiment import words_happiness
from utils.metalness_loader import load_metalness_df
from sklearn.metrics import adjusted_rand_score
from data_loading import load_music_data_with_lyrics, process_metal_songs
from clustering.albums_clustering import calculate_average_metalness
import matplotlib.pyplot as plt
from sklearn.cluster import OPTICS
import umap
import nltk
from nltk.corpus import stopwords
from sklearn.preprocessing import StandardScaler
from metrics import compute_song_metrics, load_list
import pandas as pd

def _get_project_root():
    """Get project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

csv_cache_path = os.path.join(_get_project_root(), "cache", "lyrics_data.csv")
swear_path = os.path.join(_get_project_root(), "resources", "swear_words_eng.txt")

try:
    base_stopwords = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    base_stopwords = set(stopwords.words('english'))

extra_tokens_to_remove = {'ve', 'dont', 'll', 'nt'}
custom_stopwords = base_stopwords.union(extra_tokens_to_remove)

def get_hedonometer_df():
    """Load hedonometer dataset."""
    try:
        return pd.read_csv(os.path.join(_get_project_root(), "cache", "hedonometer.csv"))
    except FileNotFoundError:
        print("File not found. Please load the file and retry")
        return pd.DataFrame(columns=["Word", "Happiness Score", "Word in English"])

def top_bands_by_album_count(df: pd.DataFrame, top_bands: int):
    top_artists_list = df.groupby('artist')['album'].nunique().nlargest(top_bands).index
    filtered_df = df[df['artist'].isin(top_artists_list)]
    return filtered_df

def calculate_metrics(metal_df: pd.DataFrame, metalness_scores: dict, happiness_scores : dict, swears: list) -> pd.DataFrame:
    print("Calculating metrics for individual songs...")
    out_df = metal_df.copy()
    out_df['lyrics'] = out_df['lyrics'].astype(str)
    out_df = compute_song_metrics(out_df, swears)
    out_df['metalness'] = out_df['lyrics'].apply(
        lambda x: calculate_average_text_score(x, metalness_scores)
    )
    out_df['happiness'] = out_df['lyrics'].apply(
        lambda x : calculate_average_text_score(x, happiness_scores)
    )

    return out_df


def calculate_average_text_score(lyrics_text, scores_dict):
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


def cluster_artists(artist_df: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    """
    Scale the provided features, run OPTICS, and compute UMAP coordinates.
    """
    df = artist_df.copy()
    scaler = StandardScaler(with_std=True, with_mean=True)
    X_scaled = scaler.fit_transform(df[features])

    print("Running OPTICS clustering...")
    optics = OPTICS(min_samples=4, xi=0.05, min_cluster_size=0.05)
    labels = optics.fit_predict(X_scaled)
    df["cluster"] = labels

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    print(f"OPTICS found {n_clusters} clusters and {n_noise} noise points.")

    print("Running UMAP projection...")
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=42)
    embedding = reducer.fit_transform(X_scaled)

    df["umap_1"] = embedding[:, 0]
    df["umap_2"] = embedding[:, 1]
    return df


def plot_artist_clusters(
    artist_df: pd.DataFrame,
    output_dir: str,
    filename: str,
    title: str,
    cluster_labels: dict[int, str] | None = None,
) -> None:
    """
    Render the clustered artists using UMAP coordinates and optional annotations.
    """
    plt.figure(figsize=(16, 12))
    noise_data = artist_df[artist_df["cluster"] == -1]
    plt.scatter(
        noise_data["umap_1"],
        noise_data["umap_2"],
        c="lightgrey",
        s=50,
        label="Noise",
        alpha=0.5,
    )

    clustered_data = artist_df[artist_df["cluster"] != -1]
    scatter = plt.scatter(
        clustered_data["umap_1"],
        clustered_data["umap_2"],
        c=clustered_data["cluster"],
        cmap="rainbow",
        s=120,
        edgecolors="k",
    )

    texts_to_annotate = artist_df if len(artist_df) < 150 else artist_df.sample(150, random_state=42)
    for artist_name, row in texts_to_annotate.iterrows():
        clean_name = str(artist_name).replace("$", "\\$")
        plt.text(row["umap_1"], row["umap_2"], clean_name, fontsize=8, alpha=0.8)

    if cluster_labels:
        non_noise_labels = {
            cid: label
            for cid, label in cluster_labels.items()
            if cid != -1 and label
        }
        for cluster_id, label in non_noise_labels.items():
            cluster_points = artist_df[artist_df["cluster"] == cluster_id]
            if cluster_points.empty:
                continue
            centroid = cluster_points[["umap_1", "umap_2"]].mean()
            plt.text(
                centroid["umap_1"],
                centroid["umap_2"],
                label,
                fontsize=12,
                fontweight="bold",
                ha="center",
                va="center",
                bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=2),
            )

    plt.title(title, fontsize=16)
    plt.xlabel("UMAP Dimension 1")
    plt.ylabel("UMAP Dimension 2")
    plt.colorbar(scatter, label="OPTICS Cluster ID")

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, filename)
    if os.path.exists(out_path):
        os.remove(out_path)
    plt.savefig(out_path, bbox_inches="tight", dpi=300)
    print(f"Plot saved to {out_path}")
    plt.close()


def perform_clustering_and_viz_MRSW(artist_df, output_dir, cluster_labels=None):
    features = ["metalness", "readability", "swear_word_ratio"]
    clustered_df = cluster_artists(artist_df, features)
    plot_artist_clusters(
        clustered_df,
        output_dir,
        "artist_clusters_optics.png",
        "Artist Clustering (Metalness, Readability, Profanity)",
        cluster_labels,
    )
    return clustered_df

def perform_clustering_and_viz_MH(artist_df, output_dir, cluster_labels = None):
    features = ["metalness", "happiness"]
    clustered_df = cluster_artists(artist_df, features)
    plot_artist_clusters(
        clustered_df,
        output_dir,
        "artist_clusters_optics_Happiness.png",
        "Artist Clustering (Metalness, Happiness)",
        cluster_labels,
    )
    return clustered_df

def perform_clustering_and_viz_M(artist_df, output_dir, cluster_labels=None):
    clustered_df = cluster_artists(artist_df, ["metalness"])
    plot_artist_clusters(
        clustered_df,
        output_dir,
        "artist_clusters_optics_Metalness.png",
        "Artist Clustering Metalness",
        cluster_labels,
    )
    if cluster_labels:
        label_dict = {
            cluster_id: label
            for cluster_id, label in cluster_labels.items()
            if cluster_id != -1 and label
        }
        for cluster_id, label in label_dict.items():
            cluster_points = artist_df[artist_df['cluster'] == cluster_id]
            if cluster_points.empty:
                continue
            centroid = cluster_points[['umap_1', 'umap_2']].mean()
            plt.text(
                centroid['umap_1'],
                centroid['umap_2'],
                label,
                fontsize=12,
                fontweight='bold',
                ha='center',
                va='center',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=2),
            )
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "artist_clusters_optics_Metalness.png")
    if os.path.exists(out_path):
        os.remove(out_path)
    plt.savefig(out_path, bbox_inches='tight', dpi=300)
    print(f"Plot saved to {out_path}")
    plt.close()
    plt.close()
    return artist_df


def cluster_evaluation(artist_df_1, artist_df_2, features_1 : list[str], features_2 : list[str]):
    cluster_1, cluster_2 = cluster_artists(artist_df_1, features_1), cluster_artists(artist_df_2, features_2)
    return adjusted_rand_score(cluster_1["cluster"], cluster_2["cluster"])

if __name__ == "__main__":
    swears = load_list(swear_path)
    parser = ArgumentParser(description="parser")
    parser.add_argument("-f", "--filepath", default=None, help = "path to dataset in json format")
    parser.add_argument('-o', "--output", default=None, help="path to output csv metalness ranking")
    parser.add_argument('-t', "--top-artists", type=int, default=50, help="top nth artists by album count to cluster")

    args = parser.parse_args()

    if os.path.exists(csv_cache_path) and args.filepath is None:
        print(f"[INFO] Loading cached data from '{csv_cache_path}'...")
        metal_songs = pd.read_csv(csv_cache_path)
    else:
        print("[INFO] Cache not found or custom file provided. Loading from JSON...")
        filepath = args.filepath if args.filepath is not None else os.path.join(_get_project_root(), 'data', 'dataset.json')
        metal_songs = load_music_data_with_lyrics(filepath)
        metal_songs.to_csv(csv_cache_path, index=False)
        print(f"[INFO] Data cached to '{csv_cache_path}'")
    metal_df = process_metal_songs(metal_songs)
    metalness_df = load_metalness_df()
    hedonometer_df = get_hedonometer_df()
    happiness_df = words_happiness(metalness_df, hedonometer_df)
    happiness_df = happiness_df.rename(columns = {"Happiness Score" : "happiness"})
    print(happiness_df.head(20))
    happiness_scores = pd.Series(happiness_df.happiness.values, index=happiness_df.Word).to_dict()
    metalness_scores = pd.Series(metalness_df.Metalness.values, index=metalness_df.Word).to_dict()

    top_bands = top_bands_by_album_count(metal_df, top_bands=args.top_artists)
    top_bands_with_metrics = calculate_metrics(top_bands, metalness_scores,happiness_scores, swears)
    top_bands_with_metrics_average = top_bands_with_metrics.groupby('artist')[["metalness", "readability", "happiness", "swear_word_ratio",]].mean()
    #perform_clustering_and_viz_MRSW(top_bands_with_metrics_average, "output_pics")
    #perform_clustering_and_viz_M(top_bands_with_metrics_average, "output_pics")
    print(f"Adjusted Rand Index  MRSW vs MH : {cluster_evaluation(top_bands_with_metrics_average, top_bands_with_metrics_average, ["metalness", "readability","swear_word_ratio"],["metalness", "happiness"])}")
    #perform_clustering_and_viz_MH(top_bands_with_metrics_average, "output_pics")
    print(f"Adjusted Rand Index  : {cluster_evaluation(top_bands_with_metrics_average, top_bands_with_metrics_average, ["metalness"],["metalness", "happiness"])}")
