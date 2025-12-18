"""Metalness metric computation based on word frequency comparison."""

import numpy as np
import pandas as pd
from tqdm import tqdm
from nltk import FreqDist


def compute_metalness(wfd_metal: FreqDist, wfd_non_metal: FreqDist) -> pd.DataFrame:
    """
    Compute metalness scores by comparing word frequencies between metal and non-metal corpora.
    
    Metalness is computed as: 1 / (1 + exp(-log(metal_freq / non_metal_freq)))
    
    Args:
        wfd_metal: Word frequency distribution for metal songs
        wfd_non_metal: Word frequency distribution for non-metal songs
        
    Returns:
        DataFrame with 'words' and 'metalness' columns
    """
    no_metal_wfd = {k: v for k, v in wfd_non_metal.items() if v >= 5}
    metal_wfd = {k: v for k, v in wfd_metal.items() if v >= 5}
    metalness = {}

    for word in tqdm(metal_wfd.keys() & no_metal_wfd.keys(), desc="Computing metalness", unit="word"):
        if len(word) > 2:
            metalness_coeff = np.log((metal_wfd[word]) / (no_metal_wfd[word]))
            metalness[word] = 1 / (1 + np.exp(-metalness_coeff))

    metalness_df = pd.DataFrame({
        'words': list(metalness.keys()),
        'metalness': list(metalness.values())
    })

    return metalness_df


def compute_songs_metalness_from_lyrics(lyrics: str, metal_dict: dict) -> float:
    """
    Compute average metalness score for a song based on its lyrics.
    
    Args:
        lyrics: Song lyrics as a string
        metal_dict: Dictionary mapping words to their metalness scores
        
    Returns:
        Average metalness score for the song, or None if no words found
    """
    if not isinstance(lyrics, str):
        return None

    words = lyrics.lower().split()
    scores = [metal_dict.get(w) for w in words if metal_dict.get(w) is not None]

    if len(scores) == 0:
        return None

    return sum(scores) / len(scores)
