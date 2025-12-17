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
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

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
    
    retour:
        la matrice tf-idf
        l'objet vectorizer
    """

    vectorizer = TfidfVectorizer(stop_words=list(custom_stopwords))
    
    vectorizer.fit(idf_corpus)
    matrix = vectorizer.transform(tf_corpus)
    
    return matrix, vectorizer



def optics_clustering(data, xi=0.05, metric='cosine', min_cluster_size=0.1):
    """
    Clustering des données avec OPTICS.

    paramètres:
        data : les données (ici matrice tf-idf)
        *args : paramètres d'OPTICS
    
    retour:
        les labels des données
    """

    optics = OPTICS(xi=xi, metric=metric, min_cluster_size=min_cluster_size)
    optics.fit(data)
    return optics.labels_



def kmeans_clustering(data, n_clusters=np.arange(2,11), return_scores: bool=True, fig_name="KMeans_scores"):
    """
    Clustering des données avec KMeans.

    paramètres:
        data : les données (ici matrice tf-idf)
        n : liste des nombres de clusters avec lequel on applique KMeans
        return_scores : afficher ou non les sihlouette_scores en fonction du nombre de clusters
        fig_name : nom de la figure à sauvegarder (si return_scores=True)

    retour:
        les labels des données par le meilleur clustering
    """

    kmeans = KMeans()
    labels = []
    scores = []

    for n in n_clusters:
        kmeans.n_clusters = n
        kmeans.fit(data)
        labels.append(kmeans.labels_)
        scores.append(silhouette_score(data, kmeans.labels_))
    
    if return_scores:
        output_path = "output_pics/" + fig_name + ".png"
        plt.plot(n_clusters, scores)
        plt.grid()
        plt.title("Score de silhouette des clusterings KMeans")
        plt.xlabel("nombre de clusters")
        plt.ylabel("score")
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
    
    arg_score = np.argmax(scores)

    return labels[arg_score]



def mapper(data, n_neighbors=5, min_dist=0.2, metric='cosine', random_state=None):
    """
    Effectue une transformation de visualisation des données avec umap.

    paramètres:
        data : les données
        *args : paramètres de UMAP
    
    return:
        les données transformées
    """

    mapper = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        metric=metric,
        random_state=random_state
        )
    
    return mapper.fit_transform(data)



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

def plot(embedding, labels, albums, fig_name):
    """
    Enregistre l'affichage de l'embedding des données en 2D avec les labels du clustering.

    paramètres:
        embedding : données transformées pour visualisation 2D
        labels : les labels des données
        albums : les noms des albums
        fig_name : nom du fichier à enregistrer
    """
    
    plt.figure(figsize=(10,10))
    plt.scatter(embedding[:, 0], embedding[:, 1], c=labels)
    plt.title("Visualisation UMAP des artists en fonction de leur metallitude")
    plt.xlabel("axe 1")
    plt.ylabel("axe 2")
    # Clean album names to remove dollar signs that break matplotlib
    for i, album in enumerate(albums):
        clean_album = str(album).replace('$', '')
        clean_album = clean_album.encode("ascii", "ignore").decode()
        plt.text(embedding[i, 0] + 0.1,
                embedding[i, 1] + 0.3,
                clean_album,
                fontsize=8)

    output_path = "output_pics/" + fig_name + ".png"
    if os.path.exists(output_path):
        os.remove(output_path)
    os.makedirs("output_pics", exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()



if __name__ == "__main__" :

    parser = ArgumentParser(description="parser")
    parser.add_argument("-f", "--figname", default="tf-idf_on_albums", help = "name of the output figure")
    parser.add_argument("-c", "--clustering", default=None, help = "the method of clustering : {'OPTICS', 'Kmeans'}")
    parser.add_argument("-a", "--artists", default=20, help = "the artists of whose to compute the albums")
    args = parser.parse_args()

    # sélection des artistes
    top_100_artists = metal_df["artist"].value_counts().head(100).index.tolist()
    if type(args.artists) == int:
        selected_artists = top_100_artists[:(args.artists+1)]
    else:
        selected_artists = args.artists

    print(f"\nArtists selected : {selected_artists}\n")

    # organisation des données
    metal_album_lyrics = (metal_df.groupby(["artist", "album"], as_index=False).agg(lyrics=("lyrics", lambda x: " ".join(x.dropna().astype(str)))))
    selected_artists_albums = metal_album_lyrics[metal_album_lyrics['artist'].isin(selected_artists)]
    albums = selected_artists_albums["album"].tolist()
    metal_album_lyrics = metal_album_lyrics["lyrics"].tolist()
    selected_artists_albums = selected_artists_albums['lyrics'].tolist()
    
    
    # calcul de la matrice tf-idf
    metal_matrix, vectorizer = tf_idf(selected_artists_albums, metal_album_lyrics)

    # clustering des albums
    labels = None
    if args.clustering is not None:
        if args.clustering == 'OPTICS':
            labels = optics_clustering(metal_matrix)
        elif args.clustering == 'KMeans':
            labels = kmeans_clustering(metal_matrix)
        else:
            raise TypeError("La méthode de clustering n'est pas valide.")
        
        # print the thematical words of each clusters
        print("===== Thematical words of each clusters =====")
        feature_names = np.array(vectorizer.get_feature_names_out())
        for c in np.unique(labels):
            cluster_indices = np.where(labels == c)[0]
            cluster_tfidf = metal_matrix[cluster_indices].mean(axis=0).A1
            top_words = feature_names[cluster_tfidf.argsort()[-10:][::-1]]
            if c == -1:  # bruit
                print(f"Bruit : {', '.join(top_words)}")
            else:
                print(f"Cluster {c} : {', '.join(top_words)}")
        print("\n")

    # visualisation 2D des données
    embedding = mapper(metal_matrix)
    plot(embedding, labels, albums, args.figname)
