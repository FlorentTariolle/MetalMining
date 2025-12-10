#!/usr/bin/python3
from process_wordcloud_metalness import load_music_data_with_lyrics
import pandas as pd
from metalness_loader import load_metalness_df

import matplotlib.pyplot as plt
import os
import nltk
from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.data import find
from tqdm import tqdm

try:
    metal_df = pd.read_csv("cache/lyrics_data.csv")
except FileNotFoundError:
    print("Warning: Metal dataset not found. Creating cache")
    metal_df = load_music_data_with_lyrics("data/dataset.json")

try:
    non_metal_df = pd.read_csv("cache/non_metal_lyrics.csv", dtype=str)
except FileNotFoundError:
    print("Warning : Non Metal dataset not found. Please create or load a new one.")
    non_metal_df = pd.DataFrame(columns=["Lyric", "language"])

try:
    hedonometer_df = pd.read_csv("cache/hedonometer.csv")
except FileNotFoundError:
    print("Warning : Hedonometer dataset not found. Please make sure to load it.")
    hedonometer_df = pd.DataFrame(columns=["Word", "Happiness Score", "Word in English"])

words_metalness_df = load_metalness_df()

tqdm.pandas()

nltk.data.path.append(os.path.join(os.getcwd(), "resources"))

def ensure_nltk_resources():
    for resource in ["punkt", "vader_lexicon"]:
        try:
            find(resource)
        except LookupError:
            nltk.download(resource)



def words_happiness(words_metalness_dataset: pd.DataFrame,
                    happiness_dataset: pd.DataFrame) -> pd.DataFrame:
    output = (
        pd.merge(
            words_metalness_dataset,
            happiness_dataset,
            on="Word",
            how="left",
        )
        .sort_values("Happiness Score", ascending=False)
        .drop(columns=["Word in English"])
        .dropna(subset=["Happiness Score"])
        .reset_index(drop=True)
    )
    return output


def measure_lyrics_sentiment(text: str) -> float:
    if not isinstance(text, str):
        return 0.0
    text = text.strip()
    if not text:
        return 0.0

    sentences = tokenize.sent_tokenize(text)
    if not sentences:
        return 0.0

    sid = SentimentIntensityAnalyzer()
    values = [sid.polarity_scores(s)["compound"] for s in sentences]
    return float(sum(values) / len(values))


def add_sentiment_index(df: pd.DataFrame) -> pd.DataFrame:
    if "lyrics" not in df.columns:
        raise ValueError("Missing column 'lyrics'.")

    out = df.copy()
    out["sentiment_index"] = (
        out["lyrics"].fillna("").astype(str).progress_apply(measure_lyrics_sentiment)
    )
    return out


def top_songs_by_sentiment(df: pd.DataFrame, n: int = 5) -> tuple[pd.DataFrame, pd.DataFrame]:
    if "sentiment_index" not in df.columns:
        raise ValueError("Missing column 'sentiment_index'.")

    cols = [c for c in ["artist", "album", "song", "sentiment_index"] if c in df.columns]

    positive = df.sort_values("sentiment_index", ascending=False).head(n)[cols]
    negative = df.sort_values("sentiment_index", ascending=True).head(n)[cols]

    return positive, negative


def aggregate_sentiment_by_artist(df: pd.DataFrame) -> pd.DataFrame:
    if "artist" not in df.columns or "sentiment_index" not in df.columns:
        raise ValueError("Missing required columns 'artist' or 'sentiment_index'.")

    agg = {
        "sentiment": ("sentiment_index", "mean"),
    }

    if "metalness" in df.columns:
        agg["metalness"] = ("metalness", "mean")
    if "readability" in df.columns:
        agg["readability"] = ("readability", "mean")
    if "swear_word_ratio" in df.columns:
        agg["swear_word_ratio"] = ("swear_word_ratio", "mean")

    if "song" in df.columns:
        agg["n_songs"] = ("song", "count")
    else:
        agg["n_songs"] = ("lyrics", "count")

    out = (
        df.groupby("artist")
        .agg(**agg)
        .reset_index()
        .sort_values("sentiment", ascending=False)
        .reset_index(drop=True)
    )
    return out


def aggregate_sentiment_by_album(df: pd.DataFrame) -> pd.DataFrame:
    required = ["album", "artist", "sentiment_index"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column '{col}'.")

    agg = {
        "sentiment": ("sentiment_index", "mean"),
    }

    if "metalness" in df.columns:
        agg["metalness"] = ("metalness", "mean")
    if "readability" in df.columns:
        agg["readability"] = ("readability", "mean")
    if "swear_word_ratio" in df.columns:
        agg["swear_word_ratio"] = ("swear_word_ratio", "mean")
    if "release_year" in df.columns:
        agg["release_year"] = ("release_year", "min")
    if "album_type" in df.columns:
        agg["album_type"] = ("album_type", "min")

    albums = (
        df.groupby("album")
        .agg(**agg, artist=("artist", "first"))
        .reset_index()
        .sort_values("sentiment", ascending=False)
        .reset_index(drop=True)
    )
    return albums


def plot_sentiment_distribution(df: pd.DataFrame, title: str = "Metal songs") -> None:
    if "sentiment_index" not in df.columns:
        return

    plt.figure(figsize=(10, 6))
    df["sentiment_index"].hist(bins=40)
    plt.title(f"Sentiment distribution – {title}")
    plt.xlabel("Sentiment (VADER compound)")
    plt.ylabel("Songs")
    plt.tight_layout()
    plt.show()


def plot_artist_scatter_metalness_sentiment(df: pd.DataFrame) -> None:
    if "metalness" not in df.columns or "sentiment" not in df.columns:
        return

    plt.figure(figsize=(10, 7))
    plt.scatter(df["metalness"], df["sentiment"], alpha=0.7, s=30)
    plt.xlabel("Metalness")
    plt.ylabel("Sentiment (average VADER)")
    plt.title("Artists: metalness vs sentiment")
    plt.tight_layout()
    plt.show()


def build_emotional_arc(df: pd.DataFrame, artist: str) -> pd.DataFrame:
    required = ["artist", "album", "sentiment_index"]
    for col in required:
        if col not in df.columns:
            raise ValueError("Missing required columns.")

    subset = df[df["artist"] == artist]
    if subset.empty:
        raise ValueError(f"No songs for '{artist}'.")

    arc = (
        subset.groupby("album")["sentiment_index"]
        .mean()
        .reset_index()
        .rename(columns={"sentiment_index": "average_sentiment"})
    )

    if "release_year" in subset.columns:
        years = subset.groupby("album")["release_year"].min().reset_index()
        arc = arc.merge(years, on="album", how="left")
        arc = arc.sort_values(["release_year", "album"]).reset_index(drop=True)
    else:
        arc = arc.sort_values("album").reset_index(drop=True)

    return arc


def plot_emotional_arc(arc_df: pd.DataFrame, artist: str) -> None:
    if arc_df.empty:
        return

    plt.figure(figsize=(10, 5))
    x = range(len(arc_df))
    plt.plot(x, arc_df["average_sentiment"], marker="o")
    plt.xticks(x, arc_df["album"], rotation=45, ha="right")
    plt.title(f"Emotional arc – {artist}")
    plt.xlabel("Album")
    plt.ylabel("Average sentiment (VADER)")
    plt.tight_layout()
    plt.show()


def build_sentiment_path(df: pd.DataFrame, artist: str) -> pd.DataFrame:
    required = ["artist", "album", "sentiment_index", "metalness"]
    for col in required:
        if col not in df.columns:
            raise ValueError("Missing required columns for sentiment path.")

    subset = df[df["artist"] == artist]
    if subset.empty:
        raise ValueError(f"No songs for '{artist}'.")

    grouped = (
        subset.groupby("album")
        .agg(
            sentiment=("sentiment_index", "mean"),
            metalness=("metalness", "mean"),
            release_year=("release_year", "min"),
        )
        .reset_index()
    )

    if "release_year" in grouped.columns:
        grouped = grouped.sort_values("release_year").reset_index(drop=True)

    return grouped


def plot_sentiment_path(df_path: pd.DataFrame, artist: str) -> None:
    if df_path.empty:
        return

    plt.figure(figsize=(12, 8))
    x = df_path["metalness"]
    y = df_path["sentiment"]

    plt.plot(x, y, marker="o", linewidth=1.5)

    for _, row in df_path.iterrows():
        plt.text(
            row["metalness"] + 0.001,
            row["sentiment"] + 0.001,
            row["album"],
            fontsize=9,
        )

    plt.xlabel("Metalness (avg per album)")
    plt.ylabel("Sentiment (avg per album)")
    plt.title(f"Sentiment path – {artist}")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    happiness_df = words_happiness(words_metalness_df, hedonometer_df)
    print(happiness_df.head(20))
    print(happiness_df.tail(20))

    ensure_nltk_resources()
    metal_with_sent = add_sentiment_index(metal_df)

    pos, neg = top_songs_by_sentiment(metal_with_sent, n=5)
    print("\nTOP POSITIVE SONGS:\n", pos.to_string(index=False))
    print("\nTOP NEGATIVE SONGS:\n", neg.to_string(index=False))

    artists_sent = aggregate_sentiment_by_artist(metal_with_sent)
    print("\nARTISTS SENTIMENT:\n", artists_sent.head(10).to_string(index=False))

    albums_sent = aggregate_sentiment_by_album(metal_with_sent)
    print("\nALBUMS SENTIMENT:\n", albums_sent.head(10).to_string(index=False))

    plot_sentiment_distribution(metal_with_sent)
    plot_artist_scatter_metalness_sentiment(artists_sent)

    try:
        arc = build_emotional_arc(metal_with_sent, "Opeth")
        plot_emotional_arc(arc, "Opeth")
    except Exception as exc:
        print("Error building emotional arc:", exc)

    try:
        path_df = build_sentiment_path(metal_with_sent, "Opeth")
        plot_sentiment_path(path_df, "Opeth")
    except Exception as exc:
        print("Error building sentiment path:", exc)
