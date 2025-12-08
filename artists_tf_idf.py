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



def tf_idf(tf_corpus, idf_corpus):
    """
    Calcule la matrice tf-idf entre des documents et leur corpus.
    Ici les documents doivent être les lyrics des 100 artists avec le plus de chansons, et le corpus le dataset de lyrics metal complet.

    parametres:
        tf_corpus : documents
        idf_corpus : corpus global
    
    return:
        la matrice tf-idf
        l'objet vectorizer
    """

    vectorizer = TfidfVectorizer(
        stop_words=list(custom_stopwords),
        min_df=5,)
    
    vectorizer.fit(idf_corpus)
    matrix = vectorizer.fit_transform(tf_corpus)
    
    return matrix, vectorizer



def optics_clustering(data):
    """
    """

    optics = OPTICS(xi=0.05, metric='cosine')
    optics.fit(data)
    return optics.labels_



def mapper(data, n_neighbors=5, min_dist=0.2, metric='cosine', random_state=42):
    """
    Effectue une transformation de visualisation des données avec umap.

    paramètre:
        data : les données
        n_neighbors, min_dist, metric, random_state : hyperparamètres de UMAP
    
    return:
        les données transformées
    """

    mapper = umap.UMAP(
        n_neighbors=5,
        min_dist=0.2,
        metric='cosine',
        random_state=42
        )
    
    return mapper.fit_transform(data)



def plot(mapper, labels, artists, fig_name):
    """
    """
    
    plt.figure(figsize=(10,10))
    plt.scatter(mapper[:, 0], mapper[:, 1], c=labels)
    plt.title("Visualisation UMAP des artists en fonction de leur metallitude")
    plt.xlabel("axe 1")
    plt.ylabel("axe 2")
    for idx, artist in enumerate(artists):
        plt.text(mapper[idx, 0] + 0.1, mapper[idx, 1] + 0.05, artist, fontsize=8)

    output_path = "output_pics/" + fig_name + ".png"
    if os.path.exists(output_path):
        os.remove(output_path)
    os.makedirs("output_pics", exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()



if __name__ == "__main__" :

    parser = ArgumentParser(description="parser")
    parser.add_argument("-f", "--figname", default="artist_clustering", help = "name of the output figure")
    args = parser.parse_args()

    # organisation des données
    top_100_artists = metal_df["artist"].value_counts().head(100).index.tolist()
    metal_lyrics = metal_df.groupby('artist')['lyrics'].agg(lambda x : " ".join(x.astype(str))).reset_index()
    top_artists_lyrics = metal_lyrics[metal_lyrics['artist'].isin(top_100_artists)]

    # calcul de la matrice tf-idf
    metallitude_matrix, _ = tf_idf(top_artists_lyrics['lyrics'], metal_lyrics['lyrics'].to_list())

    # clusterising des artistes
    labels = optics_clustering(metallitude_matrix)

    # visualisation 2D des données
    embedding = mapper(metallitude_matrix)
    plot(embedding, labels, top_100_artists, args.figname)
