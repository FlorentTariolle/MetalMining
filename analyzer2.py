#!/usr/bin/env python3
"""
Script to analyze the lyrics distribution of the metal music dataset, following the guidance of the second article of the Medium.
"""

import argparse
import json
import os
import re
import string

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from readability import ColemanLiauIndex

DEFAULT_JSON = "data/dataset.json"
SWEAR_PATH = "resources/swear_words_eng.txt"
TOP_BANDS = 1000
STUPID_CL_THRESHOLD = 3
RATIO_RANGE = np.arange(0.00, 0.26, 0.01)


# Charge un fichier texte (1 élément/ligne) et renvoie une liste en minuscules
def load_list(path):
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [ln.strip().lower() for ln in f if ln.strip()]

# Charge le DataFrame de base via analyzer.load_music_data (partie I)
def load_base(json_path):
    import analyzer
    df_songs, _ = analyzer.load_music_data(json_path)
    return df_songs

# Lit le JSON brut et associe les paroles au DataFrame (clé: artist, album, song)
def attach_lyrics(df, json_path):
    with open(json_path, "r", encoding="utf-8") as f:
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
    
    rows = []
    for artist, a in dataset.items():
        for album, al in a["albums"].items():
            for s in al.get("songs", []):
                rows.append({
                    "artist": artist,
                    "album": album,
                    "song": s.get("title", ""),
                    "lyrics": (s.get("lyrics", "") or "").strip()
                })
    df_lyr = pd.DataFrame(rows)
    out = df.merge(df_lyr, on=["artist", "album", "song"], how="left")
    out["release_year"] = pd.to_numeric(out["release_year"], errors="coerce")
    out = out.dropna(subset=["release_year"])
    return out

# Garde uniquement les chansons avec paroles en anglais
def keep_english(df):
    mask = (df["has_lyrics"] == True) & (df["language"] == "English") & df["lyrics"].fillna("").ne("")
    return df.loc[mask].copy()

# Nettoie le texte: minuscules, remplace \n, enlève la ponctuation (remplacée par des espaces)
def _prep_text(text):
    t = (text or "").lower().replace("\\n", " ")
    return t.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))

# Calcule le ratio de gros mots: occurrences exactes / nombre total de tokens
def swear_ratio(text, swear_words):
    t = _prep_text(text)
    toks = [w for w in t.split() if w]
    if not toks:
        return 0.0
    total = 0
    for w in swear_words:
        total += len(list(re.finditer(rf"\b{re.escape(w)}\b", t)))
    return total / len(toks)

# Calcule l'indice Coleman–Liau (entier ≥ 1)
def readability_cl(text):
    t = (text or "").replace("\\n", " ")
    try:
        return max(1, int(ColemanLiauIndex(t).grade_level))
    except Exception:
        return 1

# Trace une courbe simple et l’affiche 
def line_plot_show(df, x, y, xlabel, ylabel, title, figsize=(12, 6)):
    plt.figure(figsize=figsize)
    plt.plot(df[x].values, df[y].values, marker="o")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.show()

# Trace un nuage de points simple et l’affiche 
def scatter_plot_show(df, x, y, xlabel, ylabel, title, figsize=(10, 10)):
    plt.figure(figsize=figsize)
    plt.scatter(df[x].values, df[y].values, s=25, alpha=0.7)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.show()

def run(json_path, swear_path, top_bands, seed):
    # 1) données + paroles + filtre anglais
    swears = load_list(swear_path)
    base = load_base(json_path)
    df = attach_lyrics(base, json_path)
    df = keep_english(df)

    # 2) sous-ensemble groupes populaires
    pop = (df.groupby("artist")["artist"].count()
             .reset_index(name="count")
             .sort_values("count", ascending=False)
             .head(top_bands))
    df_pop = df[df["artist"].isin(pop["artist"])].copy()

    # 3) métriques
    df_pop["swear_word_ratio"] = df_pop["lyrics"].apply(lambda t: swear_ratio(t, swears))
    df_pop["readability"] = df_pop["lyrics"].apply(readability_cl)

    # 4) agrégations artistes + années
    artists = (df_pop.groupby("artist")
               .agg(average_swear_word_ratio=("swear_word_ratio", "mean"),
                    average_readability_index=("readability", "mean"),
                    n_songs=("song", "count"))
               .reset_index())

    yearly = (df_pop.groupby("release_year")
              .agg(average_swear_word_ratio=("swear_word_ratio", "mean"),
                   average_readability_index=("readability", "mean"))
              .reset_index()
              .sort_values("release_year"))

    # 5) affichage figures
    sample_n = min(150, len(artists))
    if sample_n > 0:
        scatter_plot_show(
            artists.sample(n=sample_n, random_state=seed),
            x="average_readability_index",
            y="average_swear_word_ratio",
            xlabel="Coleman–Liau readability score",
            ylabel="Fraction of swear words in lyrics",
            title="Swear words vs Coleman–Liau (artists)",
        )

    line_plot_show(
        yearly, "release_year", "average_swear_word_ratio",
        "Release year", "Average swear words ratio",
        "Evolution of average swear words ratio in metal lyrics",
    )
    line_plot_show(
        yearly, "release_year", "average_readability_index",
        "Release year", "Average Coleman–Liau score",
        "Evolution of average Coleman–Liau score of metal lyrics",
    )

    # 6) courbe “stupid songs” vs ratio de gros mots
    def percent_stupid(th):
        sub = df_pop[df_pop["swear_word_ratio"] >= th]
        if len(sub) == 0:
            return 0.0
        stupid = sub[sub["readability"] <= STUPID_CL_THRESHOLD]
        return round(100 * len(stupid) / len(sub), 2)

    curve = pd.DataFrame({
        "swear_word_ratio": RATIO_RANGE,
        "stupid_songs_perc": [percent_stupid(r) for r in RATIO_RANGE]
    })

    line_plot_show(
        curve, "swear_word_ratio", "stupid_songs_perc",
        "Swear word ratio", 'Percent of "stupid songs"',
        'Proportionality between swear word ratio and percent of "stupid songs"',
    )


def main():
    p = argparse.ArgumentParser(description="analyzer2 — display only (no file saves for plots).")
    p.add_argument("--json", default=DEFAULT_JSON)
    p.add_argument("--swears", default=SWEAR_PATH)
    p.add_argument("--topbands", type=int, default=TOP_BANDS)
    p.add_argument("--seed", type=int, default=50)
    args = p.parse_args()
    run(args.json, args.swears, args.topbands, args.seed)

if __name__ == "__main__":
    main()
