#!/usr/bin/python3
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['text.usetex'] = False
import umap
import re
metalness_csv = "output_data/metalness.csv"
from process_wordcloud_metalness import load_music_data_with_lyrics
import nltk
from nltk.corpus import stopwords
# Setup stopwords to match the filtering in tf_idf.py
try:
    base_stopwords = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    base_stopwords = set(stopwords.words('english'))

extra_tokens_to_remove = {'ve', 'dont', 'll', 'nt'}
custom_stopwords = base_stopwords.union(extra_tokens_to_remove)

#load metal dataset
try:
    metal_df = pd.read_csv("cache/lyrics_data.csv", dtype=str)
except FileNotFoundError:
    print("Warning: Metal dataset not found. Creating cache")
    metal_df = load_music_data_with_lyrics("data/dataset.json")


def calculate_album_metalness(lyrics_text, scores_dict):

    if not isinstance(lyrics_text, str):
        return 0.0

    words = re.findall(r'\b\w+\b', lyrics_text.lower())
    filtered_words = [word for word in words if word not in custom_stopwords]

    if not filtered_words:
        return 0.0

    scores = [scores_dict.get(word, 0) for word in filtered_words]

    return sum(scores) / len(filtered_words) if filtered_words else 0.0

def optics_clustering(X):
    from sklearn.cluster import OPTICS
    optics = OPTICS(min_samples = 2, xi=0.05, min_cluster_size=0.1)
    optics.fit(X)
    return optics.labels_


def umap_plot(dataframe):
    # dataframe has to have an "avg_metalness" column
    dataframe = dataframe.sample(n=100, random_state=42)
    X = dataframe[["avg_metalness"]].values
    labels = optics_clustering(X)
    print(np.unique(labels))
    reducer = umap.UMAP(n_neighbors=5, min_dist=0.3, random_state=42)
    X_umap = reducer.fit_transform(X)

    dataframe['umap_1'] = X_umap[:, 0]
    dataframe['umap_2'] = X_umap[:, 1]

    plt.figure(figsize=(8, 5))
    plt.scatter(dataframe['umap_1'], dataframe['umap_2'],
                c=labels, cmap='rainbow', s=100)

    # Clean album names to remove dollar signs that break matplotlib
    for i, album in enumerate(dataframe['album']):
        clean_album = str(album).replace('$', '')
        plt.text(dataframe['umap_1'].iloc[i] + 0.1,
                 dataframe['umap_2'].iloc[i] + 0.3,
                 clean_album,
                 fontsize=3)

    plt.title("Visualisation UMAP des albums selon la metalness")
    output_path = "output_pics/umap_metalness.png"
    if os.path.exists(output_path):
        os.remove(output_path)
    os.makedirs("output_pics", exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    # Load metalness scores into a dictionary for efficient lookup
    metalness_df = pd.read_csv(metalness_csv)
    metalness_scores = pd.Series(metalness_df.Metalness.values, index=metalness_df.Word).to_dict()
    album_lyrics = metal_df.groupby('album')['lyrics'].agg(lambda x : " ".join(x.astype(str))).reset_index()

    album_lyrics['avg_metalness'] = album_lyrics['lyrics'].apply(lambda x: calculate_album_metalness(x, metalness_scores))
    album_lyrics = album_lyrics.sort_values(by='avg_metalness', ascending=False)
    print("--- Album Metalness Scores: ---")
    print(album_lyrics[['album', 'avg_metalness']].head())
    umap_plot(album_lyrics)
