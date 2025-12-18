"""Functions for computing metrics on song-level data."""

import pandas as pd
from typing import List
from .swear_words import swear_ratio, load_list
from .readability import readability_cl


def compute_song_metrics(df: pd.DataFrame, swears: List[str]) -> pd.DataFrame:
    """
    Compute swear word ratio and readability for each song.
    
    Args:
        df: DataFrame with 'lyrics' column
        swears: List of swear words to search for
        
    Returns:
        DataFrame with added 'swear_word_ratio' and 'readability' columns
    """
    out = df.copy()
    out["swear_word_ratio"] = out["lyrics"].apply(lambda t: swear_ratio(t, swears))
    out["readability"] = out["lyrics"].apply(readability_cl)
    return out
