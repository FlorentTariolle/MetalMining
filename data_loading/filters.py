"""Filtering functions for processing music datasets."""

import pandas as pd
from data_loading.dataset_loader import LANGUAGE_MAP


def drop_songs_with_no_lyrics(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Drop all songs without lyrics from the given DataFrame.

    Args:
        dataframe (pd.DataFrame): Input DataFrame containing song data.

    Returns:
        pd.DataFrame: DataFrame with only songs that have lyrics.
    """
    initial_count = len(dataframe)
    dataframe = dataframe[dataframe['has_lyrics']]
    final_count = len(dataframe)
    print(f"Dropped {initial_count - final_count} songs without lyrics.")
    return dataframe


def drop_songs_that_are_not_english(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Drop all songs that are not in English from the given DataFrame.

    Args:
        dataframe (pd.DataFrame): Input DataFrame containing song data.

    Returns:
        pd.DataFrame: DataFrame with only English-language songs.
    """
    initial_count = len(dataframe)
    # Handle both language code ('en') and language name ('English')
    english_mask = (dataframe['language'] == 'English') | (dataframe['language'] == 'en')
    dataframe = dataframe[english_mask]
    final_count = len(dataframe)
    print(f"Dropped {initial_count - final_count} songs that are not in English.")
    return dataframe


def process_metal_songs(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Process metal songs by filtering for English songs with lyrics.
    
    Args:
        dataframe (pd.DataFrame): Input DataFrame containing song data.
        
    Returns:
        pd.DataFrame: Filtered DataFrame with English songs that have lyrics.
    """
    df = dataframe.copy()
    df = drop_songs_with_no_lyrics(df)
    df = drop_songs_that_are_not_english(df)
    return df


def process_non_metal_songs(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Process non-metal songs by filtering for English songs.
    
    Args:
        dataframe (pd.DataFrame): Input DataFrame containing song data.
        
    Returns:
        pd.DataFrame: Filtered DataFrame with English non-metal songs.
    """
    df = dataframe.copy()
    # Handle language code 'en' for non-metal dataset
    df_english = df[df['language'] == 'en']
    print(f"Non-metal songs before filtering: {len(df)}, after filtering for English: {len(df_english)}")
    return df_english
