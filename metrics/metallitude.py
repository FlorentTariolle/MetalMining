"""Metallitude computation using TF-IDF approach (TF on Metal, IDF on Non-Metal)."""

import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from nltk.corpus import stopwords
import nltk

try:
    base_stopwords = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    base_stopwords = set(stopwords.words('english'))

WORD_COLUMN_METAL = "lyrics"
WORD_COLUMN_NON_METAL = "Lyric"


def process_idf_scores(metal_df: pd.DataFrame, non_metal_df: pd.DataFrame, output: str = None) -> pd.DataFrame:
    """
    Calculate metallitude scores using TF-IDF approach.
    
    Metallitude = TF_metal * IDF_non_metal, normalized to [0, 1]
    
    Args:
        metal_df: DataFrame with metal songs (must have 'lyrics' column)
        non_metal_df: DataFrame with non-metal songs (must have 'Lyric' column)
        output: Optional path to save the results CSV
        
    Returns:
        DataFrame with Word, TF_metal, IDF_non_metal, and Metalness columns
    """
    # Treat each song's lyrics as a document
    metal_documents = metal_df[WORD_COLUMN_METAL].astype(str).tolist()
    non_metal_documents = non_metal_df[WORD_COLUMN_NON_METAL].astype(str).tolist()
    extra_tokens_to_remove = {'ve', 'dont', 'll', 'nt'}
    custom_stopwords = base_stopwords.union(extra_tokens_to_remove)
    
    # Calculate TF for the metal dataset
    tf_vectorizer = CountVectorizer(stop_words=list(custom_stopwords))
    tf_metal_matrix = tf_vectorizer.fit_transform(metal_documents)
    tf_metal_words = tf_vectorizer.get_feature_names_out()
    total_tf_metal = np.array(tf_metal_matrix.sum(axis=0)).ravel()
    tf_df = pd.DataFrame({'Word': tf_metal_words, 'TF_metal': total_tf_metal})

    # Calculate IDF for the non-metal dataset
    idf_vectorizer = TfidfVectorizer(stop_words='english')
    idf_vectorizer.fit(non_metal_documents)
    idf_non_metal_words = idf_vectorizer.get_feature_names_out()
    idf_scores = idf_vectorizer.idf_
    idf_df = pd.DataFrame({'Word': idf_non_metal_words, 'IDF_non_metal': idf_scores})

    # Merge TF and IDF dataframes
    metalness_df = pd.merge(tf_df, idf_df, on='Word', how='left')

    max_idf = np.log(len(non_metal_documents) + 1) + 1
    metalness_df['IDF_non_metal'].fillna(max_idf, inplace=True)

    # Calculate the custom "Metalness" score
    scaler = MinMaxScaler(feature_range=(0, 1), clip=True)
    metalness_df['Metalness'] = metalness_df['TF_metal'] * metalness_df['IDF_non_metal']
    metalness_df["Metalness"] = scaler.fit_transform(metalness_df[["Metalness"]])
    # Sort by the new metalness score
    metalness_df = metalness_df.sort_values(by='Metalness', ascending=False)

    print("--- Metalness score (TF_metal * IDF_non_metal) ---")
    print(metalness_df.head(20))

    if output:
        if os.path.exists(output):
            os.remove(output)
        output_dir = os.path.dirname(output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        metalness_df.to_csv(output, index=False)

    return metalness_df
