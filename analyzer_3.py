#!/usr/bin/python3
from process_wordcloud_metalness import load_music_data_with_lyrics
import pandas as pd
from metalness_loader import load_metalness_df

try:
    metal_df = pd.read_csv("cache/lyrics_data.csv")
except FileNotFoundError:
    print("Warning: Metal dataset not found. Creating cache")
    metal_df = load_music_data_with_lyrics("data/dataset.json")

try:
    non_metal_df = pd.read_csv("cache/non_metal_lyrics.csv", dtype=str)
except FileNotFoundError:
    print("Warning : Non Metal dataset not found. Please create or load a new one.")

try:
    hedonometer_df = pd.read_csv("cache/hedonometer.csv")
except FileNotFoundError:
    print("Warning : Hedonometer dataset not found. Please make sure to load it.")

words_metalness_df = load_metalness_df()

def words_happiness(words_metalness_dataset : pd.DataFrame, happiness_dataset : pd.DataFrame) -> pd.DataFrame:
    output = (
        pd.merge(
            words_metalness_dataset,
            happiness_dataset,
            on = "Word",
            how = "left"
        )
        .sort_values('Happiness Score', ascending=False)
        .drop(columns = ["Word in English"])
        .dropna(subset = ["Happiness Score"])
        .reset_index(drop=True)
    )
    return output

if __name__ == "__main__":
    print(words_happiness(words_metalness_df, hedonometer_df).head(20))
    print(words_happiness(words_metalness_df, hedonometer_df).tail(20))


