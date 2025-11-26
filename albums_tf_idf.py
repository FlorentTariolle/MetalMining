#!/usr/bin/python3

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import nltk
import umap

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from nltk.corpus import stopwords
from sklearn.cluster import OPTICS

from argparse import ArgumentParser

from process_wordcloud_metalness import load_music_data_with_lyrics


# Ignore the warning on the umap random seed
warn_message = "n_jobs value 1 overridden to 1 by setting random_state. Use no seed for parallelism."
warnings.filterwarnings("ignore", message=warn_message)

# Setup stopwords to match the filtering in tf_idf.py
try:
    base_stopwords = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    base_stopwords = set(stopwords.words('english'))

extra_tokens_to_remove = {'ve', 'dont', 'll', 'nt'}
custom_stopwords = base_stopwords.union(extra_tokens_to_remove)



# load the metal dataset
try:
    metal_df = pd.read_csv("cache/lyrics_data.csv", dtype=str)
except FileNotFoundError:
    print("Warning: Metal dataset not found. Creating cache")
    metal_df = load_music_data_with_lyrics("data/dataset.json")



def album_tfidf_matrix(album_lyrics):

    vectorizer = TfidfVectorizer(
        stop_words=list(custom_stopwords),
        max_features=5000,
        min_df=5,)

    tfidf_matrix = vectorizer.fit_transform(album_lyrics['lyrics'])
    
    return tfidf_matrix, vectorizer



def optics_clustering(X):

    optics = OPTICS(min_samples = 2, xi=0.05, min_cluster_size=0.1)
    optics.fit(X)
    return optics.labels_



def plot_clusters(dataframe, X, vectorizer):

    reducer = umap.UMAP(n_neighbors=20, min_dist=0.1, metric='cosine', random_state=42)
    embedding = reducer.fit_transform(X)

    labels = optics_clustering(embedding)

    # print the thematical words of each clusters
    print("===== Thematical words of each clusters =====")
    feature_names = np.array(vectorizer.get_feature_names_out())
    for c in np.unique(labels):
        cluster_indices = np.where(labels == c)[0]
        cluster_tfidf = X[cluster_indices].mean(axis=0).A1
        top_words = feature_names[cluster_tfidf.argsort()[-10:][::-1]]
        if c == -1:  # bruit
            print(f"Bruit : {', '.join(top_words)}")
        else:
            print(f"Cluster {c} : {', '.join(top_words)}")
    print("\n")

    plt.figure(figsize=(10, 6))
    plt.scatter(embedding[:,0], embedding[:,1], c=labels, cmap='Spectral', s=30)
    
    # Clean album names to remove dollar signs that break matplotlib
    for i, album in enumerate(dataframe['album']):
        clean_album = str(album).replace('$', '')
        clean_album = clean_album.encode("ascii", "ignore").decode()
        plt.text(embedding[i, 0] + 0.1,
                embedding[i, 1] + 0.3,
                clean_album,
                fontsize=8)
    
    plt.title("Visualisation UMAP des albums")
    plt.xlabel("UMAP 1")
    plt.ylabel("UMAP 2")

    plt.legend(labels=labels, title="Clusters", bbox_to_anchor=(1.05, 1), loc='upper left')

    output_path = "output_pics/umap_metalness.png"
    if os.path.exists(output_path):
        os.remove(output_path)
    os.makedirs("output_pics", exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

    # enrgistrement des noms d'albums par cluster dans un csv
    df = dataframe.copy()
    df["cluster"] = labels
    cluster_rows = []
    for c in sorted(df["cluster"].unique()):
        albums = df[df["cluster"] == c]["album"].tolist()
        album_list = "; ".join(albums)  # formatage
        cluster_rows.append({"cluster": c, "albums": album_list})
    out = pd.DataFrame(cluster_rows)
    out.to_csv("output_pics/albums_clusters.csv", index=False)



if __name__ == "__main__" :

    top_100_artists = (metal_df["artist"].value_counts().head(100).index.tolist())
    selected_artists = top_100_artists[:5]
    
    metal_df = metal_df[metal_df['artist'].isin(selected_artists)]
    album_lyrics = metal_df.groupby('album')['lyrics'].agg(lambda x : " ".join(x.astype(str))).reset_index()    
    metalness_matrix, vectorizer = album_tfidf_matrix(album_lyrics)

    print(f"\nArtists selected : {selected_artists}\n")
    plot_clusters(album_lyrics, metalness_matrix, vectorizer)
